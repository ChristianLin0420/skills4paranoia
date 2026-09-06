# VLA / WAM / RL code review checklist

Hunts the engineering-level errors that **do not raise and only make the numbers worse**. Problems with the method are not here — that is your expertise. This covers the class where the method was right and the implementation ate it.

Every item reads: **symptom** → **how to check** → **fix**.

---

## Tier 0 — the pre-launch gate

Ten items to clear before spending two months. Any one of them alone is enough to waste the whole batch.

| # | Check | In one line |
|---|---|---|
| 0.1 | Does this card support the precision you set | bf16 needs SM80+, fp8 needs SM89/90 |
| 0.2 | Are master weights fp32 | Pure bf16 training silently discards small updates |
| 0.3 | Is grad clipping after unscale | Wrong order and the clip threshold means nothing |
| 0.4 | Is the scheduler stepped once per optimizer step | Grad accumulation makes the schedule run N× fast |
| 0.5 | Does the frozen encoder also get `.eval()` | `requires_grad=False` stops neither BN stats nor dropout |
| 0.6 | Are normalisation statistics computed on train only | The most common leak, and it does not raise |
| 0.7 | Are truncation and termination handled separately | RL's most expensive off-by-one |
| 0.8 | Are eval seeds independent of the training step | Otherwise checkpoint comparisons are fake |
| 0.9 | Is a DDP wrapper being bypassed via `.module` | Gradients never all-reduce; multi-GPU becomes N separate models |
| 0.10 | Does a failed checkpoint load raise | Silently returning an untrained model invalidates every measurement |

The last two were added after surveying real repositories — they are not theoretical risks, they shipped in OpenVLA-OFT and LeRobot. See `precedents.md`.

---

## 1. Precision and hardware

**1.1 bf16 on a card that does not support it**
Symptom: it runs but is absurdly slow, or errors on some kernels.
Check: `torch.cuda.get_device_capability()`. Below SM80 there is no native bf16 (V100 is SM70, T4 is SM75). A100=SM80, H100=SM90, RTX 4090=SM89.
Fix: assert compute capability at startup rather than silently degrading in a try/except. If you do degrade, print it on the first line of the log.

**1.2 fp8 has a higher bar**
Symptom: `transformer_engine` imports fine but the fp8 path is never taken.
Check: fp8 needs SM89 (Ada) or SM90 (Hopper); A100 does not have it. Confirm the recipe (E4M3 forward, E5M2 backward) is actually in effect.
Fix: print the kernels actually used, not just the config.

**1.3 The TF32 default moves**
Symptom: the same code gives different results on two machines or two PyTorch versions, differing in the third decimal — which compounds into a point or two.
Check: `torch.backends.cuda.matmul.allow_tf32` and `torch.backends.cudnn.allow_tf32`. Their defaults have changed between PyTorch versions.
Fix: **set them explicitly and record the values in the run config.** Cross-run comparison assumes both match.

**1.4 Which SDPA backend actually ran**
Symptom: you think FlashAttention is in use; it fell back to the math backend, 5–10× slower and hungrier for memory.
Check: the `torch.backends.cuda.sdp_kernel` context, or read the kernel names in a profiler. An unsupported head_dim, an attention mask, or fp32 dtype all cause a fallback.
Fix: assert the expected backend in a smoke test.

**1.5 Tensor core alignment**
Symptom: throughput inexplicably around half of what you expected.
Check: hidden dim, head dim and vocab size divisible by 8 (fp16/bf16). 1000 versus 1024 matters a lot.
Fix: pad up to a multiple of 8 or 64; padding costs far less than falling off the tensor cores.

**1.6 `torch.compile` recompilation storms**
Symptom: the first few hundred steps are strangely slow, or memory spikes periodically.
Check: `TORCH_LOGS=recompiles`. Variable sequence length, changing batch size, or Python objects used as conditions all trigger it.
Fix: fix the shapes or use `dynamic=True`; treat recompile count as a monitored metric.

---

## 2. Precision and learning rate

The least-checked section.

**2.1 Low precision silently discards small updates**
Symptom: loss plateaus, or training simply stops improving late on, while grad norm looks normal.
Mechanism: bf16 has about `2^-8` relative precision (three decimal digits); fp16 about `2^-11`. When `|lr × grad| / |w| < 2^-8`, adding the update leaves the weight unchanged and it is silently discarded. Late in training, weights grow and gradients shrink, so the condition is easy to satisfy.
Check: sample some parameters and compare weights before and after `optimizer.step()`; count the fraction that did not move at all.
Fix: keep fp32 master weights (AMP does this by default; pure bf16 training does not). If you insist on pure bf16, the optimizer needs stochastic rounding or Kahan-compensated summation.

**2.2 Adam's eps underflows at low precision**
Symptom: updates blow up, or infs appear.
Mechanism: fp16's smallest normal is about `6e-5` and smallest subnormal about `6e-8`. The default `eps=1e-8` is zero in fp16 and the denominator loses its guard.
Check: the dtype of the optimizer state.
Fix: keep optimizer state in fp32, or raise eps to `1e-6`. AMP usually keeps fp32 state, but custom or 8-bit optimizers need checking.

**2.3 GradScaler eats the LR warmup**
Symptom: warmup looks normal but nothing actually updates for the first few hundred steps.
Mechanism: fp16 overflows easily early on; GradScaler skips any step where it detects an inf. Skipped steps do not advance the optimizer, but if the scheduler steps anyway, warmup never happens.
Check: log the scaler's skip count and scale value. Above 5% skipped is a problem; a scale falling to 1 means persistent overflow.
Fix: advance the scheduler only when the optimizer actually stepped, and monitor the skip rate.

**2.4 Effective batch size and LR under accumulation**
Symptom: results stop being comparable after changing the accumulation count.
Check: `effective_batch = per_device × grad_accum × world_size`. Did the LR scale with it (linear or square-root)? Is the loss divided by the accumulation steps?
Fix: print the effective batch in the log and align experiments on that, not on the per-device batch.

**2.5 Accumulating gradients in low precision**
Symptom: more accumulation steps, worse results.
Mechanism: summing 32 small gradients in fp16 loses the later ones.
Fix: accumulate into an fp32 buffer.

**2.6 Clip before unscale**
Symptom: clipping appears to work — the logged norm sits exactly at the threshold — but protects nothing.
Mechanism: GradScaler has scaled gradients by `S`, so clipping to 1.0 clips to `1.0/S` in real terms.
Fix: `scaler.unscale_(optimizer)` → `clip_grad_norm_` → `scaler.step(optimizer)`. The order is not negotiable.

**2.7 Weight decay on parameters that should not have it**
Symptom: unstable training, or norm-layer scales being pulled toward zero.
Check: the optimizer's parameter groups. Biases, LayerNorm/RMSNorm weights and biases, and embeddings are usually excluded.
Fix: two parameter groups, decay and no_decay.

---

## 3. Mixed-precision correctness

**3.1 Normalisation not computed in fp32**
Symptom: numerical drift on long sequences or large batches.
Check: whether a custom LayerNorm/RMSNorm kernel upcasts internally. autocast handles native layers; custom kernels do not.
Fix: `.float()` inside the norm, compute, cast back.

**3.2 Softmax and attention logits overflow**
Symptom: occasional NaN under fp16, nothing under bf16.
Mechanism: fp16 tops out at 65504, and attention logits exceed that easily with a large head_dim or a missing scale.
Fix: subtract the max before the exponential (standard, but often missed in custom kernels) and compute the softmax in fp32.

**3.3 Loss computed at low precision**
Symptom: distorted gradients for small loss values.
Fix: do cross-entropy and MSE reductions in fp32. `autocast` handles `F.cross_entropy`; a hand-written one is not handled.

**3.4 Metric aggregation at low precision**
Symptom: an inexplicable ±0.5% jitter in success rates.
Mechanism: summing a hundred 0/1 values in fp16 loses the later ones — fp16 starts skipping integers above 2048.
Fix: do every reduction in fp32 or float64. This one matters especially, because it contaminates the number you are going to report.

---

## 4. Freezing, parameter groups, adapters

**4.1 A frozen encoder without `.eval()`**
Symptom: it is frozen but results still shift, or the train/eval gap is unusually large.
Mechanism: `requires_grad=False` blocks gradients only. It does not stop **BatchNorm updating its running stats**, and it does not stop **dropout**. A ResNet encoder is especially exposed.
Check: `model.vision_encoder.training` should be False, and BN `running_mean` should be identical before and after training.
Fix: `requires_grad=False` plus `.eval()`, and reapply each epoch — `model.train()` reopens the whole tree.

**4.2 Adapter or LoRA parameters not in the optimizer**
Symptom: LoRA training finishes and the weights are identical to their initialisation.
Mechanism: the optimizer was built before the adapters were injected, so the parameter group is empty.
Check: does `sum(p.numel() for g in opt.param_groups for p in g['params'])` match the trainable count you expect?
Fix: inject adapters before building the optimizer, and print the trainable count and its share at startup.

**4.3 Trainable parameter count not logged**
Fix: print `trainable / total` on the first line of every run. It is the cheapest guard there is, and a surprising number of bugs show up in that one line.

**4.4 A DDP wrapper bypassed via `.module`**
Symptom: no error. Multi-GPU and single-GPU loss curves look nearly identical, but multi-GPU underperforms, and the more devices the wider the gap.
Mechanism: the module is wrapped in `DistributedDataParallel` but the code calls `head.module.predict(...)`. Bypassing `DDP.forward()` leaves the reducer unregistered, so that module's gradients never all-reduce and each rank updates from its local batch alone.
Check: after a few steps, compare hashes of that module's parameters across two ranks. With synchronisation working they must match.
Fix: call the wrapper itself and move the logic into `forward()`.

**4.5 No verification after merging LoRA**
Symptom: success collapses toward zero after merging, with no error during the merge.
Check: compare outputs on the same batch before and after merging, and take the maximum absolute difference; run a small eval after merging before publishing.
Fix: assert in CI that the post-merge eval score is within 1% of pre-merge.

---

## 5. Seeds and determinism

**5.1 Seeding does not cover every source**
Cover: `random`, `numpy`, `torch`, `torch.cuda` (all devices), **dataloader workers (`worker_init_fn` plus `generator`)**, **the environment (each env instance seeded)**, the augmentation pipeline, and replay buffer sampling.
Symptom: the same seed gives different results twice, or different seeds give identical results — the latter is worse, and means something is hard-coded.

**5.2 The DDP seeding strategy**
Fix: **the same seed for model init** (otherwise ranks start from different points) and **different seeds for data sampling** (otherwise every rank sees the same data). Getting either backwards breaks it.

**5.3 `persistent_workers=True` keeps state**
Symptom: augmentation randomness behaves differently from the second epoch onward.
Fix: know that worker RNG state persists, and decide whether that is what you want.

**5.4 Eval seeds tied to the training step**
Symptom: scores from different checkpoints are not comparable, because they were evaluated on different initial states.
Fix: a fixed seed set (e.g. `range(100)`), independent of the training step. This is a precondition for comparing checkpoints at all.

**5.5 The cost of `use_deterministic_algorithms`**
Note: some kernels then error or slow down sharply, and `cudnn.benchmark` has to be off. Whether to enable it is a trade-off, but **decide explicitly and record it** — do not have some runs with it and some without.

---

## 6. Data and evaluation correctness

**6.1 Normalisation statistics leak**
Symptom: held-out scores inexplicably high.
Check: which split the action and proprioception mean/std were computed on.
Fix: train split only, saved to a file, read by both training and eval.

**6.2 Held-out is not actually held out**
VLA-specific: the same object mesh, scene, or demonstrator appears in both train and "held-out". A different task name does not mean a different distribution.
Check: intersect asset ids, scene ids and demonstrator ids.
Fix: cut the split **at the layer that generates the data**, not on task names.

**6.3 Train and eval preprocessing diverge**
Check: resize interpolation mode (bilinear vs bicubic), crop strategy (random vs centre), normalisation constants, colour space (RGB vs BGR), value range (0-1 vs 0-255).
Fix: one preprocessing function; training only adds augmentation in front of it, never a second path.

**6.4 Action denormalisation does not match**
Symptom: fine in sim, wrong action magnitude on hardware.
Check: whether inference denormalises with the same statistics.
Fix: store the statistics with the checkpoint, not in a separate config file.

**6.5 Padded steps not masked out**
Symptom: tasks with many short episodes behave oddly.
Check: is the loss multiplied by a valid mask, and is the denominator the valid step count rather than the total?

**6.6 How the metric is aggregated**
`mean over episodes` / `mean over steps` / `mean over tasks` differ substantially with unbalanced task counts.
Fix: state which one in the log, keep it consistent across methods, and say it in the report.

**6.7 The success criterion implemented twice**
Symptom: training-time eval scores do not line up with the final eval.
Fix: implement it once and import the same function on both sides.

**6.8 One env shared across the whole eval suite**
Symptom: the same checkpoint scores differently on two runs; later episodes are less stable.
Mechanism: `env.seed()` is called once at construction, so the RNG stream advances across episodes. `reset()` samples scene placement from it into the simulator's body positions, while the function restoring the initial state typically restores only `qpos`/`qvel`, not geometry.
Check: diff the simulator's body positions between consecutive episodes. It should be zero.
Fix: reseed inside the episode loop, or rebuild the env per episode.

**6.9 Statistics computed over non-numeric fields**
Symptom: `Cast string to float is not supported` when computing dataset statistics, or worse, fields being normalised that should not be.
Fix: an explicit allowlist of fields to compute statistics over; do not recurse over the whole sample dict.

---

## 7. RL-specific

**7.1 Truncation versus termination**
The most expensive one. A `truncated` from a time limit **must bootstrap** (`V(s')` counts); a real `terminated` **must not**. The newer gym API separates them; older code often treats both as `done`.
Symptom: value systematically underestimated on long-horizon tasks, and the policy turns myopic.
Check: the lines computing the target, and where `done` came from.

**7.2 `next_value` at GAE boundaries**
Check: whether `next_value` at an episode boundary is wrongly set to zero or taken from the next trajectory.

**7.3 Reward and observation statistics updated during eval**
Symptom: eval scores change depending on how many times you evaluate.
Fix: freeze running statistics during eval.

**7.4 Does the replay buffer store pre- or post-normalisation**
Symptom: once the statistics drift, old data means something different.
Fix: store raw values and normalise on read, or freeze the statistics.

**7.5 The scope of advantage normalisation**
Per-minibatch normalisation makes the effective LR fluctuate with batch composition; per-batch is steadier. Pick one explicitly and record it.

**7.6 The unit of the target-network update interval**
Every N env steps, or every N gradient updates? Changing the update-to-data ratio decouples them.

---

## 8. VLA / WAM-specific

**8.1 Action chunk not aligned to the control frequency**
Symptom: jitter or a one-step lag on hardware.
Check: the relationship between chunk size, steps executed before re-inference, and the control loop rate. The usual bug is an off-by-one: predicting `t..t+H` but executing from `t+1`.

**8.2 Frame-stacking order**
Symptom: fine in sim, bad on hardware, or the reverse.
Check: whether training uses `[t-3, t-2, t-1, t]` or `[t, t-1, t-2, t-3]`, and whether inference matches. This never raises; the model just learns a reversed world.

**8.3 Language token padding side**
A causal decoder must use **left padding** at inference; training commonly uses right padding. A mismatch misaligns the positional encoding.
Check: `tokenizer.padding_side` on both paths.

**8.4 The teacher-forcing to autoregressive gap in the world model**
Symptom: one-step prediction is accurate, rollouts collapse after a few steps.
Check: during training the latent comes from encoding a ground-truth observation; at inference it comes from the model's own prediction. This is exposure bias.
Fix: mix in scheduled sampling or a multi-step rollout loss during training, and **record how many rollout steps training used** — it is the hyperparameter most correlated with inference performance.

**8.5 Rotation representation and normalisation**
Quaternion outputs left unnormalised, or a discontinuous representation (Euler, the double cover of unit quaternions).
Fix: use a 6D continuous representation, normalise every step; at low precision the normalisation error compounds along a rollout.

**8.6 Action units and precision**
Symptom: small-magnitude actions get quantised away in fp16.
Fix: normalise actions to `[-1, 1]` before the head rather than having the network emit metres or radians.

**8.7 Camera intrinsics, extrinsics and image geometry**
Are intrinsics, resolution, crop and distortion correction identical between sim and hardware? This is the part of the sim2real gap most often blamed on domain gap when it is a bug.

**8.8 Proprioception normalised separately from images**
Their scales differ by orders of magnitude; shared statistics make one of them disappear.

**8.9 How the latency number was measured**
Symptom: the report says 11ms, the closed loop runs at 15Hz.
Check: is that the median at batch=1 warm, or end-to-end including transport, preprocessing and safety checks? Was p99 measured?
Fix: report end-to-end and p99, and say how it was measured. The median lies.

---

## 9. Training stability and monitoring

**9.1 Is the logged grad norm before or after clipping**
Logging only the post-clip value makes it permanently equal to the threshold and tells you nothing.
Fix: log both. Spikes in the pre-clip value are the warning sign of divergence.

**9.2 NaN without fail-fast**
Symptom: you discover at the end that the second half was NaN.
Fix: abort on a non-finite loss and dump the batch and RNG state.

**9.3 The unit the LR schedule advances in**
Symptom: LR reaches zero early.
Check: is `scheduler.step()` inside or outside the accumulation loop, and is the scheduler per-step or per-epoch?

**9.4 EMA weights and evaluation consistency**
Comparing two methods where one uses EMA and the other does not invalidates the comparison.
Fix: record explicitly which weights the eval used.

**9.5 Is the dataloader starving the GPU**
Check: the GPU utilisation trace over time, not the average. An average of 85% can be alternating full and empty.
Fix: read the profiler timeline, or measure dataloader wait time.

---

## 10. Checkpointing and reproducibility

**10.1 An incomplete checkpoint**
Store: model, optimizer, scheduler, **GradScaler**, RNG states including CUDA, global step, and the **full config**.
Symptom: loss jumps on resume and then follows a different trajectory. Omitting the scaler is the most common cause.

**10.2 Best or last checkpoint for eval**
Either is defensible, but be consistent and say which in the report. If using best, make sure the metric selecting it is not the one you finally report — otherwise you selected the model on the test set.

**10.3 Config hash and commit not bound to results**
Fix: write the commit sha and config hash into the first line of every eval CSV. Without it, every cross-run comparison is a gamble.

**10.4 "The same setting" is not the same**
Fix: provide a config diff tool that compares two runs' *effective* settings — environment variables, TF32 flags, PyTorch version, GPU model — rather than comparing config files.

**10.5 A failed checkpoint load silently returns an untrained model**
Symptom: the call appears to succeed, nothing raises, a normal policy object comes back, and the only clue is a warning scrolled far up the log.
Why it is fatal: any validation that compares the loaded model against itself passes, because both sides are the same untrained model — the numbers agree perfectly and mean nothing.
Check: assert `missing_keys` and `unexpected_keys` are both empty after loading, or compare a weight hash against the checkpoint file.
Fix: always raise on a failed load. To tolerate missing keys, list the permitted names explicitly.

---

## 11. Performance traps

- `.item()`, `.cpu()` or `print(tensor)` inside the training loop force a synchronisation stall
- `pin_memory=True` with `non_blocking=False` has no effect
- Logging to wandb every step costs 5–10%
- Variable-length sequences fragment memory (consider bucketing or `expandable_segments`)
- Activation checkpointing and dropout: the RNG must align on recompute, or the forward and recomputed dropout masks differ and the gradients are wrong (PyTorch's `checkpoint` handles this; hand-rolled versions often do not)
- Multi-GPU falling back to PCIe rather than NVLink: confirm with `nvidia-smi topo -m`

---

## The report format

Every item ends in one of three states, never a fourth:

```
[PASS]   2.6 clip after unscale            train.py:214
[FOUND]  4.1 frozen encoder has no .eval() model.py:88
         BN running stats still update during training
[N/A]    7.1 truncation vs termination     this codebase is not RL
```

Anything uncertain is FOUND with a line number, for a human to judge. **Do not mark something PASS because it looks right** — the value of this checklist is that it catches errors which look correct.
