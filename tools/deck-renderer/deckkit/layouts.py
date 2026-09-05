"""Every layout in the catalog, as a function from slide dict to draw ops.

Density is the point. A research slide is expected to carry a figure, the
numbers, and the conditions they were measured under, all at once — so the type
is small, the margins are tight, and every layout reserves a footnote line for
the experimental setup.
"""
import os

from . import charts, core
from .core import BODY_BOT, BODY_TOP, CW, FOOT_RULE, FOOT_TOP, H, HEAD_RULE, HEAD_TOP
from .core import MX, NOTE_TOP, TYPE, W, hline, image, rect, text, vline
from .parser import split_fields

PROBLEM_KEYS = ["Q1", "Q2", "Q3", "Q4"]


def fit(s, size, width, max_lines, floor=None):
    floor = floor or size * 0.6
    while size > floor and len(core.wrap_text(s, size, width)) > max_lines:
        size -= 0.5
    return size


def block_h(s, size, width, leading=1.3):
    return max(1, len(core.wrap_text(s, size, width))) * size * leading


def head(ctx, left="", tag=None):
    th = ctx["th"]
    ops = []
    x = MX
    if tag:
        tw = core.measure(tag, TYPE["meta"]) + 15
        ops.append(rect(x, HEAD_TOP - 4, tw, 16, th["accent_soft"], 2.5))
        ops.append(text(x, HEAD_TOP - 4, tw, 16, tag, TYPE["meta"], th["accent_deep"],
                        align="c", valign="m", font="mono"))
        x += tw + 9
    if left:
        ops.append(text(x, HEAD_TOP - 4, 500, 16, left, TYPE["eyebrow"], th["ink2"],
                        valign="m", tracking=0.5))
    right = ctx["meta"].get("running") or ctx["meta"].get("title", "")
    ops.append(text(W - MX - 340, HEAD_TOP - 4, 340, 16, right, TYPE["eyebrow"], th["ink3"],
                    align="r", valign="m", wrap=False))
    ops.append(hline(MX, HEAD_RULE, CW, th["rule"]))
    return ops


def foot(ctx, slide=None, source=None):
    th = ctx["th"]
    ops = []
    note = (slide or {}).get("footnote")
    if note:
        ops.append(text(MX, NOTE_TOP, CW, 20, note, TYPE["meta"], th["ink3"], leading=1.4))
    ops.append(hline(MX, FOOT_RULE, CW, th["rule"]))
    left = source or (slide or {}).get("attrs", {}).get("source") or ctx["meta"].get("footer", "")
    if left:
        ops.append(text(MX, FOOT_TOP, CW - 60, 13, left, TYPE["meta"], th["ink3"], wrap=False))
    if ctx.get("page"):
        ops.append(text(W - MX - 50, FOOT_TOP, 50, 13, "%02d" % ctx["page"], TYPE["meta"],
                        th["ink3"], align="r", font="mono"))
    return ops


def titled(slide, ctx, tag=None, eyebrow=None):
    """Header + title + optional subtitle. Returns (ops, y of next free line)."""
    th = ctx["th"]
    ops = head(ctx, eyebrow if eyebrow is not None else slide["attrs"].get("eyebrow", ""), tag)
    y = BODY_TOP
    if slide["title"]:
        size = fit(slide["title"], TYPE["title"], CW, 2, 16)
        h = block_h(slide["title"], size, CW, 1.26)
        ops.append(text(MX, y, CW, h + 4, slide["title"], size, th["ink"], leading=1.26,
                        tracking=-0.2, font="display"))
        y += h + 5
    if slide["subtitle"]:
        h = block_h(slide["subtitle"], TYPE["subtitle"], CW * 0.8, 1.4)
        ops.append(text(MX, y, CW * 0.8, h + 3, slide["subtitle"], TYPE["subtitle"], th["ink2"],
                        leading=1.4))
        y += h + 4
    return ops, y + 12


def claim_tag(slide):
    s = slide["attrs"].get("solves") or slide["attrs"].get("supports")
    return s.upper() if s else None


def picture(path, base_dir, x, y, w, h, th, s, caption=None):
    full = path if os.path.isabs(path) else os.path.join(base_dir, path)
    if os.path.isfile(full):
        return [image(x, y, w, h, full, caption)]
    return [rect(x, y, w, h, th["accent_wash"], 2.5),
            text(x + 8, y, w - 16, h, s["missing_file"] % os.path.basename(path),
                 TYPE["meta"], th["ink3"], align="c", valign="m", leading=1.5)]


# --- front three -----------------------------------------------------------

def F0(slide, ctx):
    th, m = ctx["th"], ctx["meta"]
    ops = [rect(MX, 168, 28, 3, th["accent"])]
    title = slide["title"] or m.get("title", "")
    size = fit(title, TYPE["display"], CW * 0.8, 2, 22)
    h = block_h(title, size, CW * 0.8, 1.2)
    ops.append(text(MX, 190, CW * 0.8, h + 6, title, size, th["ink"], leading=1.2,
                    tracking=-0.4, font="display"))
    y = 190 + h + 10
    sub = slide["subtitle"] or m.get("subtitle", "")
    if sub:
        ops.append(text(MX, y, CW * 0.66, 26, sub, TYPE["subtitle"], th["ink2"]))
    meta_line = " · ".join(str(v) for v in [m.get("author"), m.get("team"), m.get("date")] if v)
    if meta_line:
        ops.append(text(MX, 402, CW * 0.66, 18, meta_line, TYPE["small"], th["ink3"]))
    ops += [hline(MX, FOOT_RULE, CW, th["rule"]),
            text(MX, FOOT_TOP, CW - 60, 13, m.get("footer", ""), TYPE["meta"], th["ink3"], wrap=False)]
    return ops


def P1(slide, ctx):
    """Problem — one big problem decomposed into mid-level and sub problems."""
    th, st = ctx["th"], ctx["s"]
    ops = head(ctx, st["front_1"], "1 / 3")
    big = slide["title"] or ""
    size = fit(big, TYPE["verdict"] - 3, CW, 2, 15)
    h = block_h(big, size, CW, 1.3)
    ops.append(text(MX, BODY_TOP, CW, h + 4, big, size, th["ink"], leading=1.3,
                    tracking=-0.2, font="display"))
    y = BODY_TOP + h + 15
    ops.append(hline(MX, y, CW, th["rule"]))
    y += 17
    cols = slide["bullets"][:4]
    gap = 20.0
    cw = (CW - gap * (len(cols) - 1)) / max(1, len(cols))
    for i, raw in enumerate(cols):
        key, headline, subs = problem_parts(raw, i)
        cx = MX + i * (cw + gap)
        ops.append(rect(cx, y, cw, 2, th["accent"] if i == 0 else th["ladder"][2]))
        ops.append(text(cx, y + 8, cw, 13, key, TYPE["meta"], th["accent_deep"],
                        tracking=0.6, font="mono"))
        hh = block_h(headline, TYPE["body"], cw, 1.4)
        ops.append(text(cx, y + 23, cw, hh + 4, headline, TYPE["body"], th["ink"], leading=1.4))
        sy = y + 30 + hh
        for sub in subs[:3]:
            sh = block_h(sub, TYPE["small"], cw - 11, 1.45)
            ops.append(hline(cx, sy, cw, th["rule_soft"]))
            ops.append(text(cx, sy + 6, 9, 12, "·", TYPE["small"], th["ink3"]))
            ops.append(text(cx + 11, sy + 6, cw - 11, sh + 4, sub, TYPE["small"],
                            th["ink2"], leading=1.45))
            sy += sh + 13
    if slide["kicker"]:
        ops.append(rect(MX, BODY_BOT - 12, 16, 2, th["accent"]))
        ops.append(text(MX + 24, BODY_BOT - 19, CW - 24, 18, "  ".join(slide["kicker"]),
                        TYPE["small"], th["ink2"], wrap=False))
    ops += foot(ctx, slide)
    return ops


def problem_parts(raw, i):
    """`Q1 | mid-level problem | sub | sub` -> (key, headline, [subs])."""
    parts = split_fields(raw)
    if parts and parts[0].strip().upper() in PROBLEM_KEYS:
        return parts[0].strip().upper(), (parts[1] if len(parts) > 1 else ""), parts[2:]
    return PROBLEM_KEYS[i], parts[0], parts[1:]


def P2(slide, ctx):
    """Solution — the mechanism, mapped one row per problem."""
    th, st = ctx["th"], ctx["s"]
    ops, y = titled(slide, ctx, "2 / 3", st["front_2"])
    rows = slide["bullets"][:4]
    has_img = bool(slide["images"])
    gap = 28.0
    lw = CW * 0.42 if has_img else 0.0
    rx = MX + (lw + gap if has_img else 0.0)
    rw = CW - (lw + gap if has_img else 0.0)
    if has_img:
        im = slide["images"][0]
        ih = BODY_BOT - y - (16 if im["caption"] else 0)
        ops += picture(im["path"], ctx["base_dir"], MX, y, lw, ih, th, st)
        if im["caption"]:
            ops.append(text(MX, y + ih + 4, lw, 14, im["caption"], TYPE["meta"], th["ink3"]))
    rh = (BODY_BOT - y) / max(1, len(rows))
    key_w = 32.0
    for i, raw in enumerate(rows):
        key, body, metric = split_fields(raw, 3)
        ry = y + i * rh
        ops.append(hline(rx, ry, rw, th["rule_soft"] if i else th["rule"]))
        ops.append(text(rx, ry + 10, key_w, 13, key.upper(), TYPE["meta"],
                        th["accent_deep"], font="mono"))
        bh = block_h(body, TYPE["body"], rw - key_w, 1.45)
        ops.append(text(rx + key_w, ry + 9, rw - key_w, bh + 4, body, TYPE["body"],
                        th["ink"], leading=1.45))
        if metric:
            ops.append(text(rx + key_w, ry + 13 + bh, rw - key_w, 13, metric, TYPE["small"],
                            th["accent_deep"], font="mono"))
    ops += foot(ctx, slide)
    return ops


def P3(slide, ctx):
    """Results — a dense results table beside the headline figure."""
    th = ctx["th"]
    ops, y = titled(slide, ctx, "3 / 3", ctx["s"]["front_3"])
    t = slide["table"] or {}
    has_chart = bool(slide["chart"])
    tw = CW * (0.56 if has_chart else 1.0)
    if t.get("cols"):
        ops += _table(slide, ctx, y, t["cols"], t.get("rows") or [], x=MX, width=tw)
    if has_chart:
        cx = MX + tw + 30
        ops += charts.render(slide["chart"], (cx, y, W - MX - cx, BODY_BOT - y), th, ctx["base_dir"])
    ops += foot(ctx, slide)
    return ops


def D(slide, ctx):
    th, s = ctx["th"], ctx["s"]
    label = slide["title"] or s["divider_title"]
    ops = [rect(MX, H / 2 - 26, 28, 3, th["accent"]),
           text(MX, H / 2 - 10, CW * 0.7, 38, label, TYPE["title"], th["ink"],
                tracking=-0.2, font="display")]
    if slide["subtitle"]:
        ops.append(text(MX, H / 2 + 24, CW * 0.7, 24, slide["subtitle"], TYPE["small"], th["ink3"]))
    return ops


# --- evidence --------------------------------------------------------------

def E01(slide, ctx):
    th = ctx["th"]
    idx = slide["attrs"].get("index", "")
    ops = []
    if idx:
        ops.append(text(MX, 190, 200, 78, str(idx), TYPE["numeral"], th["accent"],
                        tracking=-2.5, font="mono"))
    ops.append(text(MX, 284, CW * 0.7, 34, slide["title"] or "", TYPE["title"], th["ink"],
                    tracking=-0.2, font="display"))
    if slide["subtitle"]:
        ops.append(text(MX, 322, CW * 0.6, 34, slide["subtitle"], TYPE["small"], th["ink2"], leading=1.5))
    ops.append(hline(MX, 366, 180, th["rule"]))
    ops += foot(ctx, slide)
    return ops


def E02(slide, ctx):
    th = ctx["th"]
    ops = head(ctx, slide["attrs"].get("eyebrow", ""), claim_tag(slide))
    s = slide["title"] or ""
    size = fit(s, TYPE["verdict"], CW * 0.88, 3, 17)
    h = block_h(s, size, CW * 0.88, 1.34)
    y = (BODY_TOP + BODY_BOT) / 2 - h / 2 - 16
    ops.append(text(MX, y, CW * 0.88, h + 6, s, size, th["ink"], leading=1.34,
                    tracking=-0.2, font="display"))
    extra = slide["kicker"] + slide["paras"]
    if extra:
        ops.append(text(MX, y + h + 16, CW * 0.7, 50, "  ".join(extra), TYPE["body"],
                        th["ink2"], leading=1.55))
    ops += foot(ctx, slide)
    return ops


def E03(slide, ctx):
    th = ctx["th"]
    ops, y = titled(slide, ctx, claim_tag(slide))
    rows = slide["bullets"][:5]
    rh = min(56.0, (BODY_BOT - y) / max(1, len(rows)))
    for i, raw in enumerate(rows):
        parts = split_fields(raw)
        ry = y + i * rh
        ops.append(rect(MX + 1, ry + 6, 5, 5, th["series"][i % len(th["series"])], 2.5))
        ops.append(text(MX + 16, ry, CW - 16, rh - 6, parts[0], TYPE["lead"], th["ink"], leading=1.35))
        if len(parts) > 1:
            ops.append(text(MX + 16, ry + 21, CW - 16, rh - 24, " ".join(parts[1:]),
                            TYPE["small"], th["ink2"], leading=1.45))
    ops += foot(ctx, slide)
    return ops


def E04(slide, ctx):
    th = ctx["th"]
    ops, y = titled(slide, ctx, claim_tag(slide))
    cols = slide["bullets"][:2]
    gap = 38.0
    cw = (CW - gap) / 2
    ops.append(vline(MX + cw + gap / 2, y, BODY_BOT - y, th["rule"]))
    for i, raw in enumerate(cols):
        parts = split_fields(raw)
        cx = MX + i * (cw + gap)
        ops.append(rect(cx, y, 22, 2, th["series"][i]))
        ops.append(text(cx, y + 11, cw, 24, parts[0], TYPE["lead"], th["ink"]))
        for j, line in enumerate(parts[1:6]):
            ly = y + 42 + j * 30
            ops.append(text(cx, ly, cw, 26, line, TYPE["body"], th["ink2"], leading=1.4))
            ops.append(hline(cx, ly + 23, cw, th["rule_soft"]))
    ops += foot(ctx, slide)
    return ops


def E06(slide, ctx):
    th = ctx["th"]
    ops, y = titled(slide, ctx, claim_tag(slide))
    if slide["chart"]:
        ops += charts.render(slide["chart"], (MX, y + 4, CW, BODY_BOT - y - 8), th, ctx["base_dir"])
    ops += foot(ctx, slide)
    return ops


def E07(slide, ctx):
    th = ctx["th"]
    ops = head(ctx, slide["attrs"].get("eyebrow", ""), claim_tag(slide))
    lw = CW * 0.32
    gap = 34.0
    y = BODY_TOP
    if slide["title"]:
        size = fit(slide["title"], TYPE["title"] - 3, lw, 4, 15)
        h = block_h(slide["title"], size, lw, 1.28)
        ops.append(text(MX, y, lw, h + 4, slide["title"], size, th["ink"], leading=1.28,
                        tracking=-0.2, font="display"))
        y += h + 12
    for p in (slide["paras"] + slide["kicker"])[:4]:
        h = block_h(p, TYPE["small"], lw, 1.5)
        ops.append(text(MX, y, lw, h + 4, p, TYPE["small"], th["ink2"], leading=1.5))
        y += h + 10
    if slide["chart"]:
        cx = MX + lw + gap
        ops += charts.render(slide["chart"], (cx, BODY_TOP + 4, W - MX - cx, BODY_BOT - BODY_TOP - 8),
                             th, ctx["base_dir"])
    ops += foot(ctx, slide)
    return ops


def E08(slide, ctx):
    th = ctx["th"]
    ops = head(ctx, slide["attrs"].get("eyebrow", ""), claim_tag(slide))
    s = " ".join(slide["kicker"]) or slide["title"] or ""
    size = fit(s, TYPE["lead"] + 5, CW * 0.78, 4, 14)
    h = block_h(s, size, CW * 0.78, 1.6)
    y = (BODY_TOP + BODY_BOT) / 2 - h / 2
    ops.append(rect(MX, y - 24, 22, 2, th["accent"]))
    ops.append(text(MX, y, CW * 0.78, h + 6, s, size, th["ink"], leading=1.6))
    by = slide["attrs"].get("by") or (slide["paras"][0] if slide["paras"] else "")
    if by:
        ops.append(text(MX, y + h + 16, CW * 0.7, 18, by, TYPE["small"], th["ink3"]))
    ops += foot(ctx, slide)
    return ops


def E09(slide, ctx):
    th = ctx["th"]
    ops, y = titled(slide, ctx, claim_tag(slide))
    rows = slide["bullets"][:5]
    n = max(1, len(rows))
    mid = (y + BODY_BOT) / 2 - 24
    seg = CW / n
    ops.append(hline(MX, mid, CW, th["rule"]))
    for i, raw in enumerate(rows):
        stage, body = split_fields(raw, 2)
        cx = MX + i * seg
        ops.append(rect(cx, mid - 3, 7, 7, th["series"][i % len(th["series"])], 3.5))
        ops.append(text(cx, mid - 34, seg - 16, 26, stage, TYPE["body"], th["ink"]))
        ops.append(text(cx, mid + 16, seg - 16, 62, body, TYPE["small"], th["ink2"], leading=1.45))
    ops += foot(ctx, slide)
    return ops


def _is_num(cell):
    try:
        float(str(cell).lstrip("*").replace("%", "").replace("+", "").replace(",", ""))
        return True
    except ValueError:
        return False


def _table(slide, ctx, y, cols, rows, extra_col=None, mark=None, x=MX, width=None):
    """Shared table renderer. Numeric cells go right-aligned and monospaced."""
    th = ctx["th"]
    width = CW if width is None else width
    ops = []
    ncols = len(cols) + (1 if extra_col else 0)
    first_w = width * (0.30 if ncols <= 4 else 0.24)
    rest_w = (width - first_w) / max(1, ncols - 1)
    widths = [first_w] + [rest_w] * (ncols - 1)
    heads = list(cols) + ([extra_col] if extra_col else [])
    rh = min(32.0, (BODY_BOT - y - 24) / max(1, len(rows)))
    for i, c in enumerate(heads):
        num = i > 0
        ops.append(text(x + sum(widths[:i]), y, widths[i] - 10, 16, c, TYPE["meta"], th["ink2"],
                        tracking=0.5, align="r" if num else "l"))
    ops.append(hline(x, y + 19, width, th["rule"]))
    for r, row in enumerate(rows):
        ry = y + 24 + r * rh
        if mark is not None and r == mark:
            ops.append(rect(x - 8, ry, 2.5, rh - 5, th["accent"]))
        for i, cell in enumerate(row[:ncols]):
            raw = str(cell)
            emph = raw.startswith("*")
            val = raw.lstrip("*")
            num = _is_num(val) and i > 0
            color = th["accent_deep"] if emph else (th["ink2"] if i == 0 else th["ink"])
            ops.append(text(x + sum(widths[:i]), ry, widths[i] - 10, rh - 5, val,
                            TYPE["small"], color, valign="m",
                            align="r" if num else "l", font="mono" if num else "sans"))
        ops.append(hline(x, ry + rh - 5, width, th["rule_soft"]))
    return ops


def E10(slide, ctx):
    ops, y = titled(slide, ctx, claim_tag(slide))
    t = slide["table"] or {}
    if t.get("cols"):
        ops += _table(slide, ctx, y, t["cols"], t.get("rows") or [])
    ops += foot(ctx, slide)
    return ops


def E19(slide, ctx):
    """Ablation table: adds a Δ column against the first row and marks the winner."""
    ops, y = titled(slide, ctx, claim_tag(slide))
    t = slide["table"] or {}
    cols, rows = list(t.get("cols") or []), [list(r) for r in (t.get("rows") or [])]
    if not cols:
        return ops + foot(ctx, slide)
    target = slide["attrs"].get("delta")
    idx = cols.index(target) if target in cols else (len(cols) - 1)
    mark = None
    if rows:
        def num(r):
            v = str(r[idx]).lstrip("*").replace("%", "").replace(",", "")
            try:
                return float(v)
            except ValueError:
                return None
        base = num(rows[0])
        want_min = str(slide["attrs"].get("best", "max")).lower() == "min"
        vals = [num(r) for r in rows]
        good = [v for v in vals if v is not None]
        if good:
            pick = min(good) if want_min else max(good)
            mark = vals.index(pick)
        unit = "%" if "%" in str(rows[0][idx]) else ""
        for r, row in enumerate(rows):
            v = vals[r]
            row.append("—" if r == 0 or v is None or base is None
                       else charts.fmt_delta(v, base, str(slide["attrs"].get("delta_mode", "pp")), unit))
    ops += _table(slide, ctx, y, cols, rows, extra_col=ctx["s"]["delta"], mark=mark)
    ops += foot(ctx, slide)
    return ops


def E11(slide, ctx):
    spec = dict(slide["chart"] or {})
    spec.setdefault("type", "line")
    return E06(dict(slide, chart=spec), ctx)


def E12(slide, ctx):
    spec = dict(slide["chart"] or {})
    spec.setdefault("type", "matrix")
    return E06(dict(slide, chart=spec), ctx)


def E17(slide, ctx):
    """Multi-panel figure — two to four charts sharing one caption."""
    th = ctx["th"]
    ops, y = titled(slide, ctx, claim_tag(slide))
    specs = slide["charts"][:4]
    if not specs:
        return ops + foot(ctx, slide)
    n = len(specs)
    gap = 26.0
    avail_h = BODY_BOT - y
    cols = 2 if n == 4 else n
    rows = 2 if n == 4 else 1
    pw = (CW - gap * (cols - 1)) / cols
    ph = (avail_h - (gap - 8) * (rows - 1)) / rows
    for i, spec in enumerate(specs):
        cx = MX + (i % cols) * (pw + gap)
        cy = y + (i // cols) * (ph + gap - 8)
        ops += charts.render(spec, (cx, cy, pw, ph), th, ctx["base_dir"])
    ops += foot(ctx, slide)
    return ops


def E18(slide, ctx):
    """Experimental setup — grouped key/value pairs, values monospaced."""
    th = ctx["th"]
    ops, y = titled(slide, ctx, claim_tag(slide), slide["attrs"].get("eyebrow", ctx["s"]["setup"]))
    groups = slide["bullets"][:4]
    if not groups:
        return ops + foot(ctx, slide)
    gap = 24.0
    cw = (CW - gap * (len(groups) - 1)) / len(groups)
    for i, raw in enumerate(groups):
        parts = split_fields(raw)
        cx = MX + i * (cw + gap)
        ops.append(rect(cx, y, cw, 2, th["accent"] if i == 0 else th["ladder"][2]))
        ops.append(text(cx, y + 9, cw, 16, parts[0], TYPE["small"], th["accent_deep"]))
        for j, pair in enumerate(parts[1:9]):
            ry = y + 32 + j * 24
            key, _, val = pair.partition("=")
            ops.append(text(cx, ry, cw * 0.52, 20, key.strip(), TYPE["meta"], th["ink3"], valign="m"))
            ops.append(text(cx + cw * 0.52, ry, cw * 0.48, 20, val.strip() or "—", TYPE["small"],
                            th["ink"], align="r", valign="m", font="mono"))
            ops.append(hline(cx, ry + 20, cw, th["rule_soft"]))
    ops += foot(ctx, slide)
    return ops


def E20(slide, ctx):
    """A figure the user supplied, placed as-is under the deck's own chrome.

    Used when the figure cannot be regenerated from data — architecture
    diagrams, photographs, screenshots. Statistical plots should be redrawn
    from their source numbers instead so the styling matches the rest.
    """
    th, st = ctx["th"], ctx["s"]
    ops, y = titled(slide, ctx, claim_tag(slide))
    im = slide["images"][0] if slide["images"] else {"path": "figure.png", "caption": ""}
    cap = im.get("caption") or ""
    ih = BODY_BOT - y - (17 if cap else 0)
    ops += picture(im["path"], ctx["base_dir"], MX, y, CW, ih, th, st)
    if cap:
        ops.append(text(MX, y + ih + 4, CW, 14, cap, TYPE["meta"], th["ink3"], wrap=False))
    ops += foot(ctx, slide)
    return ops


def E21(slide, ctx):
    """Two supplied figures side by side, each with its own caption."""
    th, st = ctx["th"], ctx["s"]
    ops, y = titled(slide, ctx, claim_tag(slide))
    imgs = slide["images"][:2] or [{"path": "left.png", "caption": ""},
                                   {"path": "right.png", "caption": ""}]
    gap = 24.0
    cw = (CW - gap * (len(imgs) - 1)) / len(imgs)
    cap_h = 28 if any(i.get("caption") for i in imgs) else 0
    ih = BODY_BOT - y - cap_h
    for i, im in enumerate(imgs):
        cx = MX + i * (cw + gap)
        ops += picture(im["path"], ctx["base_dir"], cx, y, cw, ih, th, st)
        if im.get("caption"):
            ops.append(text(cx, y + ih + 5, cw, 24, im["caption"], TYPE["meta"],
                            th["ink3"], leading=1.4))
    ops += foot(ctx, slide)
    return ops


def E13(slide, ctx):
    th, s = ctx["th"], ctx["s"]
    ops, y = titled(slide, ctx, claim_tag(slide))
    imgs = slide["images"][:6] or [{"path": "frame%d.png" % (i + 1), "caption": ""} for i in range(4)]
    n = len(imgs)
    gap = 10.0
    cw = (CW - gap * (n - 1)) / n
    ch = min(cw * 0.7, BODY_BOT - y - 26)
    for i, im in enumerate(imgs):
        cx = MX + i * (cw + gap)
        ops += picture(im["path"], ctx["base_dir"], cx, y, cw, ch, th, s)
        ops.append(text(cx, y + ch + 6, cw, 26, im["caption"] or "t=%d" % i, TYPE["meta"],
                        th["ink3"], leading=1.35))
    ops += foot(ctx, slide)
    return ops


def E14(slide, ctx):
    th, s = ctx["th"], ctx["s"]
    ops, y = titled(slide, ctx, claim_tag(slide))
    notes = (slide["paras"] + slide["kicker"])[:4]
    nw = CW * 0.24 if notes else 0.0
    iw = CW - nw - (28.0 if notes else 0.0)
    cap = slide["images"][0]["caption"] if slide["images"] else ""
    ih = BODY_BOT - y - (20 if cap else 0)
    path = slide["images"][0]["path"] if slide["images"] else "architecture.png"
    ops += picture(path, ctx["base_dir"], MX, y, iw, ih, th, s)
    if cap:
        ops.append(text(MX, y + ih + 5, iw, 16, cap, TYPE["meta"], th["ink3"]))
    ny = y
    for i, p in enumerate(notes):
        ops.append(rect(MX + iw + 28, ny, 16, 2, th["series"][i % len(th["series"])]))
        h = block_h(p, TYPE["small"], nw, 1.5)
        ops.append(text(MX + iw + 28, ny + 9, nw, h + 6, p, TYPE["small"], th["ink2"], leading=1.5))
        ny += h + 26
    ops += foot(ctx, slide)
    return ops


def E15(slide, ctx):
    th, s = ctx["th"], ctx["s"]
    path = slide["images"][0]["path"] if slide["images"] else "cover.png"
    ops = picture(path, ctx["base_dir"], 0, 0, W, H, th, s)
    if slide["title"]:
        ops.append(rect(0, H - 140, W, 140, th["bg"]))
        ops.append(rect(MX, H - 116, 22, 2, th["accent"]))
        ops.append(text(MX, H - 98, CW * 0.7, 36, slide["title"], TYPE["title"] - 2, th["ink"],
                        font="display"))
        if slide["subtitle"]:
            ops.append(text(MX, H - 56, CW * 0.7, 20, slide["subtitle"], TYPE["small"], th["ink2"]))
    return ops


def E16(slide, ctx):
    th, s, m = ctx["th"], ctx["s"], ctx["meta"]
    title = slide["title"] or s["thanks"]
    ops = [text(MX, 236, CW, 44, title, TYPE["title"] + 2, th["ink"], align="c",
                tracking=-0.2, font="display"),
           rect(W / 2 - 14, 296, 28, 2.5, th["accent"])]
    lines = slide["bullets"] or slide["paras"] or [str(m.get("contact", ""))]
    for i, line in enumerate([l for l in lines if l][:3]):
        ops.append(text(MX, 322 + i * 22, CW, 20, line, TYPE["small"], th["ink2"], align="c"))
    return ops


REGISTRY = {"F0": F0, "P1": P1, "P2": P2, "P3": P3, "D": D,
            "E01": E01, "E02": E02, "E03": E03, "E04": E04, "E06": E06,
            "E07": E07, "E08": E08, "E09": E09, "E10": E10, "E11": E11, "E12": E12,
            "E13": E13, "E14": E14, "E15": E15, "E16": E16, "E17": E17, "E18": E18,
            "E19": E19, "E20": E20, "E21": E21}


def render_slide(slide, ctx):
    fn = REGISTRY.get(slide["layout"])
    if fn is None:
        raise KeyError("no renderer for %s" % slide["layout"])
    return fn(slide, ctx)
