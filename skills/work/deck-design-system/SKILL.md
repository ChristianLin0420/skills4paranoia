---
name: deck-design-system
description: >-
  The visual specification for decks — a low-saturation light palette, a small-type scale built
  for density, a 16:9 grid with exact geometry, and the IBM Plex typeset. Read this before
  producing or reviewing any slide visual, deck colour, typography or layout geometry. Chinese
  triggers: 簡報配色 / 字級 / 版面規格 / 檢查投影片外觀.
---

# deck-design-system

These are specifications, not suggestions. All values in points on a 960 × 540 pt canvas (13.333 × 7.5 in, 16:9), origin top-left.

When producing a whole deck, `research-deck` loads this automatically before emitting — the user does not need to invoke it separately. Invoke it on its own to review an existing deck's appearance, to look up a colour, or to check geometry when adding a layout.

**Language.** Write in whatever language the user writes in. This specification is in English because English is this repo's source language; slide text follows the deck's own `lang` setting.

## 1. Grid

| Position | y | Notes |
|---|---|---|
| Header text | 38 | Layout tag and eyebrow left, deck name right |
| Header rule | 62 | 0.75pt |
| Content top | 88 | Titles start here |
| Content bottom | 446 | Nothing may pass this |
| Conditions footnote | 452 | 9.5pt: n, seeds, hardware |
| Footer rule | 476 | 0.75pt |
| Footer text | 483 | Source left, page number right |

Side margins 56, content width 848. Column gaps 18–28 depending on the count.

Whitespace is structure, not decoration: leave space between columns, and separate blocks with a 0.75pt rule rather than a blank line.

## 2. Type scale

| Role | pt | Used for |
|---|---|---|
| display | 34 | Cover title |
| statement | 26 | The one big problem on P1 |
| title | 21 | Ordinary page titles |
| subtitle | 13.5 | Subtitles |
| lead | 15 | Bullet lead lines |
| body | 12.5 | Body text, main table columns |
| small | 11 | Table cells, chart labels |
| meta | 9.5 | Conditions footnote, tick labels, page number, Q identifiers |

Line height: titles 1.26, body 1.45, footnotes 1.4. Tracking: titles −0.2, large numbers −0.8, eyebrow +0.5, otherwise 0.

Two weights only, Regular and Medium. **Every number is monospaced** — tables, charts, page numbers, Q identifiers — so figures line up across rows, and it is the most direct visual difference between a research deck and a marketing one.

## 3. Palette

Three sets. One deck uses one set, never mixed. All are light-background, low-saturation, a grey ladder plus a single accent.

### slate-blue (default)

```
bg          F1F2F3      page
surface     FAFBFB      cards
ink         14171A      primary text
ink2        5F656B      secondary text
ink3        8A9096      footnotes, tick labels
rule        DCE0E3      primary hairline
rule_soft   E8EBED      secondary hairline
accent      3A6183      the single accent (steel blue)
accent_deep 27435C      accent text
accent_soft DBE4EB      tag backgrounds
accent_wash EAF0F4      block backgrounds
ladder      20242A 4B5158 787E85 A6ACB2 CDD2D6    data grey ladder
series      3A6183 20242A 6E8FA8 787E85 A6ACB2    multi-series
band        DDE5EB DFE1E3 E7ECF0 E5E7E8 EBEDEE    error bands
heat        EDF1F4 CFDCE6 A8C0D2 7C9EB8 3A6183    five heat steps
```

### linen (warm neutral, external decks)

```
bg F4F1EB · ink 1E1D1A · ink2 6A665E · ink3 938E83
rule DFDAD0 · rule_soft E9E5DC · accent 4A6274 · accent_deep 334654
series 4A6274 7C8B6B B08A6B 6F6580 9C6B62
```

### mist (cool neutral, technical and financial)

```
bg F1F3F5 · ink 16191D · ink2 5C6570 · ink3 89929C
rule DCE1E6 · rule_soft E9EDF0 · accent 3F6480 · accent_deep 2B4659
series 3F6480 5E8A80 7B7392 A98A66 8C5F5A
```

Rules:

- One accent colour, on the most important bar, line or cell. Everything else uses the grey ladder.
- Data colours come from the theme; never specify a colour in the content.
- No gradients, shadows, outlines, 3D or emoji.
- Text on a dark cell uses `bg`, not pure white.

## 4. Type

Typeface and palette are independent; switch either without the other.

| Name | Latin | CJK | Mono | Source |
|---|---|---|---|---|
| `plex` (default) | IBM Plex Sans | Noto Sans TC | IBM Plex Mono | Google Fonts, OFL |
| `plex-full` | IBM Plex Sans | IBM Plex Sans TC | IBM Plex Mono | TC from github.com/IBM/plex |
| `inter` | Inter | Noto Sans TC | JetBrains Mono | Google Fonts, OFL |
| `system` | Helvetica Neue | PingFang TC | Menlo | macOS built-in, no install |

IBM Plex is the default because it was designed for a technology company's technical communication — restrained but with recognisable letterforms — and Plex Mono keeps dense figures aligned.

**A .pptx stores font names only**, so the machine opening it must have them installed or Keynote substitutes silently and the layout shifts. Use `system` for anyone who has not installed them, especially on Windows. HTML output pulls the fonts from Google Fonts with a `<link>` and needs no install.

## 5. Component specs

**Header**: a Q tag on the left (`accent_soft` background, `accent_deep` text, 9.5pt monospace, 2.5 corner radius, 7.5 padding each side), then the eyebrow (9.5pt, `ink2`, +0.5 tracking). Deck name on the right (9.5pt, `ink3`, right-aligned). A `rule` at y=62.

**Tables**: column headers 9.5pt `ink2` with +0.5 tracking, numeric columns right-aligned; a `rule` under the header row and a `rule_soft` under each row; row height ≤32; values monospaced; cells prefixed `*` take `accent_deep`; the best row is marked with a 2.5-wide `accent` bar at x−8.

**Bullets**: a 5pt dot in the matching `series` colour, never a glyph. Lead 15pt `ink`, detail 11pt `ink2`. Five maximum.

**Large numbers**: only for the key figures on the solution page — monospaced, `accent_deep`, 11pt. **Do not build a layout that is nothing but large numbers**; that is a promotional page. Results always go in a table.

**Missing image**: draw an `accent_wash` box with 2.5 corner radius and centre the filename and "file not found" in 9.5pt `ink3`. Do not leave it blank.

## 6. Checks

1. Does anything cross the 88–446 content band?
2. Is every number monospaced?
3. Does the accent colour appear in exactly one place?
4. Do the axis ticks reach the data maximum? (a top tick below the maximum draws the line outside the box)
5. Is the contrast sufficient? `ink3` is the lightest usable text colour.
6. Any gradients, shadows, emoji or Title Case?
