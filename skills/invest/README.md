# invest

Skills for holding a position you can defend. Unlike `research/`, which is about doing the work, and `work/`, which is about communicating it, these are about **not fooling yourself with your own money**.

> **Nothing here is investment advice.** These skills do not value anything, judge whether a price is attractive, size a position, or say what to buy or sell. They take reasoning you already hold and put it into a form that can be wrong. Every judgement stays yours, and none of this substitutes for a licensed adviser.
>
> Every worked example is **mock** — the companies do not exist and the figures are invented.

| Skill | What it covers | When |
|---|---|---|
| [`company-dossier`](company-dossier) | Everything the filings say, in one interactive HTML file, every figure carrying its accession number | Getting from nothing to grounded on a business |
| [`thesis-prereg`](thesis-prereg) | Freeze the thesis, its falsifiers and both exits before buying; detect drift at review | Before opening a position, and at every scheduled review |
| `allocation-jobs` | *(next)* Every holding states its job and what would count as failing at it | When the shape of the portfolio is the question |
| `crisis-indicators` | *(next)* What the historical early-warning indicators are, and how often each cried wolf | When the backdrop, not a position, is the worry |

## Why this exists when a hundred finance skills already do

The public catalogues are two shapes. [Anthropic's own financial-services repo](https://github.com/anthropics/financial-services) is institutional analyst work product — DCF, LBO, comps, IC memos — and states plainly that its outputs are drafts staged for a qualified professional's sign-off. [tradermonty](https://github.com/tradermonty/claude-trading-skills) and [agiprolabs](https://github.com/agiprolabs/claude-trading-skills) are personal-investor skills that are largely **screeners**: VCP, CANSLIM, momentum bursts, position sizers, most of them wired to FMP, Alpaca or FINVIZ Elite.

Neither shape is the discipline layer for someone holding for years. And a screener's output — a list of candidates — was never the binding constraint. **What separates outcomes is whether a thesis can be wrong, and whether you act when it breaks.** That is a writing and reviewing problem, it needs no market-data subscription, and nothing in the catalogues does it.

Same doctrine as the rest of this repo: pure markdown, no API keys, and the skill's job is to make you state something falsifiable rather than to hand you an answer.

## company-dossier

One interactive HTML file per company, built from primary sources: SEC XBRL company facts, the 10-K or 20-F, the DEF 14A. It presents; it does not value, rate or recommend.

### Three sentences before any chart

1. What does it sell, and to whom?
2. **How does the money actually arrive** — the unit of revenue, who signs the cheque, how often?
3. What one variable decides whether it does well?

Most descriptions fail at the second, and "a leading provider of solutions" answers none of the three. Where the filings do not support a clean answer, the dossier writes the question and says so — an unanswerable second sentence is the most useful line in the file.

### A figure without an accession number does not go in

The failure mode of an agent asked for a company's history is producing plausible numbers. Every value carries the filing it came from — accession, form, fiscal period, XBRL tag. Same discipline as `codebase-onboarding`'s verification banner, and for the same reason: a plausible fiction is worse than a gap, because you will act on it.

### "From founding to now" is not available, and the file says which years are

Structured XBRL, then documents that must be read by hand, then nothing before the first filing — pre-IPO financials are not public. **Do not assume where XBRL starts; compute it.** The mandate phased in around 2009, but later filings tag their comparative prior years too; checked on one large filer the earliest period end reaches 2006.

### Restatements are shown, not resolved

Company facts carries every version of every period, and most tools take the latest and move on. Scanning one large filer's facts finds **252 concept-periods carrying more than one reported value** — not on revenue, where you would look, but on balance-sheet lines: accounts payable for one year end appearing as both $44.2bn and $49.0bn from two different filings. A clean series that has been quietly overwritten looks exactly like a clean series that was always clean.

Segment re-definitions get the same treatment: the series breaks, because a line drawn across a re-cut is comparing different things.

### What the plan pays for

The people section is not biographies. It is the compensation plan and one question: **if it paid out at maximum, what would management have had to do?** Adjusted EBITDA excluding acquisitions pays for acquiring; revenue growth without a return constraint pays for buying revenue. These are instructions, and they are followed. The dossier states them and does not judge them.

## thesis-prereg

`experiment-prereg` for money. Before buying: why this is mispriced **and why the mispricing persists**, the two to four claims the thesis rests on, the specific observation that would falsify each, the horizon, both exits, and what would make you add.

### The rule that does the most work

> **The falsification horizon must be shorter than the holding horizon.**

If knowing you were wrong takes five years and you are holding for three, the thesis cannot resolve inside the time you are giving it, and the exit will happen on price or on fatigue instead. The fix is a **nearer observable**, not a longer horizon — and in the worked example this rule fires on the first pass and forces exactly that substitution, trading stronger evidence for evidence that arrives in time.

It is the direct sibling of the minimum detectable effect: both ask whether what you are committing to can resolve within the budget you are giving it.

### Drift is the thing being detected

The document is dated and never edited; reviews append. At each review you write **why you hold it today before rereading the original** — and if that reason is not in the original, it is not an update. It is a new, untested thesis wearing an old one's clothes, and it shows up precisely when the original is failing, because that is when a replacement reason is most needed.

Two honest responses, and "note it and carry on" is not one: give the new reason its own dated document, or close the position.

### Reviews are scheduled by the horizon, never by price

A price move is not information about your thesis; it is information about what other people think. Wiring reviews to price is how a portfolio ends up managed by whichever holding is most volatile.

### The worked pair

[`input.zh.md`](thesis-prereg/examples/input.zh.md) is the untidy request — a distributor at 7× with a fast-growing service segment nobody discloses — and it ends with **"what do you think of the thesis?"**. [`filled-thesis.zh.md`](thesis-prereg/examples/filled-thesis.zh.md) is what comes back, and it **does not answer that question**. It answers a different one: what would have to be true, and how would you know if it were not.

That substitution is the skill. English pair: [`input.en.md`](thesis-prereg/examples/input.en.md), [`filled-thesis.en.md`](thesis-prereg/examples/filled-thesis.en.md).
