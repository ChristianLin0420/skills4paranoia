---
name: paper-teardown
description: >-
  Take a paper apart and rebuild it as one interactive HTML explainer: the claim in a sentence,
  every mechanism with its equation compiled and every symbol given a name, a shape and a
  provenance, the paper's own figures pulled from its source and each paired with a reading,
  original diagrams where the paper has none, and — if code exists — an end-to-end survey that
  RUNS the code and reports where it agrees with the paper and where it does not. Every claim is
  marked by how it was established: verified (observed at runtime), stated (the paper says so),
  or inferred (your reading). Third-party reimplementations are labelled as such on every claim
  they support. Use when reading an unfamiliar paper properly, preparing a reading-group or
  onboarding writeup, or deciding whether a method is worth building on. To map a repo you have
  already decided to work in, use codebase-onboarding; to chase a number that will not reproduce,
  use baseline-repro. Chinese triggers: 幫我讀這篇 paper / 這篇論文在講什麼 / 拆解這篇 arXiv /
  這篇的公式看不懂 / 幫我把這篇做成可以看的東西 / 這篇有沒有人實作過.
---

# paper-teardown

One paper in, one HTML explainer out — deep enough to build on, plain enough to read cold.

**Language.** Write in whatever language the user writes in. These instructions are English because
English is this repo's source language, not because the output must be. A Chinese user gets a
Chinese explainer down to the chrome, the figure readings and the symbol glosses — not an English
frame with Chinese paragraphs in it. Symbol names, tensor shapes, file paths and code stay as they
are in the source.

## The rule that makes this different

**Every symbol gets a home.** An equation is not explained until every symbol in it has three
things: a name in words, a shape, and a **provenance** — where it comes from.

| Provenance | Means |
|---|---|
| `input` | Arrives from outside the model |
| `learned` | A slow weight, trained and then frozen at inference |
| `fast` | Updated at test time — the thing that makes this paper this paper |
| `hyper` | A number someone chose; give its value and where it is stated |
| `derived` | Computed from the others in this same equation |
| `index` | A subscript that ranges; say over what |

Recitation is restating the equation in words. Explanation is being able to say, for each symbol,
what would break if it were wrong. **The symbol table is the deliverable**; the prose around it is
decoration. In the HTML the two are linked both ways: click a symbol in the equation and its row
lights, click a row and every occurrence in the equation lights.

## Three tiers, on every claim

Same tiers as `codebase-onboarding`, for the same reason — a reader must be able to tell what you
watched happen from what you read.

| Tier | Earned by | Shown as |
|---|---|---|
| `verified` | You ran something and observed it | solid border |
| `stated` | The paper or the code says it | plain |
| `inferred` | Your reading; the source does not say it | **dashed border** |

The tier attaches to the **claim**, not to the section. A method section is not uniformly `stated`
just because it came from the paper — the sentence "the gate keeps TTT small at initialisation" is
`stated`, and "at initialisation this layer therefore reproduces the pretrained computation" is
`inferred` until you run it.

**Never promote a tier for a claim you like.** The tiers are worth nothing the first time one is
stretched.

## Reading is not enough

If code exists, **run it**. The minimum bar is: import, construct, one forward pass, and one
assertion per mechanism the paper claims. That is usually an hour, and it is the difference between
a summary and a teardown — reading `O = attn + gate * ttt` in a source file tells you the shape of
the intent, not what the tensor does.

Write the probes as a script that prints its measurements, keep it, and ship its output in the
report. See `reference/code-survey.md`.

**When the code is not the authors'**, say so on every claim it supports, and never merge the two
into one story. Produce a **divergence table**: what the paper specifies, what this code does, and
whether the difference is cosmetic, a defensible choice, or a defect. A reimplementation is
evidence about the reimplementation. It is evidence about the paper only where they agree.

## The report

Front-loaded, same doctrine as the decks: the argument first, the evidence after.

1. **Header** — title, authors, affiliations, date, link, **licence**, and the tier legend.
2. **The claim** — one sentence, then the three numbers that carry the paper.
3. **The problem** — what was broken before, in the authors' framing and then in yours.
4. **The method** — one block per mechanism: compiled equation, symbol table, plain reading, the paper's figure.
5. **Diagrams** — the ones you drew, where the paper has none. Interactive where motion is the idea.
6. **Results** — every figure and table, each with a reading that says what to look at.
7. **The code** — the survey, the correspondence table, the divergences, the probe output.
8. **What the paper does not tell you** — unspecified protocol, absent ablations, numbers that do not reconcile, the authors' own stated limitations kept separate from yours.
9. **Sources** — every URL, commit SHA and accession, with the date fetched.

Section order in `reference/structure.md`. Visual tokens come from `html-design-system`.

## Figures come from the source, not from screenshots

Get the paper's **LaTeX source** where you can (`arxiv.org/e-print/<id>` is a tarball with the
original figure files and the actual equation source). It beats the PDF, and both beat OCR.

**Check the licence before you embed anything.** CC BY / CC0 → embed with attribution. Anything
else, including the default arXiv licence → **link, do not embed**. Full rules and the extraction
script in `reference/figures.md` and `reference/acquire.md`.

**Every figure carries a reading.** The paper's caption says what the figure is; your reading says
what to look at, what the comparison is, and what would change your mind. A figure with only its
original caption underneath has been pasted, not explained.

## Equations are compiled, not screenshotted

LaTeX → MathML at build time, with `temml`. No CDN, no JS at view time, no webfont, works offline,
selectable and searchable. `reference/math.md` has the pipeline and the fallbacks.

An image of an equation is a failure of this skill: it cannot be searched, cannot be linked to a
symbol table, and does not reflow.

## Input and output

**Input**: a paper — an arXiv ID or URL, a PDF, or a title. Optionally a code URL; if none is given,
look for one, and report what you found including that it is third-party.

**Output**: `index.<lang>.html` plus a sibling `assets/` directory holding the figures. Both language
versions share one `assets/`. A `probes.py` and its recorded output ship alongside when code was run.

Pass `--inline <assets-dir>` to `build.js` for a single self-contained file instead — for a report
that has to travel through a chat or an email, where a folder will not survive the trip.

**What it does not output**: a verdict on whether the paper is good, a novelty judgement, or a
recommendation to adopt. It explains and it marks its evidence. Reviewing is a different job.

## What this is not

- **Not a summary.** A summary is shorter than the paper. This is usually longer, and that is the point.
- **Not a replication.** It runs code to check correspondence, not to reproduce numbers — that is `baseline-repro`.
- **Not a repo map.** Once you have decided to work in the codebase, `codebase-onboarding` draws the data path.

## Files

- `reference/acquire.md` — getting the source, the licence check, what to do when there is only a PDF
- `reference/math.md` — LaTeX → MathML, the symbol table, writing a gloss
- `reference/figures.md` — vector vs raster, sizing, attribution, the reading
- `reference/code-survey.md` — surveying end to end, the probe script, the divergence table
- `reference/structure.md` — section order and what goes in each
- `templates/teardown.html` — the report
- `templates/extract_figures.py`, `templates/build.py` — the pipeline
- `examples/robottt/` — RoboTTT (arXiv 2607.15275), both languages, with a third-party code survey
