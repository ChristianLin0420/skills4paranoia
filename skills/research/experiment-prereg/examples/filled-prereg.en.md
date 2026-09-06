# Pre-registration — can a shared world model hold success on half the demonstrations

A completed example. Figures are fictional; the reasoning is not.

```
Status     frozen (primary metric and null definition fixed)
Frozen on  2026-09-08
Commit     4f2ac91
Budget     H100 × 64 × 14 days = 21,504 GPU-hours
```

## 1. The yes/no question

Can a shared world model hold the same held-out success rate when the demonstration set is halved, from 51k to 25k?

> Answerable no: if success drops past the threshold after halving, the answer is that it cannot.

## 2. Baseline and budget matching

| Arm | Setting | Data | Compute | Params | HP search trials |
|---|---|---|---|---|---|
| Control A | Shared world model, full data | 51k demos | 200k steps | 1.20B | 12 |
| Control B | No world model, half data | 25k demos | 200k steps | 1.24B | 12 |
| Treatment | Shared world model, half data | 25k demos | 200k steps | 1.20B | 12 |

Dimension let go: parameters differ by 0.04B (3%), because the world model and its replacement module cannot be sized identically. All three arms get 12 randomly sampled hyperparameter trials over the same search space.

> Why two controls: against A alone you cannot tell whether the drop came from halving the data or from having no world model.

## 3. Primary metric and minimum detectable effect

```
Primary metric      mean success over 12 held-out tasks, under perturbation
Unit of replication seed (training run). Rollouts are not the unit.
Existing σ          4.1pp (from runs/2026-08, 6 seeds at the same setting)
Difference sought   5pp (below that it does not change the Q4 resource decision)
Seeds needed        10 per arm
Seeds affordable    10 per arm, agreed in advance, all reported
Rollouts per seed   100 per task
Actually detectable 5.1pp
```

Aggregation: each seed's mean over its 12 tasks first → then mean and standard deviation across the 10 seed means. `n = 10`.

> The arithmetic: `2.80 × 4.1 × √(2/10) = 5.1pp`. Seeking 5pp sits right at the edge of what this can resolve, so 10 seeds is the floor, not headroom.
>
> Had the budget only allowed 3 seeds, this field would read "actually detectable 9.4pp; this experiment cannot detect an effect below 9pp" — rather than running anyway and calling the trend positive.

Exclusion rule (defined in advance, identical for all three arms): a run with NaN loss that cannot resume from its last checkpoint is excluded and a fresh seed is run in its place.

## 4. What counts as null

The treatment differs from control A on the primary metric by **more than 5pp** (i.e. halving costs too much), or the lower bound of the 95% interval falls below −5pp.

> Note the direction: this is a non-inferiority question, not a superiority one. We are trying to show it did not drop much, so null is that it dropped too much. Writing this field as "null if the treatment is not better than the control" would invert the whole logic of the experiment.

Secondary metrics: long-horizon subset success, per-step inference latency, training wall-clock. **Stated in advance as unable to overturn the primary** — a null on the primary cannot be rescued by reaching for one of these.

## 5. Stopping and decision rules

```
Stop when       200k steps, or held-in success flat for 20k steps
Difference < 2pp   → halving works; move the saved compute to long-horizon tasks in Q4
Difference 2–5pp   → workable but costly; run one more arm at 35k before deciding
Difference > 5pp (null) → halving does not work; keep full data and revisit acquisition cost
```

Three different next steps, so the experiment carries information.

## 6. Evaluation protocol

```
Held-out level      object instance + scene (asset and scene ids disjoint,
                    verified with scripts/check_split.py)
Success criterion   object centre in target box, 10 consecutive frames, gripper released,
                    invariant to container rotation
Criterion lives at  envs/criteria.py:success(), shared by training-time and final eval
Eval seeds          range(100), fixed, independent of training step, reseeded each episode
Rollouts            100 per task × 12 tasks × 10 seeds
Perturbation        placement ±3cm, 3 instruction rewrites, 3 initial poses, 2 lightings
Headline number     mean success under perturbation; unperturbed reported as an upper bound
```

## 7. Execution environment

```
Node assignment  three arms interleaved across 8 nodes; every arm spans all of them
Time span        all three concurrent, within one cluster scheduling window
Actual record    runs/2026-09/manifest.csv: run id → node → start/end → driver version
```

## 8. The most likely way this is wasted

1. If the half-size sample is not stratified, the task distribution shifts and we measure distribution shift rather than data volume
2. σ was estimated from full-data runs; the half-data σ may be larger, making 10 seeds insufficient
3. If the perturbation implementation differs between arms, the headline number is not comparable

---

## After the run

```
Result           treatment 68.2% ± 3.9, control A 71.0% ± 4.3,
                 difference 2.8pp (95% CI −0.9 to 6.5)
Which band       the 2–5pp middle band
Action taken     per section 5: run one more arm at 35k demos. Consistent with the prior rule.
Waste cause      item 2 half landed — the half-data σ was 3.9 rather than 4.1, no worse,
                 so 10 seeds sufficed
Protocol changes none
```

> The CI's upper bound of 6.5 crosses the 5pp null threshold, so strictly "it did not drop much" **has not been shown** — it has merely not been refuted. This is exactly what defining null in advance buys: without section 4, 2.8pp would very easily have been written up as "essentially no loss".
