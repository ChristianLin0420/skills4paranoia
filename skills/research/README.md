# research

Skills for doing the research itself, as distinct from `work/`, which is about communicating and recording it.

| Skill | What it covers | When |
|---|---|---|
| [`experiment-prereg`](experiment-prereg) | Pin the measurement contract and freeze it | Once you have decided to spend the compute |
| [`vla-code-review`](vla-code-review) | Hunts engineering failures that never raise and only make the numbers worse | Before launch, or when numbers do not reproduce |

Complementary: one covers whether you defined what "right" means, the other whether the code is quietly wrong. Run both before launching.

## experiment-prereg

Four fields, none optional: primary metric and minimum detectable effect, what counts as null, stopping and decision rules, and the evaluation protocol.

The field people skip is "what counts as null". Skipping it does not cost you a document, it costs you **the ability to be wrong** — run first and define success later and there is always some slice that looks like a win.

It carries a table of seed counts against detectable differences, and one statistical error worth naming: **rollouts are not the unit of replication, seeds are**. Most VLA papers report three seeds and claim two or three points of improvement; at σ=4pp, three seeds cannot resolve anything under 9.1.

## vla-code-review

These errors share a shape: training completes, the loss curve looks normal, nothing errors, and the final number comes out a few points low — then gets blamed on the method.

Around 60 checks in eleven categories, covering the interaction between precision and learning rate, which dtypes a card supports, mixed-precision correctness, freezing and parameter groups, seeds and determinism, data and evaluation correctness, RL and VLA-specific traps, training monitoring, reproducibility and performance.

`reference/precedents.md` ties each check to a bug that shipped in a public repo — OpenVLA's evaluation geometry drifting between episodes, OpenVLA-OFT's action-head gradients never synchronising, LeRobot's checkpoint load silently returning an untrained model, openpi's precision gap between JAX and PyTorch. Append new cases as you find them; the list is meant to grow.
