# Two layout modes

One token set, one set of evidence conventions, **two page shapes** — because two different
things happen in a reader's head and a single layout serves one of them badly.

| | **Dashboard** | **Long-read** |
|---|---|---|
| The reader is | scanning, comparing, looking something up | reading front to back, once |
| Arrives via | "what is the number for X" | "explain this to me" |
| Page surface | `--bg` grey, cards float on it | `--surface` paper, nothing floats |
| Column model | content + sticky detail panel | one measure + a navigation rail |
| An item is bounded by | a card — border, radius, background | a hairline rule and space |
| Base type | 15px / 1.62 | 16px / 1.85 |
| Built by | `codebase-onboarding`, `vla-code-review`, `company-dossier` | `paper-teardown` |

**Pick by asking what the reader does with it, not how much content there is.** A long document
is not automatically a long-read: a company dossier is very long and is still a dashboard,
because nobody reads a filing history start to finish — they go to the year they care about.
A teardown is read once, in order, and every card border in it is a wall the eye has to climb.

Choosing wrong is visible immediately. Cards in a long-read chop prose into boxes that all
look equally important. A long-read measure in a dashboard wastes the width that made
side-by-side comparison possible in the first place.

---

## Shared, and not negotiable in either mode

These do not fork. If they did, the modes would be two design systems.

- **Every colour token.** Both modes use the same palette; only which token is the page
  surface changes.
- **The evidence tiers** — `verified` / `stated` / `inferred` — their meanings, and the rule
  that `inferred` is the default you have to earn your way out of.
- **The unverified banner.** A report that was not checked must not look like one that was.
- **One CJK face for the whole document**, named in both the sans and the mono stack.
- **Proper nouns in `--name`**, applied from a term list rather than by hand.
- **The provenance footer**, with a version or a date.
- **Tags carry state, never prose.**

---

## Dashboard

The default, and the older of the two. Content column plus a sticky panel; the panel holds
the detail for whatever the reader selected, so it must not scroll away.

```css
body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.62 var(--sans)}
.wrap{display:grid;grid-template-columns:minmax(0,1fr) clamp(300px,27vw,392px);min-height:100vh}
main{padding:30px 34px 80px;min-width:0}
aside{border-left:1px solid var(--rule);background:var(--surface);position:sticky;top:0;
      height:100vh;overflow-y:auto;padding:30px 22px 40px}
```

`clamp()` on the panel, never a fixed width — a fixed panel squeezes the content column to
nothing on a laptop.

**Sections are labels, not chapters:** `h2` at 15px, uppercase, `.09em` tracking, a rule under
it. They mark where you are in a scan, so they stay small.

**Cards are the unit.** Border, 5px radius, `--surface` on `--bg`. Density is a feature here;
a dashboard that breathes is a dashboard you have to scroll.

Full type scale in `tokens.md`. The frame is `templates/base.html`.

---

## Long-read

One measure, a navigation rail, and no boxes. Everything the reader meets is on the same
vertical line.

```css
body{margin:0;background:var(--surface);color:var(--body);font:16px/1.85 var(--sans)}
html[lang^="zh"] body{line-height:2.05;letter-spacing:.028em}
.wrap{max-width:1024px;margin:0 auto;padding:0 28px}
.shell{display:grid;grid-template-columns:206px minmax(0,1fr);gap:56px}
nav.rail{position:sticky;top:28px;align-self:start;max-height:calc(100vh - 56px);overflow:auto}
section{padding-bottom:88px}
section + section{border-top:1px solid var(--rule);padding-top:64px}
h2.sec{font-size:clamp(1.4rem,2.6vw,1.85rem);font-weight:600;line-height:1.25}
h2.sec .en{display:block;font-size:.6em;font-weight:500;color:var(--muted);margin-top:6px}
.keyline{width:74px;height:4px;background:var(--accent);margin:22px 0 30px}
```

### The three rules that make it work

**One measure.** The content column *is* the reading measure — set it once, on the column.
Capping prose at `68ch` inside a wider column gives figures one right edge and text another,
and the step is visible on every figure. Assert it rather than trusting it:

```js
[...document.querySelectorAll("main p, main figure .frame, main figcaption, main table")]
  .map(n => Math.round(n.getBoundingClientRect().right))   // must be one value
```

**Exhibits are one kind of object.** A table and a figure get the same frame, the same caption
treatment, and the same anchor, so a reader learns one thing. Number them, derive an id from
the number, and turn `Figure 2` / `圖 2` in the prose into a link.

**Structure beats leading.** A wall of text is a structure problem first. Raising line-height
alone bought 6%; splitting each block's paragraphs into labelled, ruled items bought the rest.
Measure it — visible characters per 1000px of document height, with the old values reapplied
through an injected stylesheet for a controlled before and after in the same page.

### Sections are chapters here

`h2` is large, sentence case, with a `--accent` keyline under it and an optional smaller
second line for a subtitle. It is a chapter opening, not a scan label — the opposite of the
dashboard's `h2`, and the clearest single tell of which mode a file is in.

---

## One file, with one exception

Every deliverable is still one file that opens from disk with no build step, and a webfont
`<link>` is still the only external reference.

**`paper-teardown` is the exception and states it.** It ships `index.<lang>.html` beside an
`assets/` directory, because a paper's figures are 700 KB to 1 MB and base64 makes that a
third larger and stores it once per language. It also has a real build step — LaTeX compiled
to MathML, figure PDFs converted — because the alternative is an image of an equation.

The escape hatch is required, not optional: that skill's builder takes `--inline`, which
embeds every figure as a data URI and produces the single portable file for anywhere a folder
will not survive the trip. **A deliverable that cannot be reduced to one file has left the
system.**
