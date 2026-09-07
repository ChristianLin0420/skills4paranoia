# Sources

All free, no key, no account. Everything below was exercised against a live endpoint; where a number appears it was measured, not assumed.

## Request rules

SEC requires a declared `User-Agent` carrying a real contact. Requests without one are refused.

```
User-Agent: <project or name> <email>
```

Keep to ten requests a second. `companyfacts` for a large filer is a single ~4 MB call, so one company is a handful of requests, not thousands.

## The endpoints

| What | URL | Returns |
|---|---|---|
| Filing history | `https://data.sec.gov/submissions/CIK##########.json` | Name, former names, tickers, exchange, SIC, and the most recent 1,000 filings. **Older ones are in referenced files** — `filings.files[].name`, fetched from the same host |
| One concept | `https://data.sec.gov/api/xbrl/companyconcept/CIK##########/us-gaap/<Tag>.json` | Every fact for one tag, across every filing that reported it |
| Everything | `https://data.sec.gov/api/xbrl/companyfacts/CIK##########.json` | Every tag at once. ~4 MB and 500 concepts for a large filer — usually the right call |
| Cross-company | `https://data.sec.gov/api/xbrl/frames/us-gaap/<Tag>/USD/CY2024.json` | One fact per company for a period. For peer context, not for a single-company dossier |

CIK is zero-padded to ten digits. Non-custom taxonomies only: `us-gaap`, `ifrs-full`, `dei`, `srt`. A company's bespoke extension tags are not in these APIs — which matters, because that is often where segment detail lives.

## The fact record

Each fact carries what you need for provenance, and it is why the hard rule is affordable:

```
val    start / end     the value and the period it covers
fy fp  form            the fiscal year, period and form it was REPORTED in — not the period it describes
accn                   accession number: the citation
filed  frame           filing date; frame is the calendrical bucket, absent where it does not align
```

`fy`/`fp` are the *reporting* filing, `start`/`end` are the *reported* period. Confusing them is how a 2024 10-K's comparative 2022 figure gets plotted as 2024.

## Three things that break a naive pull

**1. The tag for one line item changes over time.** On one large filer, revenue is `Revenues` through FY2018 and `RevenueFromContractWithCustomerExcludingAssessedTax` from FY2019 — the ASC 606 adoption. Query one concept and the series has a hole exactly where the accounting changed.

Build each line from a **ranked list of candidate tags**, take the first that has a value for the period, and record which tag was used per point. A series stitched from two tags is fine; a series stitched silently is not.

**2. The same period appears many times with the same value.** A 10-K shows three years, so a given period is reported by several filings. Deduplicate on `(start, end, val)`, not on `end`.

**3. The same period sometimes appears with *different* values.** That is a restatement, and it is not rare — 252 concept-periods on one large filer. Do not collapse to the newest. See `statements.md`.

## Beyond XBRL

| Need | Where |
|---|---|
| Narrative, risk factors, segment discussion | The 10-K or 20-F document itself, from the accession number |
| Executives, compensation, ownership | **DEF 14A** proxy. Not in XBRL — see `people.md` |
| Pre-XBRL figures | The old filing documents. Read out by hand, marked `stated`, with an exhibit or page reference |
| Foreign private issuers | 20-F and 6-K rather than 10-K and 8-K; may report under IFRS, so the taxonomy is `ifrs-full` |

## When the company is not a US filer

There is no equivalent free structured source. The dossier can still be built from annual reports, but every figure is `stated`, the coverage banner says so, and the restatement check is not available. **Say which of these applies at the top rather than producing a file that looks the same either way.**
