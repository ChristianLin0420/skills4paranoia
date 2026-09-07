---
name: thesis-prereg
description: >-
  Write an investment thesis down and freeze it before buying: why this is mispriced and why
  the mispricing persists, the two to four claims that must be true, the specific observation
  that would falsify each, the horizon, and the exit conditions in both directions. Enforces
  one rule above the rest — the falsification horizon must be shorter than the holding horizon,
  or you will never sell for the right reason. Later reviews compare reality against the frozen
  document and name thesis drift when the reason you are holding is not the reason you bought.
  This drafts and stress-tests YOUR reasoning for your own review; it does not value anything,
  recommend anything, or tell you what to buy or sell. Use before opening a position, at a
  scheduled review, or when you notice you are justifying a holding differently than you used
  to. Chinese triggers: 幫我把投資論點寫下來 / 我為什麼要買這支 / 這個論點站得住嗎 / 什麼情況我該認錯 /
  我當初買它的理由還在嗎.
---

# thesis-prereg

A thesis you have not written down is a story you can revise after the fact. This freezes it first.

**Language.** Write in whatever language the user writes in. These instructions and the template are English because English is this repo's source language, not because the output must be.

## What this is not

**Not advice.** It does not value a business, judge whether a price is attractive, size a position, or say what to buy or sell. It takes a thesis you already hold and puts it into a form that can be wrong. Every judgement stays yours, and nothing here is a substitute for a licensed adviser.

That boundary costs less than it sounds like. Screeners hand you candidates, and candidates were never the constraint — **what separates outcomes is whether you can state a thesis that could be wrong, and whether you act when it breaks.**

## The rule that does the most work

> **The falsification horizon must be shorter than the holding horizon.**

If knowing you were wrong takes five years and you are holding for three, you have not written a thesis — you have written something that cannot be tested inside the time you are giving it, and you will exit on price or on boredom instead.

This is the direct sibling of the minimum detectable effect in `experiment-prereg`: both ask whether the thing you are about to commit to can actually resolve within the budget you are giving it. Most theses fail this on first writing, and the fix is to find a **nearer observable** — a leading indicator that moves within the horizon — not to extend the horizon.

## Fields, none optional

| Field | The failure it prevents |
|---|---|
| **The mispricing** | Why is it cheap, and *why does it stay cheap*? A value thesis without a mechanism is a story about a low multiple |
| **What must be true** | 2–4 load-bearing claims. More than four and you do not have a thesis, you have a wish |
| **Falsifier per claim** | A specific observation, with a date. "If growth slows" is a feeling; "revenue growth under 8% for two consecutive quarters" is a falsifier |
| **Horizon** | And what distinguishes *too early to tell* from *wrong* |
| **Exit, both directions** | Down: the thesis broke. **Up: the thesis played out.** Most people have a buy discipline and no sell discipline |
| **What would make you add** | Pre-committed, so averaging into a broken thesis is visibly different from adding to a working one |
| **The other side** | Someone sold this to you. State their case at its strongest |
| **The outside view** | What usually happens to situations like this. Your case is not the base rate |

Detail and the ways each field gets fudged: `reference/fields.md`.

## Reviews compare against the frozen copy

The document is dated and not edited. Reviews append.

**Reviews are scheduled by the horizon and by thesis events, never by price.** A price move is not information about your thesis; it is information about other people's. Wiring reviews to price is how a portfolio ends up managed by its most volatile holding.

**Drift is the thing being detected.** If the reason you give today for holding is not in the original document, that is not an update — it is a new, untested thesis wearing an old one's clothes. Name it, and either write it a document of its own or close the position. Procedure in `reference/review.md`.

## Input and output

**Input**: a position you hold or are about to open, and whatever you already believe about it. Untidy is fine; the fields are what make it tidy.

**Output**: `thesis-<name>-<date>.md`, frozen. Reviews append a dated block: what happened, which claims moved, whether any falsifier fired, and whether the stated reason for holding still matches the original.

**Not output**: a valuation, a price target, a recommendation, or a position size.

## Pairs with

- **`grill-deeper`** — run it on the thesis before freezing. The frontier mechanism finds the claim you have not examined, and its store remembers the kinds of question you go vague on
- **`allocation-jobs`** — this document says why you believe it; that one says what job it does in the portfolio, and what would count as failing that job
- **`crisis-indicators`** — for the market-level backdrop a thesis assumes without saying so

## Files

- `reference/fields.md` — every field, and how each one gets fudged
- `reference/review.md` — the review ritual, and detecting drift
- `templates/thesis.md` — the document
- `examples/filled-thesis.en.md`, `.zh.md` — a worked one. **Mock: the company does not exist**
