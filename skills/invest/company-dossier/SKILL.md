---
name: company-dossier
description: >-
  Build one interactive HTML dossier on a company from its own filings: three sentences that
  say what it sells, how the money arrives and what decides whether it does well; the operating
  and cash-flow history charted as far back as the filings go; the balance sheet; share count;
  and what the compensation plan actually pays management to maximise. Every figure carries the
  accession number it came from, restatements are shown rather than silently overwritten by the
  latest version, and segment re-definitions are marked as breaks in the series. Reads primary
  sources — SEC XBRL company facts, 10-K, 20-F, DEF 14A — not summaries. Presents; it does not
  value, rate or recommend. Use to get from nothing to grounded on a business. Chinese triggers:
  幫我研究這間公司 / 這間公司歷年財報 / 我想看這家的長期數字 / 管理層是誰 / 幫我做一份公司分析.
---

# company-dossier

Everything the filings say about a business, in one file, with every number traceable to the document it came from.

**Language.** Write in whatever language the user writes in. These instructions are English because English is this repo's source language; the dossier's own text follows the user. Both font stacks name a CJK face.

## What this is not

**Not advice, and not a valuation.** It does not rate the business, judge the price, or suggest a position. It reads primary sources and lays out what they say, which is the work that has to happen before a judgement is worth anything. The judgement is yours — and `thesis-prereg` is where it goes next.

## The hard rule

> **A figure without an accession number does not go in the file.**

The failure mode of an agent asked for a company's history is producing plausible numbers. Every value in the dossier carries the filing it was read from — accession number, form type, fiscal period, and the XBRL tag where there is one. A figure that cannot be sourced is either omitted or rendered with the `inferred` mark and said out loud; it is never shown as though it were read.

This is the same discipline as `codebase-onboarding`'s verification banner, for the same reason: **a plausible fiction is worse than a gap, because you will act on it.**

## "From founding to now" is not available. Say what is.

| Period | What exists | Mark |
|---|---|---|
| XBRL era → now | Company facts: structured, machine-readable, and carrying every version of every period | `verified` |
| first filing → XBRL | Filings exist as documents; figures must be read out of them | `stated`, with a page or exhibit reference |
| before the first filing | **Nothing public.** Pre-IPO financials are not disclosed | absent, and the coverage banner says so |

**Do not assume where the XBRL era starts — compute it.** The mandate phased in around 2009, but later filings tag their comparative prior periods too, so the earliest period *end* in company facts reaches further back than the earliest *filing*. Checked on one large filer it reaches 2006. Take the minimum `end` across all facts and report that.

The dossier opens with a **coverage banner** naming the earliest fiscal year available and by which route. A chart that starts in 2010 because that is where the data starts must not look like a business that started in 2010.

## The three sentences

Before any chart. Three sentences, each answering one question, in plain language and without adjectives:

1. **What does it sell, and to whom?**
2. **How does the money actually arrive?** The unit of revenue, who signs the cheque, and how often. Recurring, per-unit, per-seat, per-transaction, cost-plus, take-rate.
3. **What one variable decides whether it does well?** Volume, price, utilisation, attach rate, credit losses, the cycle.

Most descriptions fail at the second. "It is a leading provider of solutions" answers none of the three and is the thing this section exists to forbid. If the filings do not support a clean answer, write the question and say so — an unanswerable second sentence is itself the most useful line in the dossier.

## What goes in

| Section | Why it, and not something else |
|---|---|
| Three sentences | Above |
| Operating history | Revenue and operating income as far back as the filings go. The **shape** over a decade, not the last three years |
| Margins | Gross, operating, net, on one axis. A margin series answers questions a revenue series cannot |
| Cash | Cash from operations against net income. **The gap between them is the tell**; capex and free cash flow beneath |
| Share count | Diluted shares outstanding over time. Dilution is invisible in every per-share metric and in every total-return chart |
| Balance sheet | Debt, cash, equity. Plus the maturity wall if one is disclosed |
| Returns | ROIC or ROE, with the denominator stated — the two are not interchangeable and the choice changes the answer |
| Restatements | Where a period was later reported differently, both versions and the filing that changed it |
| Segments | With re-definitions marked as breaks. A segment chart across a re-segmentation compares different things |
| People | Named executives, tenure, and **what the compensation plan pays them to maximise** — see `reference/people.md` |

Detail on each: `reference/statements.md`. Sources and their limits: `reference/sources.md`.

## Restatements are shown, not resolved

XBRL company facts returns **every version of every period** a company has filed, tagged with the form and fiscal year it came from. Most tools take the most recent and move on.

Do not. Where a period's reported figure changed, show both, name the filing that changed it, and mark the series. **A clean series that has been quietly overwritten looks exactly like a clean series that was always clean.**

This is not a rare event. Scanning one large filer's company facts turns up **252 concept-periods carrying more than one reported value** — and they are not on the revenue line, which is where you would look. They are on balance-sheet items: accounts payable for one fiscal year end appears as both $44.2bn and $49.0bn, from two different filings. Restatements cluster around standard adoptions, discontinued operations, segment reorganisations and errors, all of which are things worth knowing about.

## Input and output

**Input**: a company — a name, a ticker or a CIK. Optionally a period of interest.

**Output**: `dossier-<ticker>-<date>.html`, one self-contained file, built on `html-design-system`. Interactive: hover a point for the filing behind it, toggle a series, switch absolute against margin, expand a restatement.

**Not output**: a valuation, a price target, a rating, a position size.

## Pairs with

- **`thesis-prereg`** — the dossier is what you read before writing a thesis; the thesis is where judgement enters
- **`html-design-system`** — owns the tokens and primitives this template is built on
- **`grill-deeper`** — run it on the three sentences. If the second one cannot survive questioning, the business is not understood yet

## Files

- `reference/sources.md` — the endpoints, what each returns, coverage limits, and the request rules
- `reference/statements.md` — what to chart, restatements, segment breaks
- `reference/people.md` — reading the proxy: what the plan pays for
- `templates/dossier.html` — the deliverable
