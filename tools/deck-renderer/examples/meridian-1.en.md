---
title: Meridian-1 quarterly review
running: Meridian-1 · Q3
subtitle: Freeze the architecture, move Q4 compute to data
author: Your Name
team: Robotics Learning
date: 2026-09-05
lang: en
theme: slate-blue
typeface: plex
footer: Example deck · all figures are fictional
contact: you@example.com
---

<!-- F0 cover -->

<!-- P1 problem -->
# A manipulation policy has to work on tasks it has never seen, yet the demonstration cost of every new task grows linearly
- Q1 | Sample efficiency: every new task needs thousands of fresh demonstrations | Real demos cost about $40 each — 20 tasks is $1.7M | Simulated data is cheap but carries a sim2real gap | Data demand scales with task count and never amortises
- Q2 | Generalisation: success collapses outside the training distribution | Changing material or lighting breaks it | Long-horizon tasks lose context after the second subgoal | Contact-rich tasks have almost no force signal in the demos
- Q3 | Deployability: inference latency does not fit closed-loop control | Vision encoding eats more than half the budget | p99 jitter is unmeasured, so no safety margin can be derived | Diffusion methods run 23ms/step and cannot hold 30Hz
> Left unsolved, every new task is a data-engineering project started from zero.

<!-- P2 solution -->
# Split learning physics from learning tasks with a shared world model, and let the task head learn only the residual
![Meridian-1: frozen vision encoder, shared world model, lightweight action decoder](figures/arch.png)
- Q1 | The world model is shared across tasks and the decoder learns only a residual; the vision encoder stays frozen with adapters | trainable params 11%, demos to target 4200 → 510
- Q2 | Simulated rollouts mixed 4:1 with material and lighting randomisation; context window spans the full episode | 68% mean over 12 held-out task families
- Q3 | The frozen encoder quantises cleanly and the world model runs a single forward pass at inference | 11ms/step, 28Hz closed loop
~ The three mechanisms are independent and can be ablated one at a time — see the Δ column on page 09.

<!-- P3 results -->
# All three mechanisms hold; long-horizon is the one that did not
## One checkpoint throughout, no per-task finetuning
| Method | Demos to target | Held-out | Long-horizon | Latency | Stability |
| --- | --- | --- | --- | --- | --- |
| Baseline BC | 4200 | 31% | 8% | 7ms | 71% |
| Diffusion baseline | 1750 | 41% | 19% | 23ms | 84% |
| Meridian-1 | *510 | *68% | *34% | *11ms | *92% |
```chart
type: line
data: data/curves.csv
band: std
unit: "%"
xlabel: env steps
note: "success rate on 20 held-in tasks"
```
~ TaskSuite-20 · 3 seeds · ±1σ · A100×8 · rollouts=100/task · "long-horizon" is the >200-step subset.

<!-- E01 section index=01 -->
# Sample efficiency
## Evidence for Q1: curves, cost to target, scaling, ablation

<!-- E18 setup solves=Q1 eyebrow="Protocol" -->
# All three methods share one training and evaluation protocol
- Model | params=1.24B | vision=ViT-L/14 frozen | action head=6-layer | ctx=256
- Data | demos=51k | tasks=20 | sim:real=4:1 | aug=colour+material
- Training | optim=AdamW | lr=3e-4 | bs=256 | steps=200k | warmup=2k
- Eval | rollouts=100/task | seeds=3 | horizon=200 | hw=A100×8
~ Every hyperparameter outside the backbone is identical across the three methods, so the gap is attributable to architecture.

<!-- E11 curves solves=Q1 source="runs/2026-08/curves.csv" -->
# On the same data budget, Meridian-1 converges at 78%
## Shaded region is ±1σ over 3 seeds
```chart
type: line
data: data/curves.csv
band: std
unit: "%"
xlabel: env steps
baseline: {value: 56, label: "Diffusion baseline plateau"}
note: "success rate on 20 held-in tasks · rollouts=100/task"
```
~ TaskSuite-20 · 3 seeds · ±1σ · A100×8 · each point is the success rate over 100 rollouts.

<!-- E17 panels solves=Q1 -->
# Data scaling and horizon decay
```chart
type: line
title: Success vs demonstration count
data: data/scaling.csv
band: std
unit: "%"
xlabel: demos
note: "log-spaced sampling, no early stopping"
```
```chart
type: line
title: Success vs episode length
data: data/horizon.csv
band: std
unit: "%"
xlabel: steps
baseline: {value: 55, label: "Q4 threshold"}
note: "one checkpoint, no per-horizon finetuning"
```
~ Both panels use the same weights (step=200k, seed-averaged). Decay steepens past 200 steps — that is the main Q4 risk.

<!-- E06 chart-full solves=Q1 source="Demonstrations required to reach 60% mean success" -->
# Cost to target drops below a third
```chart
type: bar
labels: [Baseline BC, Diffusion baseline, Meridian-1]
values: [4200, 1750, 510]
highlight: 2
delta: pct
note: "demos required to reach 60% mean success"
```
~ Found by bisection on demo count; each point re-run with 3 seeds, ±8% error.

<!-- E19 ablation solves=Q1 delta=Success best=max source="200k steps, protocol as on page 06" -->
# Ablation: the gain comes from the shared world model, not from a bigger backbone
| Variant | Params | GPU-hours | Success |
| --- | --- | --- | --- |
| Baseline BC | 0.31B | 42 | 31% |
| + larger backbone | 1.24B | 128 | 38% |
| + shared world model | 1.20B | 96 | 64% |
| + 4:1 sim mixing | *1.24B | *104 | *78% |
~ Δ is in percentage points against the first row. GPU-hours are wall-clock on A100×8.

<!-- E14 architecture solves=Q1 -->
# Where the efficiency comes from
![Meridian-1: frozen vision encoder, shared world model, action decoder](figures/arch.png)
The shared world model means the action decoder never relearns physics.
The vision encoder stays frozen and only adapters train, cutting trainable parameters to 11%.
Demonstrations are mixed 4:1 with simulated rollouts to offset scarce real data.
~ Dashed paths exist only during training; at inference the world model runs a single forward pass.

<!-- E01 section index=02 -->
# Generalisation
## Evidence for Q2: task matrix, failure attribution, rollouts

<!-- E12 matrix solves=Q2 source="Each cell is the success rate over 100 rollouts; the rule marks the best method per task" -->
# Held-out task matrix
## Rows are tasks the model never saw during training
```chart
type: matrix
data: data/matrix.csv
unit: "%"
note: "held-out tasks · 100 rollouts each · seed-averaged"
```
~ One checkpoint, no per-task finetuning. Long-horizon tidy is the only category still under 50%.

<!-- E07 chart-side solves=Q2 source="Failure attribution across 12 held-out tasks" -->
# The remaining failures cluster into two causes
Contact-rich insertion still suffers, mainly because force feedback is almost absent from the demonstrations.
Long-horizon failures mostly begin after the second subgoal, where the model loses earlier context.
The rest are perception edge cases, which data augmentation should cover.
```chart
type: bar-h
labels: [Context loss, Force control, Perception edge cases, Other]
values: [41, 28, 19, 12]
unit: "%"
note: "n=384 failed rollouts, hand-labelled by two annotators"
```
~ Inter-annotator agreement κ=0.81; the 7% they disagreed on is filed under Other.

<!-- E03 solves=Q2 -->
# Three confirmed failure modes
## Each has a next step that does not touch the architecture
- Context lost after a subgoal | Extend the context window to 512, roughly +7% training time
- Insufficient force control | Collect 8k force-annotated demos, already scheduled with hardware
- Reflective and transparent objects | Material randomisation in augmentation, no new data needed

<!-- E13 filmstrip solves=Q2 source="Long-horizon tidy, successful rollout, every 40th frame" -->
# One successful long-horizon rollout
![t=0](figures/roll0.png)
![t=40](figures/roll1.png)
![t=80](figures/roll2.png)
![t=120](figures/roll3.png)
![t=160](figures/roll4.png)
~ One of the 34% that succeed. Failures typically release the object after t=80.

<!-- E20 figure solves=Q2 source="On-robot capture, not simulation" -->
# The failures share one moment: the frame where the second subgoal is handed over
![Four failed rollouts overlaid, boxes marking where the object is released](figures/failure_grid.png)
~ Four representative cases drawn from 384 failures. Screen capture from on-robot video — no underlying numbers exist, so it is placed as-is rather than redrawn.

<!-- E02 solves=Q2 -->
# Generalisation is not memorisation: held-out success sits only 14 points below in-distribution
> Same weights throughout, with no per-task finetuning.

<!-- E01 section index=03 -->
# Deployment
## Evidence for Q3: latency breakdown, options, schedule

<!-- E10 solves=Q3 source="Median of 1000 consecutive forward passes, warmup excluded" -->
# Latency breakdown: vision encoding is still the largest block
| Stage | Median | p99 | Share | Headroom |
| --- | --- | --- | --- | --- |
| Vision encoding | 4.2ms | 5.1ms | 38% | high, INT8 |
| World model forward | 3.6ms | 4.4ms | 33% | medium |
| Action decoding | 1.9ms | 2.3ms | 17% | low |
| Transport and safety | 1.3ms | 2.5ms | 12% | low |
| *Total | *11.0ms | *14.3ms | *100% | — |
~ A100 batch=1 · 1000 forward passes · 28Hz closed loop; safety margin taken as 2× p99.

<!-- E10 solves=Q3 source="Estimated against 64 H100s for two months" -->
# Two deployment paths
## Recommend A now, keep B as a Q1 option
| Item | A: freeze and scale data | B: keep searching |
| --- | --- | --- |
| Time to result | *8 weeks | 20+ weeks |
| Compute | *128 GPU-months | 800 GPU-months |
| Long-horizon estimate | *55% | 60%, high variance |
| Fallback if it fails | *data stays useful | branches hard to recover |

<!-- E04 solves=Q3 -->
# What actually separates the two paths
- Freeze and scale data | Ships in 8 weeks, risk concentrated in data quality | Data remains useful in Q1 | Needs the infra quota confirmed by 9/20
- Keep searching | 20+ weeks, risk spread but uncontrolled | Abandoned branches are hard to recover | Competes with the on-robot team for compute

<!-- E09 solves=Q3 -->
# Four Q4 checkpoints
- Mid Oct | Data scaled 3x, long-horizon above 42%
- Early Nov | Force data complete, insertion tasks above 70%
- Late Nov | Eight hours of uninterrupted closed-loop operation
- Mid Dec | Long-horizon above 55%, otherwise reopen architecture

<!-- E08 solves=Q3 by="On-robot integration team, August sync" -->
# Quote
> We are not short of smarter models. We are short of a model whose latency is stable and whose failures are predictable.

<!-- E16 -->
# Thank you
- Full experiment logs and run ids are on the internal wiki
- you@example.com
