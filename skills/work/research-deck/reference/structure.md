# Input format and the front three pages

One markdown file is one deck. After the YAML front-matter, every page opens with a single HTML comment naming its layout and attributes.

```
<!-- E11 curves solves=Q1 eyebrow="sample efficiency" source="runs/2026-08/curves.csv" -->
```

## Common syntax

| markdown | Meaning |
|---|---|
| `# text` | Title. A conclusion, not a topic |
| `## text` | Subtitle |
| `> text` | Emphasis line, depending on the layout |
| `- text` | Bullet; multiple fields separated by `\|` |
| `- observation \| why it matters` | Analysis on a figure or table page; two or three required |
| `~ text` | Conditions footnote: n, seeds, hardware, method of measurement |
| `![caption](path)` | Image, path relative to deck.md |
| ` ```chart ` | Chart YAML, see `research-figures` |
| ` ```notes ` | Speaker notes |
| A pipe table | Table data |

Common attributes: `solves=Q1` (required on evidence pages), `eyebrow="…"`, `source="…"`, `footnote="…"`, `analysis=right|below`.

## Front-matter

```yaml
title: Meridian-1 quarterly review
running: Meridian-1 · Q3        # short name, top right
subtitle: Freeze the architecture, move compute to data
author: Your Name
team: Robotics Learning
date: 2026-09-05
lang: en                        # en | zh
theme: slate-blue               # slate-blue | linen | mist
typeface: plex                  # plex | plex-full | inter | system
footer: Internal
contact: you@example.com
```

## P1 — problem

```markdown
<!-- P1 problem -->
# The big problem in one sentence
- Q1 | mid-level problem | obstacle | obstacle | obstacle
- Q2 | mid-level problem | obstacle | obstacle
- Q3 | mid-level problem | obstacle | obstacle
> What happens if it stays unsolved (one line)
```

- The big problem gets two lines at most; longer means it has not converged.
- Two to four mid-level problems, labelled `Q1`…`Q4` in the first field; numbering is automatic if omitted.
- Two or three sub-problems each, and they must be measurable, falsifiable obstacles.
- Layout: the big problem on top, a `rule` beneath, then equal columns; each column has a 2pt bar (first `accent`, rest `ladder[2]`), the Q label at 9.5pt monospace `accent_deep`, the mid-level problem at 12.5pt `ink`, and sub-problems at 11pt `ink2` each above a `rule_soft`.

## P2 — solution

```markdown
<!-- P2 solution -->
# The mechanism, in one sentence
![architecture caption](figures/arch.png)
- Q1 | the mechanism addressing it | key number
- Q2 | the mechanism addressing it | key number
- Q3 | the mechanism addressing it | key number
~ conditions footnote
```

- Every Q declared on P1 must have a row. No orphan Qs.
- The third field's key number is monospaced `accent_deep`, e.g. `trainable params 11%, demos 4200 → 510`.
- With an image, the left takes 42% and the rows take the right; without one, the rows take the full width.
- Layout: a hairline above each row, the Q label at a fixed width of 32, the mechanism at 12.5pt, the key number at 11pt monospace.

## P3 — results

```markdown
<!-- P3 results -->
# The result in one sentence, including what is not solved
## Subtitle states the key precondition of the evaluation
| Method | Metric A | Metric B | Metric C |
| --- | --- | --- | --- |
| Baseline | … | … | … |
| Ours | *… | *… | *… |
```chart
type: line
data: data/curves.csv
band: std
```
~ conditions footnote
```

- **It must be a table**, not a few large numbers. Methods as rows, metrics as columns, the best method's cells prefixed `*`.
- The table must include the column that is not solved. Listing only wins turns it into promotion.
- With a figure the table takes 56% and the figure the rest; without one the table takes the full width.
- The subtitle states the key precondition, e.g. "one checkpoint throughout, no per-task finetuning".

## Evidence pages

Everything from page 4 on is evidence; layouts in `layouts.md`. Place the user's own figures with `E20` (single), `E21` (pair), `E13` (frames), `E14` (figure plus notes) or `E15` (bleed); redraw figures whose underlying data exists with `E06` / `E11` / `E12` / `E17` / `E19` instead. Every page declares `solves=Qn`, except the section page `E01`.

There is no divider page and no closing page. P3 runs straight into the first piece of evidence, and the last page is the last piece of evidence.

## What not to do

- No "so here is what I need you to decide" page. A research deck shows the problem, the solution and the result; limits go in a footnote on the results or an evidence page.
- No "background", "related work" or "motivation" page. What matters is already in P1's sub-problems.
- No page carrying only three or four large numbers.
- No page carrying a single sentence.
- No mixing languages, palettes or typefaces within one deck.
