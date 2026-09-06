# Precedents

Every check maps to a bug that actually shipped in a real repository. Two purposes: it gives findings weight — "this might be a problem" and "openvla-oft#160 is exactly this" are not the same sentence — and it lets the checklist keep growing.

**Append new cases as you find them.** Format: check number → repo#issue → one line on how it broke. Links must be to public issues; no internal links.

---

## Precision and learning rate

**2.1 Pure low-precision training with no fp32 master weights**
[Physical-Intelligence/openpi#989](https://github.com/Physical-Intelligence/openpi/issues/989) — the same data and the same evaluation protocol finetuning `pi0.5_base`: 82.6 in JAX, 71.9 in PyTorch. The README states JAX uses mixed precision while PyTorch supports only full bf16 or full fp32, and that full bf16 gives higher losses.

**9.1 No gradient clipping**
[openvla/openvla#333](https://github.com/openvla/openvla/issues/333) — LoRA finetuning on LIBERO-Spatial: at step 6000 loss jumps from 2.2 to 5.2, action accuracy collapses toward zero and never recovers, final success 0/50. The reporter points at a missing `clip_grad_norm_` in `finetune.py`.

## Hardware and kernels

**1.4 Silent SDPA fallback**
[openvla/openvla#333](https://github.com/openvla/openvla/issues/333) — the same report surfaces something else: **the authors' own checkpoint** scored 74% on an ARM64 GH200 against 84.7% in the paper. The difference is that the prebuilt flash-attn wheel is x86 only and did not install in the container. Ten points from an attention backend being swapped out, with no error message.

**1.1 Precision versus compute capability**
[unslothai/unsloth#4082](https://github.com/unslothai/unsloth/issues/4082) — a V100 (SM70) cannot do full finetuning of a bf16 model. Easiest to hit when moving a config between machines.

## Distribution and parameters

**4.4 DDP bypassed via `.module`**
[moojink/openvla-oft#160](https://github.com/moojink/openvla-oft/issues/160) — the action head is wrapped in DDP but `finetune.py` calls `action_head.module.predict_action(...)`. Bypassing `DDP.forward()` leaves the reducer unregistered, the action head's gradients never all-reduce, and each rank updates its own head from its local batch.

**4.5 Collapse after merging LoRA**
[moojink/openvla-oft#151](https://github.com/moojink/openvla-oft/issues/151) — the official checkpoint scores 93.2%; re-merging with the repo's own `merge_lora_weights_and_save.py` drops success to zero.

## Evaluation correctness

**6.8 One env reused across episodes**
[openvla/openvla#342](https://github.com/openvla/openvla/issues/342) — `run_libero_eval.py` builds one env per task and calls `env.seed()` once. `env.reset()` samples fixture placement from the already-advanced RNG stream into `sim.model.body_pos`, while `set_init_state()` restores only `qpos`/`qvel`. On `libero_10` task 2 the stove moves 3.0mm between episodes. Adding `env.seed(cfg.seed)` inside the episode loop removes the effect entirely.

**6.7 Success criterion too loose (false positives)**
[simpler-env/SimplerEnv#129](https://github.com/simpler-env/SimplerEnv/issues/129) — WidowX tasks report success while the object is merely near the target, the robot has not released, and sometimes while the object is about to fall.
[Lifelong-Robot-Learning/LIBERO#149](https://github.com/Lifelong-Robot-Learning/LIBERO/issues/149) — LIBERO-10 Task 6 can succeed before the pudding contacts the table.

**6.7 Success criterion too strict (false negatives)**
[Lifelong-Robot-Learning/LIBERO#145](https://github.com/Lifelong-Robot-Learning/LIBERO/issues/145) — `SiteObject.in_box()` ignores site orientation. When a container rotates during a rollout, an object whose centre is visually inside is classified as outside.

**6.3 Preprocessing contradicts the checkpoint's own config**
[huggingface/lerobot#4548](https://github.com/huggingface/lerobot/issues/4548) — the documented `rename_map` contradicts the preprocessor embedded in the checkpoint, and the evaluation instructions are themselves out of distribution, so the model is systematically under-evaluated.

**6.9 Statistics computed over non-numeric fields**
[octo-models/octo#163](https://github.com/octo-models/octo/issues/163) — a custom RLDS dataset with a `language_instruction` string field breaks dataset statistics computation outright (`Cast string to float is not supported`).

**6.1 Normalisation statistics not bound to the checkpoint**
[moojink/openvla-oft#156](https://github.com/moojink/openvla-oft/issues/156) — a question about how unnorm stats couple to the finetuned checkpoint.
[Physical-Intelligence/openpi#1025](https://github.com/Physical-Intelligence/openpi/issues/1025) — a direct request for a read-only normalisation compatibility report, which says how often this is hit.

## Loading and reproducibility

**10.5 A failed load silently returns an untrained model**
[huggingface/lerobot#4577](https://github.com/huggingface/lerobot/issues/4577) — `PI0Policy.from_pretrained` prints a warning and returns the model anyway when it cannot apply a checkpoint, and `strict=True` does not stop it. The reporter was verifying that an exported model matched the original; both were the same untrained model, the numbers agreed perfectly, and a whole batch of measurements was worthless before they noticed.

**10.3 Scores that do not reproduce**
[NVlabs/vla0#29](https://github.com/NVlabs/vla0/issues/29) — the paper reports 94.7 on LIBERO, reproduction gives about 92.5; the authors got 92.2 after retraining and re-evaluating.
[moojink/openvla-oft#150](https://github.com/moojink/openvla-oft/issues/150) — LIBERO-Spatial success below the published figure.

**The quality of the data itself**
[Lifelong-Robot-Learning/LIBERO#148](https://github.com/Lifelong-Robot-Learning/LIBERO/issues/148) — a data-quality audit of LIBERO in LeRobot format: 920 readable, 773 missing (a loader bug), with action and tracking anomalies unresolved. Every conclusion built on that data is affected.

## Is generalisation memorisation

**LIBERO-PRO** — models scoring 90%+ on LIBERO collapse toward zero under in-simulator perturbation of object placement, paraphrased instructions, initial state or environment. The researchers attribute it to rote memorisation of action sequences and layouts.

This does not map to a single check, but it governs how you read a held-out number: **if your held-out only changes task names and not the distribution, that number measures memory rather than generalisation** (see `checklist.md` 6.2).

---

## Using these in a report

Add a "precedent" line at the bottom of each finding, linking to the matching issue here. Findings with no matching case get no line — **do not attach a loosely related link to look grounded**.

Criteria for adding a case: **public, verifiable, and a silent failure.** Installation errors, version conflicts and CUDA OOM are out — they announce themselves and need no review to catch.
