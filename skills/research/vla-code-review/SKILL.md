---
name: vla-code-review
description: >-
  Review VLA / WAM / RL training and evaluation code for the engineering-level failures that
  never raise and only make the numbers worse — precision paired badly with the learning rate, a
  dtype the card does not support, DDP gradients never synchronised, a checkpoint load that
  silently returns an untrained model, evaluation state leaking between episodes, a success
  criterion that fires early. Produces a visual review report. Use when reviewing a robot-
  learning, VLA, world-model or RL codebase before launching an expensive training run, or when
  reproduced numbers do not match expectations.
---

# vla-code-review

Hunts the errors that **do not raise, and only make the numbers worse**. Problems with the method itself are out of scope — that is the researcher's expertise. This covers the class where the method was right and the implementation ate it.

What these have in common: training completes, the loss curve looks normal, nothing errors, and the final number comes out a few points below what it should be — then gets diagnosed as the method not being good enough. Every entry in `reference/precedents.md` is a bug that shipped in a well-known repo.

**Language.** Write in whatever language the user writes in. These instructions and the report template are in English because English is this repo's source language, not because the output must be English. A Chinese user gets a Chinese report with the same structure.

## 1. Three outcomes, never a fourth

```
[PASS]   2.6 clip after unscale            train.py:214
[FOUND]  4.4 DDP bypassed via .module      train.py:388
         action-head gradients are never all-reduced
[N/A]    7.1 truncation vs termination     this codebase is not RL
```

**Anything uncertain is FOUND, with a line number, for a human to judge.** This checklist hunts errors that look correct, and the dominant failure mode is an agent marking something PASS because the code reads sensibly. Marking a real problem PASS costs the user two months of compute; marking a non-problem FOUND costs them three minutes. Those are not symmetric.

Say explicitly when something was not checked. Do not leave it blank — blanks get read as passes.

## 2. Order

**Run Tier 0 first.** The ten items at the top of `reference/checklist.md`; any one of them alone is enough to waste a whole batch of experiments. If any fails, the report's verdict is "do not launch" and everything else ranks below it.

**Then work the eleven categories.** Precision and hardware, precision and learning rate, mixed-precision correctness, freezing and parameter groups, seeds and determinism, data and evaluation correctness, RL-specific, VLA/WAM-specific, training stability and monitoring, checkpointing and reproducibility, performance traps.

**Mark a whole category N/A when it does not apply.** A codebase that is not RL gets category 7 marked off entirely; do not go hunting.

**Finish by listing what static review cannot see.** Five kinds of item need an actual run (which SDPA backend was used, the fraction of zero-displacement weights, whether seeding reaches the dataloader workers, whether the dataloader starves the GPU, whether NVLink is in play). List them separately; they cannot be folded into the passes.

## 3. Severity

| Level | Meaning | Test |
|---|---|---|
| **Blocker** | The conclusions from this batch are unusable | Do not launch until fixed, and do not trust numbers already produced |
| **High** | Numbers are systematically affected | The direction may still hold, the magnitude does not |
| **Medium** | Measurable but bounded | This round can proceed; fix before the next |
| **Watch** | I am not sure; you need to judge | Something looks off but the agent lacks the domain context |

**Watch exists on purpose.** An agent can see that a success criterion has no hold-duration requirement but cannot know whether that is acceptable for this task. Without this level, agents write guesses up as findings in order to look useful.

## 4. Fields every finding needs

- **Symptom** — what the user would observe. Not "this is written wrong" but "stops improving late in training while grad norm looks normal".
- **Cause** — why, in a sentence or two, with a mechanism rather than a label.
- **How to confirm** — **one concrete, runnable check.** Compare parameter hashes across two ranks, diff `body_pos`, count zero-displacement weights. This field matters most: it means the user does not have to trust the report.
- **Fix** — what to change.
- **Precedent** — look in `reference/precedents.md` and link the public issue if there is one. **If there is no match, leave it out**; do not attach a loosely related link to look grounded.

## 5. The report

`templates/report.html` is ready to adapt and shares the design system with `research-deck`. Format spec in `reference/report-format.md`.

Top to bottom: the verdict (a plain sentence, not a count) → four tallies → the Tier 0 gate table → findings by severity → the coverage matrix → what static review could not reach.

**The verdict is a sentence in plain language.** Not "7 issues found" but "do not launch: the multi-GPU gradients are not synchronised and the checkpoint may not have loaded, so the conclusions from this batch are unusable". The reader should know from one glance whether to keep reading.

## 6. Adding precedents

Append new public issues to `reference/precedents.md` as you find them. Criteria: **public, verifiable, and a silent failure.** Installation errors, version conflicts and CUDA OOM do not qualify — those announce themselves and need no review to catch.

## 7. Files

- `reference/checklist.md` — around 60 items in eleven categories, each as symptom → how to check → fix
- `reference/precedents.md` — the real case behind each check
- `reference/report-format.md` — report spec
- `templates/report.html` — the report template
