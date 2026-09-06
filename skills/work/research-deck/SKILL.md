---
name: research-deck
description: >-
  Turn a folder of experiment material — figures, run logs, experiment and model design notes,
  meeting notes — into a research deck (PPT / Keynote / HTML), after interviewing the user about
  what actually matters. Enforces a three-page front that carries the whole argument (problem,
  solution, results) with everything after it as evidence. Figures the user supplies are placed
  as-is; figures whose underlying data exists are redrawn to the theme so the styling stays
  uniform. Use when someone points at a folder of experiment material and wants slides, a deck
  or a presentation out of it. Chinese triggers: 做簡報 / 做一份投影片 / 幫我把實驗結果做成報告 / 週報 / 進度回顧.
---

# research-deck

The input is a folder, the output is a deck. The part that matters most in between is not layout, it is **finding out what matters**.

The material will not tell you — that lives in the user's head. So the order is: inventory → interview → confirm the plan → only then write.

**Language.** Write in whatever language the user writes in, and set the deck's own `lang` accordingly. These instructions are in English because English is this repo's source language; a Chinese user gets a Chinese deck, and the examples ship in both.

This skill is the entry point; it loads two sibling skills when it needs them:

- **`research-figures`** — before laying out evidence in step 5. Decides redraw-or-place per figure, and the axis, error-band and reference-line specs for redrawn ones.
- **`deck-design-system`** — before emitting in step 7. Palette, type scale, grid, per-layout geometry.

Do not write specifications from memory; those two files are the only source.

## 1. Phase 0 is mandatory

Given a folder, **work through the inventory and interview in `reference/intake.md`** before writing any slide.

1. **Inventory** — scan the folder, read every `.md` in full, sample the logs, list every figure, and show the user what you found. Ask nothing in this phase.
2. **Interview** — five rounds: the problem and its decomposition, a verdict on every figure, results and what is still unsolved, the audience, gap backfill. Propose candidate answers; do not ask open questions.
3. **Confirm the plan** — lay out the Q decomposition, which figure hangs off which Q, the results table columns and the page estimate. Do not start writing until the user agrees.

The only reason to skip the interview is the user saying "do not ask, just do it". Then do it, but afterwards tell them which judgements you made on their behalf, especially which figures you dropped.

## 2. The front three pages are the whole argument

| Page | Content | Test |
|---|---|---|
| 1 · Problem | One big problem, split into 2–4 mid-level problems (Q1…Q4), each with 2–3 concrete technical obstacles | Can the reader judge for themselves whether this is worth solving |
| 2 · Solution | The mechanism in a sentence, then **one row per Q** from page 1 | Every Q has a row; no orphan Q, no unclaimed mechanism |
| 3 · Results | A method-by-metric table plus one key figure | Includes the cell that is not solved yet, not only the wins |
| 4+ | Evidence. Every page declares `solves=Q2` and introduces no new conclusion | Would deleting this page cost some Q its support |

Consequences:

- **No "so here is what I need you to decide" page.** This is a research deck, not an internal proposal. Limits go in a footnote on the results or evidence pages.
- **The problem page is not "background".** No field introduction, no related work, no motivational story. State the problem and split it.
- **The results page must contain what is unsolved.** Only showing wins turns it into marketing. The failed cell on the table is where credibility comes from.
- An evidence page exists for exactly one reason: to support some Q. If you cannot say which, delete it.

### How to split the problem

The big problem is one sentence, the mid-level problems are its necessary conditions, and the sub-problems are concrete technical obstacles. Test: a sub-problem must be measurable and falsifiable, not an adjective.

Bad: "generalisation is insufficient", "efficiency needs improving".
Good: "changing material or lighting breaks it", "diffusion methods run 23ms/step and cannot hold 30Hz".

## 3. Where figures come from

Three sources, decided figure by figure during the interview. Do not assume.

| Source | When | Style |
|---|---|---|
| **Redraw to the theme** | The underlying data exists (CSV, jsonl, log) | Uniform with the rest |
| **Place the user's original** | Cannot be reproduced: architecture diagrams, pipelines, rollout frames, on-robot capture | Differs from the other pages, but irreplaceable |
| **Drop it** | Hangs off no Q | — |

**The test: redraw if the underlying data exists, place if it does not.** Statistical figures can almost always be redrawn as long as the numbers can be found. Redrawing gives uniform colour, type and axes; placing keeps the things that cannot be generated. You need both to be uniform *and* complete.

A placed original will not match the surrounding type and colour. Do not crop or filter it to hide that — it only makes it worse. Keep the title and footnote format consistent and let the framework's uniformity carry the style's inconsistency.

Placement layouts: `E20 figure` (one), `E21 figure-pair` (two side by side), `E13 filmstrip` (a sequence), `E14 architecture` (figure plus notes), `E15 image-full` (bleed).

### Every figure needs analysis

**A page holding only a figure or only a table is not acceptable.** Two or three analysis lines go beside or under it, in the form `- observation | why it matters`:

```markdown
- The split happens at 50k steps | Before that the three curves overlap, so the gap is not from initialisation
- The baseline flattens after 125k | Ours is still climbing, so more data still buys progress
- The ±1σ band narrows after 100k | All three seeds agree; this is not one lucky run
```

The title states the conclusion; the analysis states **how the figure gets you to that conclusion**. They are different and both are required. Tables too — a latency breakdown sitting there tells the reader every cell but not which cell to look at.

**If you are unsure what the analysis should be, go back and ask. Do not invent it.** You can see the curve splits at 50k; you cannot see what that means for their research. Ask "what do you want the reader to see here" for every figure during the interview — the answer is these lines.

Whether the analysis sits to the right or underneath is **decided automatically** by how much width the figure actually needs: few horizontal slots (three bars, a three-column matrix, a table under five columns) put it on the right so the figure keeps its height; many (a nine-point curve, a wide table, a multi-panel figure) put it underneath so the figure keeps its width. Rules in `reference/layouts.md`; override with `analysis=right` or `analysis=below`.

## 4. Density

One page carries one complete piece of evidence: the figure, the numbers, and **the conditions they were measured under**. The test is whether the page lets someone judge the conclusion for themselves.

Required:

- **A conditions footnote on every figure and table** — n, seeds, hardware, hyperparameters, method of measurement. The line starting with `~ `.
- **Draw dispersion for multi-seed results**, never a bare mean.
- **Draw a reference line where there is a baseline**, so the reader knows what good means.
- **Compute a delta where there is a comparison** — percentage points or relative percent, one or the other throughout.
- **Monospace every number**, so table and chart values line up.

Not allowed:

- **A page with a figure and no analysis.** That hands the interpretation back to the audience.
- **A page carrying one sentence.** Statement pages and pull quotes both count — a sentence is not worth a slide; fold it into a figure's analysis or a results title.
- **A "here comes the evidence" divider.** Evidence pages announce themselves with `solves=Qn`.
- **A closing "thank you" page.** The last page should be the last piece of evidence.
- A page of three or four large numbers and an adjective. That is a promotional page; use a table.
- Figures with no axis label or unit.
- "Substantially improved", "significantly better" and other claims without numbers.
- More than five bullets. Reaching for bullets usually means you have not turned it into data yet.

## 5. Process

**Step 1 — finish phase 0.** See `reference/intake.md`. Do not proceed without a plan the user has agreed to.

**Step 2 — write the problem page** from the confirmed decomposition.

**Step 3 — write the solution page, row by row against the Qs.** One row per Q: the mechanism, and the key number. A Q with no matching mechanism means the solution does not cover a problem you raised — either add the mechanism or drop the Q.

**Step 4 — write the results page.** Method by metric, best values marked, and the unsolved metric the interview surfaced left on the table.

**Step 5 — lay out the evidence.** Load `research-figures` first, then follow the figure-to-Q map from the interview. Redrawn figures come from the data; placed ones use `E20` / `E21` / `E13` / `E14`. Layout selection in `reference/layouts.md`.

**Step 6 — self-check, then emit.** Section 7.

**Step 7 — emit.** Load `deck-design-system` for the palette, type scale and geometry, then follow `reference/emit.md`.

## 6. Input format

The intermediate format is one markdown file — versionable and diffable. Full spec in `reference/structure.md`, complete examples in `examples/`, and six rendered sample pages in `examples/preview/` if you want to see what comes out before reading the spec.

```markdown
---
title: Meridian-1 quarterly review
lang: en
theme: slate-blue
typeface: plex
---

<!-- P1 problem -->
# The one big problem, in a sentence
- Q1 | mid-level problem | obstacle | obstacle | obstacle
- Q2 | mid-level problem | obstacle | obstacle
> What happens if it stays unsolved

<!-- P2 solution -->
# The mechanism, in a sentence
![architecture](figures/arch.png)
- Q1 | the mechanism that addresses it | key number
- Q2 | the mechanism that addresses it | key number
~ conditions

<!-- P3 results -->
# The result in a sentence, including what is not solved
| Method | Metric A | Metric B | The unsolved one |
| --- | --- | --- | --- |
| Baseline | … | … | … |
| Ours | *… | *… | *… |
~ conditions

<!-- E20 figure solves=Q2 -->
# What this figure shows (a conclusion, not a topic)
![](figures/rollout_grid.png)
- observation | why it matters
- observation | why it matters
~ conditions
```

`~ ` is the conditions footnote, `- observation | why it matters` is the analysis (two or three required on any figure or table page), `*` prefixes a cell that takes the accent colour, and `solves=Q1` declares which mid-level problem the page supports.

**Keep `deck.md` in the project under version control.** Next time round the problem decomposition usually does not change; only the evidence pages and the results numbers do. Use the incremental path in `intake.md` rather than interviewing again.

## 7. Self-check before emitting

1. Has every figure been given a verdict (redraw / place / drop)?
2. **Does every figure and table page carry two or three analysis lines?** Tables included.
3. Does every Q have a matching row on the solution page?
4. Does every Q have at least one evidence page?
5. Is there a page whose deletion would cost no Q its support? Delete it.
6. Does the results table include the metric that is not solved?
7. Does every figure and table have a conditions footnote?
8. Is dispersion drawn for multi-seed results, and a reference line where there is a baseline?
9. Is there a page of large numbers with no table?
10. Is there a "what I need you to decide", a divider, a thank-you, or a single-sentence page? Delete it.
11. One palette, one typeface, one language throughout?
12. Are titles conclusions rather than topics?

## 8. How the three skills divide up

| Skill | Who invokes it | When |
|---|---|---|
| `research-deck` | The user | The only entry point |
| `research-figures` | Loaded by `research-deck` at step 5 | Also standalone: plot one paper figure, or decide redraw-vs-place for an existing one |
| `deck-design-system` | Loaded by `research-deck` at step 7 | Also standalone: review an existing deck, look up a colour, check geometry for a new layout |
