---
name: research-figures
description: >-
  Specifications for research figures — training curves with error bands, task-by-method
  matrices, ablation tables with a delta column, baseline reference lines, and the conditions
  footnote. Read before plotting any experimental result. Covers the decision of whether to
  redraw a figure from its underlying data or place the one the user already has. Use when
  plotting experiment results, training curves, ablations, benchmark comparisons, or success-
  rate matrices for a paper or a deck.
---

# research-figures

What separates a paper figure from a marketing figure is not the artwork, it is **whether it says how it was measured**. Without the conditions, a figure is decoration.

Colours and type sizes are in `deck-design-system`.

**Language.** Write in whatever language the user writes in. These instructions are in English because English is this repo's source language; axis labels, captions and footnotes should be in the user's language.

When producing a whole deck, `research-deck` loads this automatically before laying out evidence — the user does not need to invoke it separately. Invoke it on its own to plot a single paper figure, or to decide whether an existing figure should be redrawn or placed as-is.

## 0. First decide: redraw or place as-is

Users often already have figures. Do not redraw everything, and do not place everything.

| Source | When | Result |
|---|---|---|
| **Redraw to the theme** | The underlying data still exists (CSV, jsonl, log) | Colours, type and axes match the rest |
| **Place the original** | Cannot be reproduced: architecture diagrams, pipelines, rollout frames, on-robot capture, screenshots | Style differs from the other pages, but irreplaceable |

**The test: redraw if the underlying data exists, place if it does not.** Statistical figures — curves, bars, matrices, ablations — can almost always be redrawn as long as the numbers can be found, and redrawing them is what makes a deck look like one person made it.

Decide this figure by figure during the interview; do not assume. When something is obviously a statistical plot but the numbers cannot be found, ask whether the original log still exists.

The specifications below apply to redrawn figures. For a placed original, just keep the title and the `~` conditions footnote in the same format; do not crop or filter it in an attempt to unify the style.

## 1. The minimum for any figure

A figure is not finished without these five:

1. **Axis labels and units** — numbers without units cannot be compared.
2. **Dispersion** — multiple seeds means a ±1σ band or error bars; a mean line alone hides variance.
3. **A reference baseline** — draw and label it, so the reader knows what "good" is relative to.
4. **A conditions footnote** — n, seed count, hardware, key hyperparameters, how it was measured.
5. **Analysis** — two or three "observation | why it matters" lines. The figure gives the numbers; the analysis says where to look. Tables need this too.

Example footnote: `ManiSkill-20 · 20 tasks · 3 seeds · ±1σ · A100×8 · rollouts=100/task · lr 3e-4, bs 256`

## 2. Choosing a form

| Shape of the data | Use | Not |
|---|---|---|
| Several lines over training steps | Line plus ±1σ band | A table |
| Task by method scores | Heat matrix, best marked per row | Grouped bars |
| A few quantities compared | Bars with delta annotations | Pie |
| Proportions or ranking (≤6) | Horizontal bars | Pie |
| Ablations, one mechanism at a time | Table with a delta column | A line plot |
| Hyperparameters, hardware, data specs | Key-value table, values monospaced | Bullets |
| Two related quantities | Side-by-side panels under one title | Overlaid on one axis |

There is no pie chart. Use horizontal bars or a 100% stack for proportions.

## 3. Axes

**Ticks must bracket the data.** Pick a nice step (1 / 2 / 2.5 / 5 × 10ⁿ), round the lower bound down and the upper bound up until it is **greater than or equal to the data maximum**. The common error is computing from the data range and stopping there, which draws the topmost series outside the plot box. With an error band, compute the range from the band's bounds, not the mean.

Tick labels monospaced, 9.5pt, `ink3`, right-aligned. Gridlines `rule_soft`, the baseline `rule`.

Keep x labels under eight. When there is an axis name, measure its width first and drop any tick label that would run into it — skipping only the last one is not enough on a narrow plot, and the narrower it gets the more collide.

## 4. Lines and error bands

Draw order: **bands → gridlines → reference line → lines**. Bands go before the gridlines or they cover them.

- Bands use `band` colours, no stroke.
- Line weight 1.8 for the primary series, 1.4 for the rest.
- No legend — label each series at the end of its line in the line's own colour, reserving width on the right.
- A 4.4pt square marker at the end.
- Reference line in `ink3` at 0.9pt, label to the **left** above the line — on the right it collides with the series end labels.

## 5. Bars

- Only the most important bar gets the accent colour; the rest use the grey ladder.
- Values outside the bar, monospaced.
- With a comparison, add a delta: `pp` for percentage points, `pct` for relative percent. Use one or the other throughout.
- Horizontal bars: category label left, value right, delta one column further right.
- Corner radius 1.5, no capsule ends.

## 6. Matrices

Five heat steps, values centred in the cell and monospaced. Cells above 0.62 normalised take `bg` for the text, the rest `ink`. A 2pt `accent_deep` underline marks the best value in each row. Cell gap 2.5.

Row labels left, column labels centred above at 9.5pt `ink2`.

## 7. Ablation tables

First row is the baseline, each later row adds one mechanism. Add a Δ column against the first row. Mark the winning row with an `accent` bar on the left. Numeric columns right-aligned and monospaced.

```
| Variant | Params | GPU-hours | Success |
| Baseline BC | 0.31B | 42 | 31% |
| + larger backbone | 1.24B | 128 | 38% |
| + shared world model | 1.20B | 96 | 64% |
| + 4:1 sim mixing | *1.24B | *104 | *78% |
```

The footnote must say whether Δ is percentage points or relative percent, and what hardware the GPU-hours are wall-clock on.

## 8. Data sources

Point at files, do not paste numbers. First CSV column is the category or x tick; column names are the legend. For ±1σ add a `<name> std` column; for bounds add `<name> lo` and `<name> hi`.

```csv
step,Baseline BC,Baseline BC std,WAM-v1,WAM-v1 std
0,2,1,4,1
25k,9,3,22,5
```

After a re-run, rebuild; nothing in the slides needs touching.

## 9. Checks

1. Does the top tick reach the data maximum, bands included?
2. Are there axis labels and units?
3. Is dispersion drawn for multi-seed results?
4. Is there a reference line where there is a baseline, and does its label clear the series end labels?
5. Is there a conditions footnote?
6. Are values monospaced and right-aligned?
7. Does the accent colour appear in exactly one place?
8. Has every displayed number been rounded? (no `0.30000000000000004`)
