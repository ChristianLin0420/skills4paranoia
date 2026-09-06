# work

Communication and record-keeping. Unlike `research/`, these **follow you to a new job**.

| Skill | What it covers |
|---|---|
| [`grill-deeper`](grill-deeper) | Interrogates your plan, and accumulates an understanding of your work |
| [`research-deck`](research-deck) + [`deck-design-system`](deck-design-system) + [`research-figures`](research-figures) | Research decks |

## grill-deeper

Interrogates until every branch of the design tree has been visited, then remembers what the session taught it.

Questions are scheduled on a **frontier**: the ring whose prerequisites are settled, asked one round at a time with a recommended answer attached to each. The mechanism comes from `grilling` in [mattpocock/skills](https://github.com/mattpocock/skills).

What this adds is **memory**, and it meshes with the frontier rather than sitting beside it: **a known fact is a settled node**, so the first round's frontier starts further out. With no store, round one asks how your evaluation works; with one, round one asks whether the perturbation stays at last time's ±3cm. Same round, two levels deeper.

The global layer separately accumulates **the categories of question you go vague on**. After five sessions it knows you get vague every time evaluation protocol comes up, puts that question first in the round, and **gives it no recommended answer** — supplying one is how you skate past it.

Two layers: project facts in `<project>/.grill/` (gitignored), your blind-spot profile in `~/.claude/grill/profile.md`. Blind spots follow the person; project facts do not.

The decision log lives here too: decision, alternative considered, what evidence would reverse it, date. The reversal condition is also how a decision expires — age does not stale one, its condition coming true does.

## The research-deck trio

Three skills that reference each other and can also be used alone. Use `research-figures` on its own to plot one paper figure; use `deck-design-system` on its own to review an existing deck's appearance.

| Skill | What it covers |
|---|---|
| [`research-deck`](research-deck) | Structure and process: problem → solution → results, and how evidence attaches |
| [`deck-design-system`](deck-design-system) | Palette, type scale, grid, typeface, layout geometry |
| [`research-figures`](research-figures) | Curves with error bands, matrices, ablation deltas, reference lines, conditions footnotes |

### The claim

**The front three pages carry the whole argument; everything after them is evidence.**

1. **Problem** — one big problem, split into 2–4 mid-level problems (Q1…Q4), each with 2–3 measurable technical obstacles
2. **Solution** — the mechanism in a sentence, then one row per Q
3. **Results** — a method-by-metric table that **keeps the cell that is not solved**, plus one key figure

Every page from the fourth on declares `solves=Qn`. Anything attaching to no Q is deleted.

No "here is what I need you to decide" page — that is an internal proposal, not a research deck. No wall of numbers — results go in a table, and showing only wins is promotion.

### Density

One page carries one complete piece of evidence: the figure, the numbers, and the conditions they were measured under. Every figure and table needs a `~ ` conditions footnote and two or three analysis lines; multiple seeds need dispersion drawn; a baseline needs a reference line; a comparison needs a delta; numbers are monospaced.

Where the analysis sits is decided by how much width the figure needs — few horizontal slots put it on the right so the figure keeps its height, many put it underneath so it keeps its width.

### Examples

`research-deck/examples/` has complete decks in both English and Chinese covering every layout, with the CSVs in `data/`. Starting from an example beats starting from blank.
