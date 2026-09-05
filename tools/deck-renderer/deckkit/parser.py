"""deck.md -> deck dict.

A deck is YAML front-matter followed by slides. Every slide opens with a single
HTML comment naming its layout and its attributes:

    <!-- E07 chart-side supports=C2 eyebrow="樣本效率" -->
"""
import os
import re

import yaml

FRONT_IDS = ["P1", "P2", "P3"]

ALIASES = {
    "cover": "F0", "problem": "P1", "solution": "P2", "results": "P3", "divider": "D",
    "section": "E01", "statement": "E02", "bullets": "E03", "two-col": "E04",
    "chart-full": "E06", "chart-side": "E07", "quote": "E08",
    "timeline": "E09", "table": "E10", "curves": "E11", "matrix": "E12",
    "filmstrip": "E13", "architecture": "E14", "image-full": "E15", "closing": "E16",
    "panels": "E17", "setup": "E18", "ablation": "E19",
}
NAMES = {v: k for k, v in ALIASES.items()}
EVIDENCE_IDS = [i for i in NAMES if i.startswith("E")]

DIRECTIVE = re.compile(r"^<!--\s*([A-Za-z0-9\-]+)\s*(.*?)\s*-->\s*$")
ATTR = re.compile(r'([A-Za-z_][\w\-]*)\s*=\s*(?:"([^"]*)"|\'([^\']*)\'|(\S+))')
IMAGE = re.compile(r"^!\[([^\]]*)\]\(([^)]+)\)\s*$")
FENCE = re.compile(r"^```\s*(\w*)\s*$")


class DeckError(Exception):
    pass


def parse_file(path):
    with open(path, encoding="utf-8") as fh:
        deck = parse(fh.read())
    deck["meta"].setdefault("title", os.path.splitext(os.path.basename(path))[0])
    deck["base_dir"] = os.path.dirname(os.path.abspath(path))
    return deck


def parse(src):
    meta, body, offset = _split_front_matter(src)
    slides = []
    cur = None
    fence = None
    buf = []
    for n, raw in enumerate(body.split("\n"), start=offset):
        m = DIRECTIVE.match(raw) if fence is None else None
        if m:
            if cur:
                _finish(cur, buf)
                slides.append(cur)
            cur = _new_slide(m.group(1), m.group(2), n)
            buf = []
            continue
        if cur is None:
            if raw.strip():
                raise DeckError("line %d: content before the first <!-- layout --> directive" % n)
            continue
        f = FENCE.match(raw)
        if f:
            if fence is None:
                fence = (f.group(1) or "text", [])
            else:
                cur["blocks"].append((fence[0], "\n".join(fence[1])))
                fence = None
            continue
        if fence is not None:
            fence[1].append(raw)
            continue
        buf.append(raw)
    if fence is not None:
        raise DeckError("unclosed ``` fence at end of file")
    if cur:
        _finish(cur, buf)
        slides.append(cur)
    return {"meta": meta, "slides": slides, "base_dir": "."}


def _split_front_matter(src):
    lines = src.split("\n")
    if lines and lines[0].strip() == "---":
        for i in range(1, len(lines)):
            if lines[i].strip() == "---":
                meta = yaml.safe_load("\n".join(lines[1:i])) or {}
                if not isinstance(meta, dict):
                    raise DeckError("front-matter must be a YAML mapping")
                return meta, "\n".join(lines[i + 1:]), i + 2
    return {}, src, 1


def _new_slide(token, attr_src, line_no):
    key = token if token in NAMES else ALIASES.get(token.lower())
    if key is None:
        raise DeckError("line %d: unknown layout %r (see catalog.md)" % (line_no, token))
    attrs = {}
    for m in ATTR.finditer(attr_src or ""):
        attrs[m.group(1)] = next(g for g in m.groups()[1:] if g is not None)
    return {"layout": key, "name": NAMES[key], "attrs": attrs, "line": line_no,
            "title": None, "subtitle": None, "kicker": [], "bullets": [],
            "paras": [], "images": [], "blocks": [], "chart": None, "charts": [],
            "table": None, "notes": None, "footnote": attrs.get("footnote")}


def _finish(slide, buf):
    table_rows = []
    for raw in buf:
        s = raw.strip()
        if not s:
            continue
        if s.startswith("## "):
            slide["subtitle"] = s[3:].strip()
        elif s.startswith("# "):
            slide["title"] = s[2:].strip()
        elif s.startswith("> "):
            slide["kicker"].append(s[2:].strip())
        elif s.startswith("~ "):
            slide["footnote"] = ((slide["footnote"] + " · ") if slide["footnote"] else "") + s[2:].strip()
        elif s.startswith("- ") or s.startswith("* "):
            slide["bullets"].append(s[2:].strip())
        elif s.startswith("|"):
            table_rows.append(s)
        else:
            m = IMAGE.match(s)
            if m:
                slide["images"].append({"caption": m.group(1), "path": m.group(2)})
            else:
                slide["paras"].append(s)
    if table_rows:
        slide["table"] = _pipe_table(table_rows)
    for kind, payload in slide["blocks"]:
        if kind == "chart":
            slide["charts"].append(yaml.safe_load(payload) or {})
            slide["chart"] = slide["charts"][0]
        elif kind == "table":
            slide["table"] = yaml.safe_load(payload) or {}
        elif kind == "notes":
            slide["notes"] = payload.strip()
    if slide["kicker"]:
        slide["kicker"] = [k for k in slide["kicker"] if k]


def _pipe_table(rows):
    cells = [[c.strip() for c in r.strip().strip("|").split("|")] for r in rows]
    cells = [r for r in cells if not all(set(c) <= set("-: ") and c for c in r)]
    if not cells:
        return None
    return {"cols": cells[0], "rows": cells[1:]}


def split_fields(s, n=None):
    parts = [p.strip() for p in s.split("|")]
    if n:
        parts += [""] * (n - len(parts))
        return parts[:n]
    return parts
