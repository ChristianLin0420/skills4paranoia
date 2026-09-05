"""Geometry, theme tokens and draw-op primitives.

Every layout emits a flat list of ops in this coordinate space (points, origin
top-left, 960x540 = 16:9). Both the .pptx backend and the .svg preview backend
consume the same ops, so a layout is written once and never drifts.

The type scale is deliberately small. A research slide carries a full piece of
evidence — chart, numbers, and the conditions they were measured under — not a
single headline, so the sizes here sit closer to a paper figure than to a
conference keynote.
"""
import json
import os

W, H = 960.0, 540.0

MX = 56.0
HEAD_TOP = 38.0
HEAD_RULE = 62.0
BODY_TOP = 88.0
BODY_BOT = 446.0
NOTE_TOP = 452.0
FOOT_RULE = 476.0
FOOT_TOP = 483.0
CW = W - 2 * MX

TYPE = {
    "display": 34.0,
    "verdict": 26.0,
    "title": 21.0,
    "subtitle": 13.5,
    "lead": 15.0,
    "body": 12.5,
    "small": 11.0,
    "meta": 9.5,
    "eyebrow": 9.5,
    "number": 34.0,
    "number_sm": 26.0,
    "numeral": 64.0,
}

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
THEME_DIR = os.path.join(ROOT, "themes")
TYPESET_DIR = os.path.join(ROOT, "typesets")


def _load_json(kind, directory, name):
    path = name if os.path.isfile(name) else os.path.join(directory, "%s.json" % name)
    if not os.path.isfile(path):
        raise SystemExit("%s not found: %s (looked in %s)" % (kind, name, directory))
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def load_theme(name, typeface=None):
    """Colour theme and typeface set are orthogonal — pick them independently."""
    th = _load_json("theme", THEME_DIR, name)
    ts = _load_json("typeset", TYPESET_DIR, typeface or "plex")
    th["typeset"] = ts["name"]
    th["typeset_label"] = ts.get("label", ts["name"])
    th["google_fonts"] = ts.get("google", [])
    th["font_latin"] = ts["latin"]
    th["font_cjk"] = ts["cjk"]
    th["font_mono"] = ts["mono"]
    th["font_display"] = ts.get("display", ts["latin"])
    return th


def face(th, kind):
    """(latin, cjk) typeface names for a font role."""
    if kind == "mono":
        return th["font_mono"], th["font_mono"]
    if kind == "display":
        return th["font_display"], th["font_cjk"]
    return th["font_latin"], th["font_cjk"]


def rect(x, y, w, h, fill, radius=0.0):
    return {"op": "rect", "x": x, "y": y, "w": w, "h": h, "fill": fill, "radius": radius}


def hline(x, y, w, color, weight=0.75):
    return rect(x, y, w, weight, color)


def vline(x, y, h, color, weight=0.75):
    return rect(x, y, weight, h, color)


def text(x, y, w, h, s, size, color, align="l", valign="t", bold=False,
         leading=1.35, tracking=0.0, font="sans", wrap=True):
    return {"op": "text", "x": x, "y": y, "w": w, "h": h, "s": str(s), "size": size,
            "color": color, "align": align, "valign": valign, "bold": bold,
            "leading": leading, "tracking": tracking, "font": font, "wrap": wrap}


def poly(points, color, weight=1.6, close=False, fill=None):
    return {"op": "poly", "pts": points, "color": color, "weight": weight,
            "close": close, "fill": fill}


def band(points, fill):
    """Closed, filled, unstroked polygon — used for error bands."""
    return {"op": "poly", "pts": points, "color": None, "weight": 0.0,
            "close": True, "fill": fill}


def image(x, y, w, h, path, label=None):
    return {"op": "image", "x": x, "y": y, "w": w, "h": h, "path": path, "label": label}


def is_cjk(ch):
    o = ord(ch)
    return 0x2E80 <= o <= 0x9FFF or 0xF900 <= o <= 0xFAFF or 0xFF00 <= o <= 0xFF60


def measure(s, size):
    """Rough advance width in points. Good enough for preview wrapping."""
    w = 0.0
    for ch in s:
        if is_cjk(ch):
            w += size
        elif ch in "iljt.,'!|":
            w += size * 0.30
        elif ch.isupper() or ch.isdigit():
            w += size * 0.58
        else:
            w += size * 0.50
    return w


def wrap_text(s, size, width, tracking=0.0):
    """Greedy wrap that breaks between CJK glyphs and on spaces for latin."""
    out = []
    for para in s.split("\n"):
        line = ""
        for tok in _tokens(para):
            trial = line + tok
            if line and measure(trial, size) + tracking * len(trial) > width:
                out.append(line.rstrip())
                line = tok.lstrip() if not is_cjk(tok[0]) else tok
            else:
                line = trial
        out.append(line.rstrip())
    return out


def _tokens(s):
    buf = ""
    for ch in s:
        if is_cjk(ch):
            if buf:
                yield buf
                buf = ""
            yield ch
        elif ch == " ":
            buf += ch
            yield buf
            buf = ""
        else:
            buf += ch
    if buf:
        yield buf
