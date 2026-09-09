---
name: html-design-system
description: >-
  The shared visual and structural specification for every interactive HTML deliverable in this
  collection — the colour tokens, two layout modes (dashboard for scanning and comparing,
  long-read for reading front to back), the type scale for each, the primitives (page frame,
  banner, section header, tag, evidence mark, warn block, mono field grid, collapsed roll-up,
  provenance footer), and the conventions that make one report look like the next. Read this
  before writing or reviewing any single-file HTML report, so a third deliverable does not
  become a third stylesheet. Owns tokens and primitives only; each skill keeps its own components. For
  slides rather than HTML, use deck-design-system. Chinese triggers: html 報告的樣式 / 這些輸出風格要統一 /
  報告配色 / 我要新做一個 html 產出 / 這兩份 html 長得不一樣.
---

# html-design-system

The specification every HTML deliverable in this collection is built against, so that a reader who has seen one can read the next without relearning it.

**Language.** This is a specification and is in English because English is this repo's source language. Report text follows the user's language; both font stacks name a CJK face for exactly that reason.

## What it owns, and what it does not

| | |
|---|---|
| **Owns** | Colour tokens, the two layout modes and the type scale for each, the page frame, and a small set of primitives that recur in every report |
| **Does not own** | A skill's own components. `codebase-onboarding` has lanes and span bars; `vla-code-review` has findings and precedents; a company dossier has statement tables. Forcing those into shared classes would be a worse design, not a more consistent one |

The line is: **if two skills would name the same thing differently, it belongs here.** That is the failure this exists to prevent — `codebase-onboarding` called the alarm colour `--warn` and `vla-code-review` called it `--block`, with identical values, which is one concept and two vocabularies.

## Two modes

A reader either **scans and compares** or **reads front to back**, and one page shape cannot
serve both. The tokens, the evidence conventions and the primitives are shared; the page
surface, the column model, the type scale and how an item is bounded are not.

| | Dashboard | Long-read |
|---|---|---|
| Reader | scanning, comparing, looking something up | reading once, in order |
| Surface | `--bg` grey, cards float on it | `--surface` paper, nothing floats |
| Columns | content + sticky detail panel | one measure + a navigation rail |
| An item is bounded by | a card | a hairline rule and space |
| Base type | 15px / 1.62 | 16px / 1.85 |
| Built by | `codebase-onboarding`, `vla-code-review`, `company-dossier` | `paper-teardown` |

**Pick by what the reader does, not by how much content there is.** A company dossier is very
long and is still a dashboard, because nobody reads a filing history start to finish. Full
specification, including the three rules that make the long-read work, in `reference/modes.md`.

## Non-negotiables

Every HTML deliverable in this collection is:

- **One file.** No build step, no bundler, no local assets. It opens from disk, and it still opens in two years. `paper-teardown` is the one exception, states it, and ships an `--inline` build that collapses back to a single file — see `reference/modes.md`
- **Network-optional.** A webfont `<link>` is the only external reference, and the stacks degrade to system faces without it
- **Bilingual-capable.** Both the sans and the mono stack name a CJK face. A monospace stack without one renders Chinese as tofu
- **Honest about evidence.** If a number or an edge was not verified, the file says so where the reader cannot miss it — a banner at the top, not a footnote

## Files

- `reference/modes.md` — the two layout modes, when each applies, and what they share
- `reference/tokens.md` — the canonical tokens, a type scale per mode, and the names that are no longer used
- `reference/primitives.md` — the recurring pieces, with the CSS to paste
- `templates/base.html` — an empty **dashboard**: tokens, primitives, content column and sticky panel
- `templates/longread.html` — an empty **long-read**: masthead, hero, rail, sections, exhibits

## Built against this

| Deliverable | Mode |
|---|---|
| `codebase-onboarding/templates/map.html` | dashboard |
| `vla-code-review/templates/report.html` | dashboard |
| `company-dossier/templates/dossier.html` | dashboard |
| `paper-teardown/templates/teardown.html` | long-read |

When one of them needs something the others will need too, it comes here first. When one needs
something only it will ever need, that is a sign it belongs to that skill — not that the system
needs a third mode.
