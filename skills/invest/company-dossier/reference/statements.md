# What to chart, and what breaks a series

A long series exists to show a **shape**. Choose the lines that make a shape legible and leave out the ones that only make the file longer.

## The charts, and what each is for

| Chart | Reads off it |
|---|---|
| **Revenue and operating income**, full history, absolute | Whether growth is steady, cyclical or step-shaped, and whether profit follows revenue or lags it |
| **Margins** — gross, operating, net, one axis, percent | Where the money goes. A margin series answers questions a revenue series cannot: pricing power, mix drift, operating leverage |
| **CFO against net income** | **The single most informative pair in the file.** Persistent CFO below NI means profit is not converting to cash, and the reason is always somewhere specific — receivables, inventory, capitalisation |
| **Capex and free cash flow** | What growth costs. Under the CFO/NI pair, same axis |
| **Diluted share count** | Dilution is invisible in every per-share metric and every total-return chart. A business that grew earnings 8% a year while issuing 6% a year is a different business |
| **Debt, cash, equity** | Plus the maturity wall where disclosed. Refinancing risk is a date, not a ratio |
| **ROIC or ROE** | **State the denominator.** They are not interchangeable, and the choice changes the answer for anything levered |

## Two lines that mislead if drawn without care

**Per-share anything, over a long window.** Buybacks and issuance mean the denominator moves. Draw the total and the share count, and let per-share be inferred.

**Anything indexed to 100 at the start.** The choice of start date is doing the arguing. If a series is indexed, the file states why that start was chosen.

## Restatements

Company facts carries **every version of every period**. Do not collapse to the most recent.

Detection is mechanical: group facts by `(concept, unit, start, end)`, and any group with more than one distinct `val` is a restatement. On one large filer that finds 252 of them, mostly on balance-sheet lines rather than on revenue.

Show them:

- Mark the point on the series
- On hover, both values and the accession number each came from
- If the restatement is large enough to change the shape, draw the superseded series behind the current one

Restatements cluster where the interesting things are: a standard adoption applied retrospectively, a discontinued operation pulled out of prior years, a segment reorganisation, an error correction. **The chart that hides them is the one a reader trusts most, which is the problem.**

## Segment re-definitions

Segments are re-cut more often than they are restated, and a chart across a re-cut compares different things.

The tell is in the filing rather than the data: a 10-K that reports prior years under new segment names, or an 8-K announcing a reorganisation. When the definition changes:

- **Break the series.** A gap, not a smooth line
- Say what changed, and which filing introduced it
- Where the company restated prior periods onto the new basis, use those and mark the point where the basis changes

The alternative — one continuous line across a definition change — is not a simplification, it is a false statement about a quantity.

## Fiscal calendars

A fiscal year ending in September is not a calendar year, and 52/53-week retail calendars produce a 14-week quarter roughly every five years, which shows up as growth that is not there.

Chart against the **fiscal period end**, label the axis with the fiscal year, and note the year-end month once at the top. Where a 53-week year occurs, mark it.

## What not to compute

**No ratios the filings do not support.** A margin needs both a numerator and a denominator from the same basis; if revenue is under one tag and cost of sales under an incompatible one for that year, the margin for that year is absent, not estimated.

**No forward numbers.** Not estimates, not guidance treated as data, not a trend extended past the last reported period. The dossier's window closes at the last filing.
