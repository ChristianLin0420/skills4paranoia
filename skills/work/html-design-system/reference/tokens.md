# Tokens

Paste this block verbatim. It is the same palette as `deck-design-system`, which owns the slide side; the values are shared so a deck and a report from the same work do not disagree.

```css
:root{
  /* surface */
  --bg:#F1F2F3;        /* page */
  --surface:#FAFBFB;   /* raised: cards, side panels */
  --sunk:#F6F7F8;      /* recessed: a full-width bar inside a card */

  /* ink */
  --ink:#14171A;       /* body */
  --ink2:#5F656B;      /* secondary */
  --ink3:#8A9096;      /* labels, captions, disabled */

  /* rules */
  --rule:#DCE0E3;
  --rule-soft:#E8EBED;

  /* the one accent */
  --accent:#3A6183;
  --accent-deep:#27435C;
  --accent-soft:#DBE4EB;
  --accent-wash:#EAF0F4;

  /* the one alarm */
  --warn:#8C4A3C;
  --warn-soft:#EFE3E0;

  /* proper nouns — model names, tickers, entity names */
  --name:#54547A;
  --name-soft:#E6E6EE;

  --sans:'IBM Plex Sans','Noto Sans TC',sans-serif;
  --mono:'IBM Plex Mono','Noto Sans TC',Menlo,monospace;
}
```

```html
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&family=Noto+Sans+TC:wght@400;500&display=swap">
```

## Rules

**One accent, one alarm.** A second accent colour is almost always a component that wanted a shape instead. `--name` is the exception and is deliberately narrow: proper nouns only — a model, a ticker, an entity — because those are what a reader scans for on a first pass, and colouring anything else makes them stop working.

**`--warn` is the alarm. Not `--block`, not `--danger`, not `--risk`.** `vla-code-review` used `--block` with the same values before this file existed; one concept, two names, and neither file knew about the other.

**CJK in both stacks.** `Noto Sans TC` is not monospaced and a mixed Latin/CJK line loses column alignment. Tofu is the worse half of that trade.

**One CJK face across a whole document.** Two Chinese faces on one page is the first thing a native reader notices, and it makes a layout look busier than its content — so do not split the stack by job the way you might in Latin-only typography. A calligraphic face (楷體, and LXGW WenKai in particular) is a specific trap: pleasant on its own, too literary beside code and equations. `paper-teardown` tried the split and reverted it; the finding is recorded in its `reference/structure.md`.

## Type scale

Points, at a default 15px base. HTML reports are read at arm's length on a large display, which is a different problem from a projected slide — do not import the deck's scale.

| Role | Size | Weight | Face |
|---|---|---|---|
| Page title | 22 | 500 | sans |
| Section (`h2`) | 15 | 600 | sans, `letter-spacing:.09em`, uppercase, `--accent-deep` |
| Sub-section / group label | 11 | 500 | sans, `letter-spacing:.1em`, `--ink3` |
| Body | 15 / 1.62 | 400 | sans |
| Secondary body | 13 | 400 | sans, `--ink2` |
| Card title | 14.5 | 500 | sans |
| Data, shapes, paths, figures | 11.5–12 | 400 | **mono**, `font-variant-numeric:tabular-nums` |
| Label / caption | 10.5–11 | 400 | mono or sans, `--ink3` |
| Tag | 10 | 400 | mono |

**Every number a reader might compare down a column is mono with tabular figures.** Proportional digits in a financial table are a defect, not a style choice.
