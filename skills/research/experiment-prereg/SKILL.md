---
name: experiment-prereg
description: >-
  Pre-registration for an experiment: before the compute is spent, write down and freeze the
  primary metric, the minimum detectable effect, what counts as null, the stopping and decision
  rules, and the evaluation protocol. Blocks the pseudoreplication of treating rollouts as
  independent samples. Use before committing GPU time, when designing an ablation or benchmark
  comparison, or when reproduced numbers do not match and the protocol needs pinning down. Also
  answers informal phrasings like how many seeds do I need / is this a fair comparison / is that
  gap significant / let us just try it. This does NOT design the experiment — for choosing the
  design itself (randomisation, blocking, factorial or crossover layouts) or closed-form power
  analysis, use a dedicated experimental-design or statistical-power skill. For the code rather
  than the protocol, use vla-code-review. Chinese triggers: 要跑幾個 seed / 這樣比較公平嗎 / 這個差距算不算顯著 /
  先跑跑看 / 這個實驗該怎麼定義成功.
---

# experiment-prereg

**This skill does not design experiments.** It takes a design that already exists and pins it down before the compute is spent.

What it does is pre-registration: declare the primary metric, what counts as null, the stopping and decision rules and the evaluation protocol, then **freeze them**. Discovering two months in that the design was wrong is this field's most expensive mistake, but deciding what counts as success *after* the run is worse — by then you will always find some slice that satisfies you.

It does not comment on whether your method is good; that is your expertise. It confirms one thing: **that whatever the result turns out to be, you will get a clear answer out of it.**

**Language.** Write in whatever language the user writes in. These instructions and templates are in English because English is this repo's source language, not because the output must be English.

## 1. Four fields, none optional

Do not launch without all four. Not being able to fill one in usually means the run should not happen yet.

| # | Field | Test |
|---|---|---|
| 1 | **Primary metric and minimum detectable effect** | One primary metric. How large a difference must you detect? How many seeds? |
| 2 | **What counts as null** | What range means the hypothesis did not hold |
| 3 | **Stopping and decision rules** | What condition stops the run; what you do for each outcome band |
| 4 | **Evaluation protocol** | Held-out level, success criterion, seed protocol, perturbation |

**Check one thing before any of this**: do your hypothesis and its negation predict *different* observations? If they predict the same thing, the experiment does not discriminate, and pinning a measurement contract to it pins down something meaningless.

Example: "success went up after adding the world model" follows just as well from "it shares physics across tasks" as from "it added parameters". In that situation, find a manipulation that separates the two before going further.

### Why the second field matters most

"What counts as null" is the field people skip and avoid. Skipping it does not cost you a document, it costs you **the ability to be wrong** — run first and define success later and there is always some task subset, some checkpoint, some aggregation that looks like a win. Writing null down in advance binds you while you still have no motive to cheat.

Press until the answer is concrete. "If the effect is unclear" is not an answer; "the mean difference on the primary metric is under 5 percentage points, or the 95% interval crosses zero" is.

### Baseline matching: do not miss the search budget

Matching data, compute and parameter count is not enough. **Your method tuned over 100 configurations against a baseline on defaults** is still an invalid comparison, and it is the most common unfair one because it is less visible than the other three.

Either give both sides the same number of trials, or write "ours searched N, baseline searched M" into the document so the reader can discount it (Dodge et al.).

## 2. How many seeds

Most VLA papers report three seeds and claim two or three points of improvement. That is not readable from the data.

At 80% power and two-sided α=0.05, the smallest difference n seeds per arm can detect is about `2.80 × σ × √(2/n)`:

| Seeds per arm | Detectable | At σ=4pp that is |
|---|---|---|
| 3 | 2.29 σ | ≥ 9.1 percentage points |
| 5 | 1.77 σ | ≥ 7.1 |
| 10 | 1.25 σ | ≥ 5.0 |
| 20 | 0.89 σ | ≥ 3.5 |

**How to use it**: estimate σ from existing runs (the standard deviation across seeds at the same setting), decide how large a difference would matter, then read off the seeds you need. If that number is unaffordable, say so in writing — **this experiment cannot detect the effect you are after** — which is far more honest than reaching for "the trend is positive" afterwards.

With σ unknown, run three seeds to estimate it and then decide whether to add more. That is a reasonable two-stage approach, but declare it in advance; do not decide after seeing the numbers.

**Running ten seeds and reporting the best three undoes the entire exercise.** Agree the count in advance and report all of them. Excluding a run needs a rule defined beforehand — "diverged with NaN loss" — applied identically to both arms.

### Do not let rollouts stand in for seeds

The most damaging statistical error here, and in classical design it has a name: **pseudoreplication**.

A hundred rollouts from one checkpoint are **not a hundred independent samples**. They share the weights and every random choice of that training run. The unit of replication for comparing methods is the **training run (seed)**, not the rollout.

- Variation between rollouts measures how unstable that checkpoint is
- Variation between seeds measures how unstable the *method* is

**Do it this way**: each seed gets its own mean success rate first, giving one number per seed; then take the mean and standard deviation across those numbers. `n` is the seed count, not the rollout count.

Treating 300 rollouts (3 seeds × 100) as n=300 shrinks the error bar by roughly ten, after which any two curves look separated. Every `n` in the table above is a seed count.

Rollouts still need to be plentiful enough that each seed's mean is stable, but **more rollouts buy no statistical power; only more seeds do**.

## 3. Pin the evaluation protocol

This section comes from real reproduction failures (see `vla-code-review/reference/precedents.md`). Leave these four unfixed and your numbers cannot be compared with anyone's, including your own three months from now.

See `reference/evaluation-protocol.md`. In brief:

- **Which layer held-out is cut at** — task name, object instance, scene and demonstrator are four different levels. Change only the task name and the number measures memorisation, not generalisation.
- **The full success criterion** — including hold duration and gripper state. Without those, the criterion fires early.
- **The eval seed protocol** — a fixed set, independent of training step, reseeded every episode.
- **Perturbation testing** — without it you do not know whether 90% is capability or rote learning.

### Do not let hardware and time in

Classical design randomises run order against batch drift. Here that means: **do not put the control on one node and the treatment on another**, and do not run one arm last month and the other this week. Driver versions, individual card variation and shared-cluster load all leak into your effect.

Randomise the assignment of runs to nodes, or at least make every arm span every node. Record which run went to which machine and when.

## 4. Sanity-check the compute budget

Estimate the GPU-hours, then ask: **if the result is the best possible one, does it change any decision?**

If not, do not run it. That sounds obvious, but "let us just try it" consumes more compute than anyone admits.

Ask the same of the worst case. If both outcomes lead to the same next step, the experiment carries no information.

## 5. The interview

Do not ask open questions. Derive candidate answers from the existing material — the design doc, past runs, the paper — and let the user reject or correct them. Full protocol in `reference/interview.md`.

Five rounds: the yes/no question, baseline and budget, the definition of null, stopping and decision rules, and the most likely way this run is wasted.

**When the user says "let us just try it"**, neither comply nor refuse. Ask instead: "then shall we set the stopping rule at 20k steps and look once?" Turn an exploratory run into an exploratory run with an endpoint.

## 6. Freeze after launch

Once the document is settled and the run starts, **the primary metric and the definition of null are frozen**.

Changing them is allowed, but it goes in the decision record with the reason and the date. Changing the criterion afterwards and leaving no trace is fooling yourself — the thing this whole repo exists to prevent.

## 7. Output

`templates/prereg.md` is the blank; `examples/filled-prereg.en.md` and `.zh.md` are worked ones — start from the example, the margin notes there show how specific each field has to be.

The document is three things at once: the pre-launch checklist, the source for the deck's setup page in `research-deck`, and the only record of what you were actually testing when you look back in three months.

Return to it after the run and go field by field.

## 8. Related

- `vla-code-review` — run it before launch too. That one covers whether the code is quietly wrong; this one covers whether you defined what "right" means.
- `research-deck` — the document becomes the deck's experimental setup page.
