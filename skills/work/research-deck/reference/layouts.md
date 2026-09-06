# Evidence layout catalogue

The layouts available from page 4 on. Every page must declare `solves=Qn` (except the section page `E01`). Do not use the same layout on two consecutive pages.

**There is no divider page, no closing page, no single-statement page and no pull quote.** A sentence is not worth a slide; evidence pages announce themselves with `solves=`; and the last page should be the last piece of evidence.

## Choosing

Look at the shape of the data first. Preference runs top to bottom.

| Shape of the data | First choice | Second | Not |
|---|---|---|---|
| Several lines over training steps | `E11` curves | `E06` | A table |
| Task by method scores | `E12` matrix | `E10` | Bullets |
| Two related quantities | `E17` panels | Two pages | Overlaid on one axis |
| Ablations, one mechanism at a time | `E19` ablation | `E10` | `E03` |
| Hyperparameters, hardware, data specs | `E18` setup | `E10` | `E03` |
| A few quantities compared | `E06` chart | `E07` | `E03` |
| Proportions or ranking (≤6) | `E07` chart-side | `E06` | Pie (no such layout) |
| Multi-column specification comparison | `E10` table | `E04` | `E03` |
| A trade-off between two options | `E04` two-col | `E10` | `E03` |
| Schedule or phases | `E09` timeline | `E10` | `E03` |
| One supplied figure | `E20` figure | `E15` | — |
| Two figures side by side | `E21` pair | `E17` | Overlaid |
| Frame sequences, rollouts | `E13` filmstrip | `E21` | — |
| Architecture, pipeline | `E14` architecture | `E20` | — |

Reaching for `E03 bullets` usually means you have not turned it into data yet — check first whether it can become a figure or a table.

## The layouts

| Code | Alias | Purpose | Consumes | Cap |
|---|---|---|---|---|
| `F0` | cover | Cover, optional | front-matter | — |
| `E01` | section | Section break with a large numeral | `#` `##`, attribute `index=01` | — |
| `E03` | bullets | Bullets | `#` `##`, `-` (`lead \| detail`) | 5 |
| `E04` | two-col | Side-by-side comparison | `#`, two `-` (`heading \| line \| line …`) | 2 × 5 |
| `E06` | chart-full | Full-width chart | `#` `##`, ```chart | — |
| `E07` | chart-side | Text left, chart right | `#`, body paragraphs, ```chart | 4 paragraphs |
| `E09` | timeline | Timeline | `#`, `-` (`stage \| description`) | 5 stops |
| `E10` | table | Table | `#` `##`, a pipe table. A `*` prefix takes the accent colour | 6 rows suggested |
| `E11` | curves | Training curves; `E06` locked to `type: line` | as `E06` | 5 lines |
| `E12` | matrix | Success matrix; `E06` locked to `type: matrix` | as `E06` | — |
| `E13` | filmstrip | Frame strip | `#`, several `![caption](path)` | 6 frames |
| `E14` | architecture | Figure plus notes on the right | `#`, one `![]()`, body paragraphs | 4 notes |
| `E15` | image-full | Bleed image with a title band | one `![]()`, `#` `##` | — |
| `E17` | panels | 2–4 charts sharing one title | `#`, 2–4 ```chart blocks (each may carry `title:`) | 4 |
| `E18` | setup | Experimental setup, values monospaced and right-aligned | `#`, `-` (`group \| key=value \| …`) | 4 × 8 |
| `E19` | ablation | Ablation table, adds a Δ column and marks the winner | as `E10` plus `delta=<column>` `best=max\|min` | 6 rows suggested |
| `E20` | figure | One supplied figure, filling the content area | `#` `##`, one `![caption](path)`, `~` footnote | 1 |
| `E21` | figure-pair | Two side by side, each captioned | `#`, two `![caption](path)`, `~` footnote | 2 |

There is no "wall of numbers" layout. Results always go in a table.

## Redraw or place

Decide figure by figure during the interview (`intake.md` group 2); do not assume.

**Redraw if the underlying data exists** (`E06` / `E11` / `E12` / `E17` / `E19`), and colour, type and axes match the rest.
**Place the original if it does not** (`E20` / `E21` / `E13` / `E14` / `E15`); the style will differ but it is irreplaceable.

Statistical figures can almost always be redrawn as long as the CSV or log can be found. Architecture figures, pipelines, rollout frames, on-robot capture and screenshots can only be placed.

## Figures and tables both need analysis

`E06` `E10` `E11` `E12` `E17` `E19` `E20` `E21` all need two or three analysis lines written as `-` bullets, in the form `observation | why it matters`. Missing them fails the structure check. `E07` uses its left-hand body paragraphs as the analysis, equally required.

**Tables need analysis as much as figures do.** A latency breakdown sitting there tells the reader every cell but not which cell to look at.

The title states the conclusion; the analysis states how the figure or table gets you there. If you are unsure what the analysis should be, go back and ask.

### Right or below

Decided by **how much horizontal space the figure actually needs**, not fixed:

| On the right (figure keeps its height, takes 60% width) | Below (figure keeps its width, takes 62% height) |
|---|---|
| Five or fewer horizontal slots: three bars, a horizontal bar chart, a matrix of ≤5 columns | More than five: a many-point training curve, a wide matrix |
| A table of four columns or fewer | More than four columns |
| One placed figure `E20` | Multi-panel `E17`, pairs `E21` |

Counting slots: a line plot counts x ticks, a bar chart counts bars, a matrix counts columns, a horizontal bar chart always counts 1, a table counts columns.

**A three-bar chart does not need 848pt of width**; forcing the analysis underneath only flattens it. Conversely, a nine-point curve squeezed into 60% width turns into a smear.

Override the automatic choice with `analysis=right` or `analysis=below` on the directive.

Analysis spec: stacked vertically when on the right, with a `rule_soft` between entries; equal columns when below, under a `rule`. Either way a 14pt `series` bar on top, observation at 11pt `ink`, detail at 9.5pt `ink2`.

## Geometry

All layouts share the grid (see `deck-design-system`): content from y 88 to 446, side margins 56, content width 848.

- **Title**: 21pt from y=88, two lines maximum, shrinking to 16pt if it does not fit. Subtitle 13.5pt beneath. Content begins 12 below the title's bottom.
- **E06 / E10 / E11 / E12 / E19 / E20**: with the analysis on the right, the figure or table takes `CW × 0.60` with a 30 gap and the analysis column takes the rest at full height; below, the figure takes `(BODY_BOT − y) × 0.62` and the analysis sits underneath in equal columns.
- **E07**: text on the left at 32%, gap 34, chart on the right; the chart starts at y=88 rather than below the title.
- **E17**: two side by side, or 2×2 for four, column gap 26. Each chart's `title:` renders at 11pt `ink` at the top of its own box, taking 19pt.
- **E18**: equal columns, a 2pt bar and an 11pt `accent_deep` heading on each; rows 24pt tall, key at 9.5pt `ink3` left, value at 11pt monospace `ink` right, a `rule_soft` under each.
- **E20**: figure fills (56, y, 848, 446−y); with a caption the height drops 17 and the caption sits below at 9.5pt `ink3`.
- **E21**: two equal columns, gap 24; with captions the height drops 28.
- **E13**: equal cells, gap 10, height `min(column width × 0.7, available − 26)`, captions below at 9.5pt.
- **E14**: with notes the figure takes 76% and the notes column 24%, gap 28; each note has a 16pt `series` bar above it.

## The chart block

```yaml
type: line          # bar | bar-h | line | matrix
data: data/x.csv    # or labels / values / series inline
unit: "%"
xlabel: env steps
title: Success vs data volume     # panel title inside E17
note: "rollouts=100/task"         # a conditions line hugging the figure
band: std                         # reads "<name> std" for ±1σ; or bounds for lo/hi
baseline: {value: 56, label: "Diffusion baseline plateau"}
delta: pp           # bar / bar-h: difference against the first, pp or pct
delta_base: 0       # index of the reference
highlight: 2        # which index to emphasise
max: 100            # fix the axis top for cross-page comparison
mark_best: true     # matrix: underline the best in each row
```

Details in `research-figures`.
