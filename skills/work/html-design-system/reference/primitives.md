# Primitives

The pieces that recur in every report. Each is small; the point is that they are the *same* small thing each time.

## Page frame

Two columns where a report has a persistent detail panel, one where it does not. The panel is sticky, the content scrolls.

```css
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.62 var(--sans);-webkit-font-smoothing:antialiased}
.wrap{display:grid;grid-template-columns:minmax(0,1fr) clamp(300px,27vw,392px);min-height:100vh}
main{padding:30px 34px 80px;min-width:0}
aside{border-left:1px solid var(--rule);background:var(--surface);position:sticky;top:0;
      height:100vh;overflow-y:auto;padding:30px 22px 40px}
.mono{font-family:var(--mono);font-variant-numeric:tabular-nums}
footer{grid-column:1/-1;padding:14px 34px;border-top:1px solid var(--rule);
       font-size:11.5px;color:var(--ink3);display:flex;justify-content:space-between;gap:16px;flex-wrap:wrap}
```

`clamp()` on the panel, not a fixed width — a fixed panel squeezes the content column to nothing on a laptop.

## Evidence banner

**The most important primitive in the collection.** It sits directly under the title, and it is the first thing a reader sees.

```css
.banner{border:1px solid var(--warn);background:var(--warn-soft);padding:11px 15px;margin:0 0 16px;
        font-size:13.5px;display:flex;gap:11px;align-items:flex-start;line-height:1.55}
.banner .t{font-family:var(--mono);font-size:11px;font-weight:500;color:#fff;background:var(--warn);
           padding:2px 7px;white-space:nowrap;margin-top:2px;letter-spacing:.04em}
.banner.ok{border-color:var(--accent);background:var(--accent-wash)}
.banner.ok .t{background:var(--accent)}
```

```html
<div class="banner"><span class="t">NOT VERIFIED</span><p style="margin:0">…what was not checked, and what a reader must not conclude from this file.</p></div>
```

Two states only, and the unverified one is the default. **A report that was not checked must not look like one that was** — that is the whole convention, and it is why the alarm state is a full-width band rather than a small mark.

## Section header

```css
h2{font-size:15px;font-weight:600;letter-spacing:.09em;text-transform:uppercase;
   color:var(--accent-deep);margin:0 0 11px;padding-bottom:7px;border-bottom:1px solid var(--rule)}
.sub{font-size:12.5px;color:var(--ink2);margin:0 0 16px;font-family:var(--mono)}
```

## Field grid

For "attribute: value" runs — a node's shape and source, a filing's form and date, a metric and its unit. Not a table: tables are for things a reader compares down a column.

```css
dl{margin:0;display:grid;grid-template-columns:74px minmax(0,1fr);gap:6px 12px;font-size:13.5px}
dt{color:var(--ink3);font-size:11.5px;padding-top:3px}
dd{margin:0;min-width:0;overflow-wrap:anywhere}
dd.mono{font-family:var(--mono);font-size:12px;line-height:1.5}
```

## Tag

```css
.tag{font-family:var(--mono);font-size:10px;padding:1.5px 6px;border-radius:2px;
     background:var(--rule-soft);color:var(--ink2)}
.tag.on{background:var(--accent-soft);color:var(--accent-deep)}
.tag.warn{background:var(--warn-soft);color:var(--warn)}
```

Tags carry state, never prose. If it needs a sentence it is a note.

## Evidence mark

The per-item counterpart of the banner. Three levels, and the dashed border is what makes the weakest one visible without reading it.

```css
.conf{display:inline-block;font-family:var(--mono);font-size:10.5px;padding:1px 6px;border-radius:2px}
.conf.verified{background:var(--accent-soft);color:var(--accent-deep)}
.conf.stated  {background:var(--rule-soft);color:var(--ink2)}
.conf.inferred{background:var(--warn-soft);color:var(--warn)}
.card.inferred{border-style:dashed;border-color:var(--ink3)}
```

| Level | Means |
|---|---|
| `verified` | Observed — a probe ran, a figure was read off the source document |
| `stated` | Taken from the source at face value, unambiguous |
| `inferred` | Your reading. Could be wrong |

Default to `inferred` and earn the others.

## Warn block

For the one thing about an item that bites. Distinct from the banner, which is about the whole file.

```css
.trap{border-left:2px solid var(--warn);background:var(--warn-soft);padding:10px 12px;margin-top:14px;
      font-size:13px;line-height:1.6;color:#5E3228}
.trap .h{font-family:var(--mono);font-size:10.5px;letter-spacing:.08em;color:var(--warn);margin-bottom:4px}
```

## Roll-up

Rows that are evidence the work was done, not something to read. Show the count, collapse the rest.

```html
<details><summary>17 rows checked and identical</summary> … </details>
```

A table where most rows say the same thing is mostly noise. **Give the count, then get it out of the way** — the count is the information.

## Proper nouns

```css
b.name{font-weight:600;color:var(--name)}
```

Model names, tickers, entity names. Applied by a term list on the data, not by hand, so it is consistent everywhere the name appears. Keep the list to proper nouns; colouring acronyms colours half the page and then points at nothing.

## Provenance footer

Every report ends with what produced it and against what.

```html
<footer><span>&lt;skill&gt; · &lt;what this is&gt;</span><span class="mono">&lt;source&gt; @ &lt;version or date&gt;</span></footer>
```

A report without a version in the footer cannot be told apart from a stale copy of itself.
