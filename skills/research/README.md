# research

Skills for doing the research itself, as distinct from `work/`, which is about communicating and recording it.

| Skill | What it covers | When |
|---|---|---|
| [`experiment-prereg`](experiment-prereg) | Pin the measurement contract and freeze it | Once you have decided to spend the compute |
| [`vla-code-review`](vla-code-review) | Hunts engineering failures that never raise and only make the numbers worse | Before launch, or when numbers do not reproduce |
| [`baseline-repro`](baseline-repro) | Bisects a gap against a published number, and ledgers every axis on which the two setups differ | When your number lands short of someone else's |

The first two are complementary before a run: one covers whether you defined what "right" means, the other whether the code is quietly wrong. The third is for afterwards, when the number disagrees with a paper.

## experiment-prereg

Four fields, none optional: primary metric and minimum detectable effect, what counts as null, stopping and decision rules, and the evaluation protocol.

The field people skip is "what counts as null". Skipping it does not cost you a document, it costs you **the ability to be wrong** — run first and define success later and there is always some slice that looks like a win.

It carries a table of seed counts against detectable differences, and one statistical error worth naming: **rollouts are not the unit of replication, seeds are**. Most VLA papers report three seeds and claim two or three points of improvement; at σ=4pp, three seeds cannot resolve anything under 9.1.

## baseline-repro

They report 63.2. You get 51.4. This decides what that means — and the first thing it does is refuse to let you call it a reproduction failure.

Three claims get written the same way and need wildly different evidence: **you are measuring something else** (most of the time), **their setup has an advantage you do not** (often), and **their number is wrong** (rare). Only the third is a claim about the paper. Most public reproduction failures are the first, written as the third.

### Bisect before you enumerate

Two artifacts, two harnesses, four cells — and the one people skip is the one that decides everything downstream:

| Weights | Harness | Isolates |
|---|---|---|
| theirs | theirs | The environment. A miss here means no work on your model can close the gap |
| theirs | yours | Your evaluator |
| yours | theirs | Your training |
| yours | yours | Where you started |

### The ledger, and the rule

Every axis gets `same`, `differs`, or `unknown` — and **`unknown` is not `same`**. An unread row is not a matching row.

**You may not write "does not reproduce" while the ledger holds an `unknown` row that could account for the gap.** Saying "I get 51.4 under this protocol, and here is the protocol" is always available, always true, and more useful to a reader.

[`examples/repro-ledger.md`](baseline-repro/examples/repro-ledger.md) is one worked through end to end, from an untidy request that opens "starting to think their number is optimistic". The bisection localises the gap to the evaluator in two hours; nineteen of twenty rows then close without a GPU; both rows that differ turn out to be house rules in the reader's own harness — a 300-step cap and open-loop chunk execution — which apply to every model that harness has ever run. The verdict is *we are measuring something else*, and the useful finding is not about the paper at all.

The axes are the ones specific to this field, ordered by how often they turn out to be the answer — success criterion, episode limit, reset distribution, aggregation, then the inference-time constants that exist nowhere in training. openpi integrates 10 Euler steps by default and VITRA 10 DDIM steps at `cfg_scale=5.0`; openvla denormalises by an `unnorm_key`, openpi by a flag choosing between mean/std and quantiles, VITRA by one statistics file per source dataset. **Every one of those changes the policy without changing a weight**, and none of them appears in a training config.

## vla-code-review

These errors share a shape: training completes, the loss curve looks normal, nothing errors, and the final number comes out a few points low — then gets blamed on the method.

Around 60 checks in eleven categories, covering the interaction between precision and learning rate, which dtypes a card supports, mixed-precision correctness, freezing and parameter groups, seeds and determinism, data and evaluation correctness, RL and VLA-specific traps, training monitoring, reproducibility and performance.

`reference/precedents.md` ties each check to a bug that shipped in a public repo — OpenVLA's evaluation geometry drifting between episodes, OpenVLA-OFT's action-head gradients never synchronising, LeRobot's checkpoint load silently returning an untrained model, openpi's precision gap between JAX and PyTorch. Append new cases as you find them; the list is meant to grow.
