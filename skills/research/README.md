# research

Skills for doing the research itself, as distinct from `work/`, which is about communicating and recording it.

| Skill | What it covers | When |
|---|---|---|
| [`experiment-prereg`](experiment-prereg) | Pin the measurement contract and freeze it | Once you have decided to spend the compute |
| [`vla-code-review`](vla-code-review) | Hunts engineering failures that never raise and only make the numbers worse | Before launch, or when numbers do not reproduce |
| [`baseline-repro`](baseline-repro) | Bisects a gap against a published number, and ledgers every axis on which the two setups differ | When your number lands short of someone else's |
| [`paper-teardown`](paper-teardown) | Rebuilds a paper as an interactive explainer — compiled maths, its own figures, and a code survey that runs the code | When you need to actually understand a method, not skim it |

The first two are complementary before a run: one covers whether you defined what "right" means, the other whether the code is quietly wrong. The third is for afterwards, when the number disagrees with a paper. The fourth comes first of all, when you are still deciding whether a method is worth any of the other three.

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

[`examples/repro-ledger.en.md`](baseline-repro/examples/repro-ledger.en.md) — and [`.zh.md`](baseline-repro/examples/repro-ledger.zh.md) — is one worked through end to end, from an untidy request that opens "starting to think their number is optimistic". The bisection localises the gap to the evaluator in two hours; nineteen of twenty rows then close without a GPU; both rows that differ turn out to be house rules in the reader's own harness — a 300-step cap and open-loop chunk execution — which apply to every model that harness has ever run. The verdict is *we are measuring something else*, and the useful finding is not about the paper at all.

The axes are the ones specific to this field, ordered by how often they turn out to be the answer — success criterion, episode limit, reset distribution, aggregation, then the inference-time constants that exist nowhere in training. openpi integrates 10 Euler steps by default and VITRA 10 DDIM steps at `cfg_scale=5.0`; openvla denormalises by an `unnorm_key`, openpi by a flag choosing between mean/std and quantiles, VITRA by one statistics file per source dataset. **Every one of those changes the policy without changing a weight**, and none of them appears in a training config.

## paper-teardown

One paper in, one HTML explainer out. It fetches the LaTeX source rather than the PDF, so the equations are the authors' and not something retyped off a rendered page; compiles them to MathML at build time, so they are selectable, searchable and need no CDN; pulls the paper's own figures out of the source tarball; and if code exists, surveys it end to end.

**The rule: every symbol gets a home.** An equation is not explained until every symbol in it has a name, a shape and a *provenance* — `input`, `learned`, `fast`, `hyper`, `derived` or `index`. Recitation is restating the equation in words. Explanation is being able to say what breaks if a given symbol is wrong. In the report the two are linked: click `W` in Equation 1 and every form of it lights — `W_t`, `W_{t-1}`, the subscript on `∇_W`, the one inside `f_{W_{t-1}}` — along with its row in the table.

**Reading is not enough.** Where code exists it gets run, and every claim carries how it was established: `verified` (observed at runtime), `stated` (the source says so), `inferred` (your reading, dashed border). This is not ceremony. In the RoboTTT example, one line looks wrong on the page and is correct at runtime — a negated loss and an added gradient compose to a descent step — while another looks fine and doubles the attention branch of every layer it wraps. Two plausible readings, opposite verdicts, and only a probe separates them.

**Third-party code is labelled on every claim it supports.** A reimplementation is evidence about the reimplementation; it is evidence about the paper only where the two agree. It gets a divergence table, never a merged narrative, and each divergence is graded *cosmetic*, *a choice*, or *a defect* — the last only ever from a measurement.

Two worked examples ship, and they fail in opposite directions — which is the point.

[`examples/robottt`](paper-teardown/examples/robottt) — [RoboTTT](https://arxiv.org/abs/2607.15275), NVIDIA / Stanford / UT Austin. No official code, so a third-party reimplementation is surveyed. Running it finds that one line looks like an ascent step and is a descent step, while another looks fine and doubles the attention branch of every layer it wraps — measured at exactly 2.000000 with the gate zeroed, which defeats the stated purpose of the paper's gating equation.

[`examples/lingbot-va2`](paper-teardown/examples/lingbot-va2) — [LingBot-VA 2.0](https://arxiv.org/abs/2607.08639), Robbyant / Ant Group, 29 authors. Here official code *does* exist: the authors' own organisation, Apache-2.0, 1,863 stars, actively maintained, with this paper's PDF committed at the root. **It implements version 1.0** — the model the paper defines itself against. All five of the paper's mechanisms are absent, all four markers of the thing being departed from are present, and the only arXiv id anywhere in the repository is the previous paper's. Every signal a reader uses to conclude "this is the code for that paper" fires correctly, and the conclusion is wrong.

Both ship `probes.py` and its recorded output, so every claim can be re-run. Both are in English and Chinese, Chinese down to the headings and figure readings.

## vla-code-review

These errors share a shape: training completes, the loss curve looks normal, nothing errors, and the final number comes out a few points low — then gets blamed on the method.

Around 60 checks in eleven categories, covering the interaction between precision and learning rate, which dtypes a card supports, mixed-precision correctness, freezing and parameter groups, seeds and determinism, data and evaluation correctness, RL and VLA-specific traps, training monitoring, reproducibility and performance.

`reference/precedents.md` ties each check to a bug that shipped in a public repo — OpenVLA's evaluation geometry drifting between episodes, OpenVLA-OFT's action-head gradients never synchronising, LeRobot's checkpoint load silently returning an untrained model, openpi's precision gap between JAX and PyTorch. Append new cases as you find them; the list is meant to grow.
