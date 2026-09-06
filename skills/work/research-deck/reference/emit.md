# Emitting

This skill ships no script. The producing code is written on the spot and thrown away. Below is the specification and the traps already hit.

## Which format

| Need | Output | How |
|---|---|---|
| For people to look at, project, print to PDF | A single HTML file | Write the HTML directly, no dependencies |
| Editable in Keynote or PowerPoint | `.pptx` | Write python-pptx code on the spot |
| Both | HTML first to check layout, then pptx | Emit twice from the same deck.md |

Emit HTML first and look at it; only produce the pptx once the layout is right. A pptx has to be opened in Keynote to be seen, which makes iteration slow.

## HTML

One file, each page as an inline SVG (`viewBox="0 0 960 540"`), fonts pulled from Google Fonts with a `<link>`. Nothing needs installing to see the real typefaces.

```html
<!doctype html>
<meta charset="utf-8">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500&family=IBM+Plex+Mono:wght@400;500&family=Noto+Sans+TC:wght@400;500&display=swap">
<style>
body{margin:0;padding:28px;background:#E7E8EA;font:13px/1.5 -apple-system,sans-serif}
.s{margin:0 0 22px;border-radius:3px;overflow:hidden;box-shadow:0 1px 3px rgba(0,0,0,.14)}
svg{display:block;width:100%;height:auto}
</style>
<div class="s"><svg viewBox="0 0 960 540">…</svg></div>
```

SVG notes:

- Every `<text>` needs its own line breaking, split into several `<tspan x= y=>`. CJK glyphs are about one em wide; latin lowercase about 0.50, uppercase and digits about 0.58.
- Baseline position: `top + size × (leading − 0.30)`, then add `size × leading` per line. This matches PowerPoint's line-box behaviour.
- Tracking via `letter-spacing`, in the same units as the viewBox (points).
- Alignment via `text-anchor` plus x: `start` at the left edge, `middle` at the centre, `end` at the right edge.
- Polylines with `<polyline fill="none">`, error bands with `<polygon>` and no stroke.
- For printing to PDF, one page per sheet: add `@page{size:960pt 540pt;margin:0}` and `.s{page-break-after:always}`.

## .pptx

Use python-pptx. Canvas 960 × 540 pt, blank layout, everything drawn as your own shapes — no built-in placeholders.

```python
from pptx import Presentation
from pptx.util import Emu, Pt
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.oxml.ns import qn

prs = Presentation()
prs.slide_width = Emu(int(Pt(960)))
prs.slide_height = Emu(int(Pt(540)))
blank = prs.slide_layouts[6]

slide = prs.slides.add_slide(blank)
slide.background.fill.solid()
slide.background.fill.fore_color.rgb = RGBColor.from_string("F1F2F3")
```

### Traps already hit

**The CJK typeface has to be set separately.** `run.font.name` sets only the latin face and Chinese falls back to a default. Write the XML directly, setting `latin`, `ea` and `cs`:

```python
rPr = run._r.get_or_add_rPr()
for tag, face in (("a:latin", "IBM Plex Sans"), ("a:ea", "Noto Sans TC"), ("a:cs", "IBM Plex Sans")):
    el = rPr.find(qn(tag))
    if el is None:
        el = rPr.makeelement(qn(tag), {}); rPr.append(el)
    el.set("typeface", face)
```

**Tracking has no API.** Set the `spc` attribute on `rPr`, in hundredths of a point: `rPr.set("spc", str(int(tracking * 100)))`.

**Text boxes have default insets.** Zero all four margins or every position shifts:

```python
tf = box.text_frame
tf.word_wrap = True
tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
tf.vertical_anchor = MSO_ANCHOR.TOP        # or MIDDLE / BOTTOM
p.alignment = PP_ALIGN.LEFT                # or CENTER / RIGHT
p.line_spacing = 1.45                      # a float is a multiple
```

**Shapes carry a default shadow.** Every shape needs `shp.shadow.inherit = False`, or Keynote draws a default drop shadow.

**Rounded-rectangle corners must be computed.** `shp.adjustments[0] = radius / min(w, h)`, capped at 0.5. Below 1.5pt in width or height, use a plain rectangle instead or the radius swallows the shape.

**Polylines must not use the default close.** `add_line_segments(pts, close=False)`; the default `True` draws an extra segment back to the start:

```python
b = shapes.build_freeform(pts[0][0], pts[0][1], Pt(1))   # scale = EMU per unit
b.add_line_segments(pts[1:], close=False)
shp = b.convert_to_shape()
shp.fill.background()
shp.line.color.rgb = RGBColor.from_string("3A6183")
shp.line.width = Pt(1.8)
```

Error bands are the reverse: walk the upper bound forward and the lower bound back into one loop, `close=True`, fill it, and `shp.line.fill.background()` to leave it unstroked.

**Images get stretched.** Read the pixel dimensions with `pptx.parts.image.Image.from_file(path).size`, compute a proportional scale yourself and centre it; do not pass both width and height to `add_picture`.

**Use rectangles for hairlines, not connectors.** A 0.75pt-tall rectangle is more stable in Keynote.

**Speaker notes**: `slide.notes_slide.notes_text_frame.text = "…"`.

### Check after emitting

Do not just check that it finished. Open the file and verify:

```python
from pptx import Presentation
import re
p = Presentation(out)
xml = "".join(s.shapes._spTree.xml for s in p.slides)
assert round(p.slide_width / 12700) == 960
print(sorted(set(re.findall(r'typeface="([^"]+)"', xml))))   # both faces must be present
```

Then confirm no shape falls outside 0–960 / 0–540. The usual cause is an axis whose top tick is below the data maximum, which draws the line outside the box — see `research-figures` section 3.

## Installing the fonts

A `.pptx` stores font names only, so the machine opening it must have them or Keynote substitutes silently and the layout shifts. To install the default IBM Plex plus Noto Sans TC: download `IBM Plex Sans`, `IBM Plex Mono` and `Noto Sans TC` from Google Fonts, put the ttf/otf files in `~/Library/Fonts`, and restart Keynote.

`IBM Plex Sans TC` is not on Google Fonts; take it from a release at github.com/IBM/plex.

For anyone without the fonts, especially on Windows, use `typeface: system` — Helvetica Neue, PingFang TC and Menlo, all macOS built-ins.
