---
name: baseline-repro
description: >-
  Your number does not match a published one. Before concluding anything, bisect the pipeline
  with their checkpoint and their eval script to find which half the gap lives in, then build a
  delta ledger of every axis on which the two setups differ — success criterion, episode limit,
  reset distribution, simulator and asset versions, action space convention, checkpoint identity,
  sampling hyperparameters, normalisation statistics, aggregation. Separates three claims that
  get conflated: their number is wrong, you are measuring something else, or their setup has an
  advantage you do not. Use when reproducing a baseline, when a reimplementation lands short, or
  before writing that something does not reproduce. This is the ENTRY POINT for a number that
  disagrees with a published one; it hands off to vla-code-review once the gap is localised to
  your training, and to experiment-prereg for any protocol field the paper leaves unspecified. Chinese triggers: 跑不出論文的數字 / 這個 baseline
  對不上 / 復現不了 / 我的結果比他們低 / 這個數字是怎麼算出來的.
---

# baseline-repro

They report 63.2. You get 51.4. This decides what that means.

**Language.** Write in whatever language the user writes in. These instructions are English because English is this repo's source language, not because the output must be.

## The claim you are actually making

Three different statements get written as "it does not reproduce", and they need wildly different evidence:

| Claim | How common | What it takes to say it |
|---|---|---|
| **You are measuring something else** | Most of the time | Nothing — this is the default until ruled out |
| **Their setup has an advantage you do not** | Often | Name the advantage: a checkpoint, a data version, compute |
| **Their number is wrong** | Rare | An empty ledger, their own artifacts, and the protocol matched |

Only the third is a claim about the paper. The first two are claims about you. **Most public reproduction failures are the first, written as the third** — and it is a costly thing to get backwards, both for you and for whoever wrote the paper.

## 1. Bisect before you enumerate

Do not start by listing what might differ. Start by cutting the space in half, which is usually cheaper than reading a single config file carefully.

| Weights | Eval harness | Isolates |
|---|---|---|
| theirs | theirs | The environment and the machine. If this misses, nothing downstream is interpretable |
| theirs | yours | **Your eval harness** — same policy, different measurement |
| yours | theirs | **Your training** — different policy, same measurement |
| yours | yours | The full delta you started with |

Run the first cell first. It is the one people skip because it feels like it proves nothing, and it is the one that decides whether the next week is spent on your trainer or your evaluator.

**When their code is not released**, this table collapses to one cell, every row of the ledger below opens as `unknown`, and the strongest verdict available to you is *cannot be attributed*. Not *does not reproduce*. Say so.

## 2. The delta ledger

One row per axis, and three states — the distinction between them is the whole point:

| State | Means |
|---|---|
| `same` | Checked, and identical. Record where you checked |
| `differs` | Checked, and different. Record both values |
| `unknown` | Not determinable from what is published, or not yet looked at |

**`unknown` is not `same`.** An unread row is not a matching row, and a ledger of blanks is not agreement.

The axes are in `reference/axes.md` — the ones specific to VLA, world models and RL, where most of them live in evaluation rather than in the model. Template in `templates/ledger.md`.

## 3. Order by cost, not by suspicion

Every row gets a cheapest test that would settle it. Most are free — a constant in a config, a line in an eval script, the shape of an action tensor. **Do the free ones before any of the ones that need a GPU**, even the ones you find less likely: an hour of reading routinely closes rows that a day of compute would not.

## The rule

**You may not write "does not reproduce" while the ledger holds an `unknown` row that could account for the gap.**

Nothing stops you saying "I get 51.4 under this protocol, and here is the protocol." That statement is always available, always true, and it is what a reader can actually use.

## What closes a ledger

A row is closed by evidence, not by plausibility. "Probably the same" is `unknown`.

When every row that could account for the gap reads `same`, and the bisection shows the gap survives their weights and their harness, you have a real disagreement — and now it is worth reporting, with the ledger attached, because the ledger is what makes it credible.

When a row reads `differs` and closing it moves your number, you have your answer and it was never a scientific dispute.

## Input and output

**Input**: the reported number and where it is reported, their repo if there is one, your setup, and your number.

**Output**: `repro-ledger.md`, and it is **front-loaded** — the same doctrine `research-deck` applies to a
deck. The verdict and the scope are the first two lines; a reader who stops there has the answer. Everything
below is evidence for it.

| Section | Carries |
|---|---|
| **Verdict** | One sentence, then reported · measured · gap · what accounts for it |
| **Scope** | The exact claim under test — table, row, number — and what is *not* under test |
| **What accounts for the gap** | Contributing factors, plural. Two ordinary conventions compounding is the usual shape; one dramatic cause is not |
| **Bisection** | The four cells, and which half they localised it to |
| **Ledger** | A roll-up line, then only the rows that are not `same`. The identical ones collapse into a `<details>` — they are evidence the ledger was worked, not something to read |
| **What was easy · what was difficult** | Kept separate, because they are co-dependent rather than opposite: released weights can make the start trivial while an unstated convention makes the middle expensive. This is what tells the next person what to budget |
| **Where this bites beyond one number** | What outlives this comparison. A house rule in your own harness applies to every model it has ever run |
| **Action items** | Owner and date on each. Without both it is a wish |
| **Still unknown** | Every `unknown` row that could account for the gap |

Seventeen rows reading `same / — / free` are 85% of a table and none of its information. Roll them up.

**Not output**: a judgement about the paper's honesty. The ledger either accounts for the gap or does not.

## Pairs with

- **`codebase-onboarding`** — map both repos and diff the maps. Preprocessing and action-space deltas are visible there in a way they are not in a config diff
- **`experiment-prereg`** — their evaluation protocol reconstructed in the same fields you would pin your own with; if a field cannot be filled from the paper, that is an `unknown` row, not a detail
- **`vla-code-review`** — when the bisection puts the gap in your training, that is where to look next
- **`run-triage`** — for a number that disagrees with your own expectation rather than with a paper

## Files

- `examples/input.en.md`, `examples/input.zh.md` — what a real request looks like, untidy
- `examples/repro-ledger.en.md`, `examples/repro-ledger.zh.md` — the same one filled in:
  bisection, twenty rows, verdict. The Chinese pair is the deliverable a Chinese user gets,
  technical terms left in English the way this field is actually written
- `reference/axes.md` — the delta axes, and which ones actually move numbers
- `reference/bisection.md` — running the 2×2, and what each cell rules out
- `templates/ledger.md` — the ledger
