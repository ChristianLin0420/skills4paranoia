"""Draw ops -> SVG contact sheet.

Preview only. The .pptx is the deliverable; this exists so a layout change can
be eyeballed in a second without opening Keynote, and so an agent can check its
own output. Both backends read the same ops, so they cannot drift structurally.
"""
import os
from xml.sax.saxutils import escape

from . import core

PAGE = """<!doctype html>
<meta charset="utf-8">
<title>%(title)s — preview</title>
%(fonts)s
<style>
body{margin:0;padding:28px;background:#E7E8EA;font:13px/1.5 -apple-system,'PingFang TC',sans-serif;color:#5F656B}
h1{font-size:15px;font-weight:500;margin:0 0 18px;color:#14171A}
.s{margin:0 0 22px;box-shadow:0 1px 3px rgba(0,0,0,.14);border-radius:3px;overflow:hidden;background:#fff}
.n{display:flex;justify-content:space-between;font-size:11px;margin:0 0 5px;color:#8A9096}
svg{display:block;width:100%%;height:auto}
</style>
<h1>%(title)s · %(count)d 頁 · %(theme)s</h1>
%(body)s
"""


def build(deck, ops_per_slide, theme, out_path):
    parts = []
    for i, (slide, ops) in enumerate(zip(deck["slides"], ops_per_slide), start=1):
        parts.append('<div class="n"><span>%02d · %s</span><span>%s</span></div>' % (
            i, escape(slide["name"]), escape(slide["attrs"].get("supports", "").upper())))
        parts.append('<div class="s">%s</div>' % svg_slide(ops, theme))
    html = PAGE % {"title": escape(str(deck["meta"].get("title", "deck"))),
                   "count": len(deck["slides"]),
                   "theme": escape("%s · %s" % (theme["name"], theme.get("typeset_label", ""))),
                   "fonts": _font_link(theme), "body": "\n".join(parts)}
    with open(out_path, "w", encoding="utf-8") as fh:
        fh.write(html)
    return out_path


def _font_link(th):
    """Pull the typeset from Google Fonts so the preview shows the real faces.

    Only the preview needs this. The .pptx names the fonts and Keynote resolves
    them locally, so those must be installed — see scripts/install-fonts.sh.
    """
    fams = th.get("google_fonts") or []
    if not fams:
        return ""
    q = "&".join("family=" + f.replace(" ", "+") for f in fams)
    return ('<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
            '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?%s&display=swap">' % q)


def svg_slide(ops, th):
    body = ['<rect width="%g" height="%g" fill="#%s"/>' % (core.W, core.H, th["bg"])]
    for op in ops:
        body.append(_emit(op, th))
    return '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %g %g">%s</svg>' % (
        core.W, core.H, "".join(body))


def _emit(op, th):
    kind = op["op"]
    if kind == "rect":
        r = op.get("radius", 0)
        return '<rect x="%g" y="%g" width="%g" height="%g" rx="%g" fill="#%s"/>' % (
            op["x"], op["y"], max(op["w"], 0.1), max(op["h"], 0.1), r, op["fill"].lstrip("#"))
    if kind == "poly":
        pts = " ".join("%g,%g" % (x, y) for x, y in op["pts"])
        fill = "#" + op["fill"].lstrip("#") if op.get("fill") else "none"
        if not op.get("color"):
            return '<polygon points="%s" fill="%s"/>' % (pts, fill)
        return '<polyline points="%s" fill="%s" stroke="#%s" stroke-width="%g" ' \
               'stroke-linejoin="round" stroke-linecap="round"/>' % (
                   pts, fill, op["color"].lstrip("#"), op.get("weight", 1.8))
    if kind == "image":
        href = "file://" + op["path"] if os.path.isabs(op["path"]) else op["path"]
        return '<image x="%g" y="%g" width="%g" height="%g" href="%s" ' \
               'preserveAspectRatio="xMidYMid meet"/>' % (
                   op["x"], op["y"], op["w"], op["h"], escape(href, {'"': "&quot;"}))
    if kind == "text":
        return _text(op, th)
    return ""


def _text(op, th):
    size = op["size"]
    leading = op.get("leading", 1.35)
    tracking = op.get("tracking", 0.0)
    lines = []
    for para in str(op["s"]).split("\n"):
        if op.get("wrap", True):
            lines += core.wrap_text(para, size, op["w"], tracking)
        else:
            lines.append(para)
    align = op.get("align", "l")
    anchor = {"l": "start", "c": "middle", "r": "end"}[align]
    tx = {"l": op["x"], "c": op["x"] + op["w"] / 2, "r": op["x"] + op["w"]}[align]
    total = len(lines) * size * leading
    valign = op.get("valign", "t")
    if valign == "m":
        top = op["y"] + (op["h"] - total) / 2
    elif valign == "b":
        top = op["y"] + op["h"] - total
    else:
        top = op["y"]
    first = top + size * (leading - 0.30)
    kind = op.get("font", "sans")
    latin, cjk = core.face(th, kind)
    # a monospace face falling back to sans-serif loses the column alignment that
    # is the only reason it is there, so the generic family has to follow the role
    if kind == "mono":
        family = "'%s','%s','SF Mono',Menlo,Consolas,monospace" % (latin, cjk)
    else:
        family = "'%s','%s','Helvetica Neue',Arial,sans-serif" % (latin, cjk)
    spans = "".join(
        '<tspan x="%g" y="%g">%s</tspan>' % (tx, first + i * size * leading, escape(ln))
        for i, ln in enumerate(lines))
    extra = ' letter-spacing="%g"' % tracking if tracking else ""
    weight = ' font-weight="500"' if op.get("bold") else ""
    return '<text font-family="%s" font-size="%g" fill="#%s" text-anchor="%s"%s%s>%s</text>' % (
        family, size, op["color"].lstrip("#"), anchor, extra, weight, spans)
