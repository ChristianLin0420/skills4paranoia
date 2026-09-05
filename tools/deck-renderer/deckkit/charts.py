"""Chart specs -> draw ops.

Charts are drawn from primitives rather than embedded as native PowerPoint
charts. The trade-off is deliberate: primitives render identically in the .pptx
and the .svg preview, honour the theme exactly, and stay editable in Keynote as
ordinary shapes. Regenerate from source data instead of editing values in place.

Every chart can carry the conditions it was measured under (`note:`), a
reference level (`baseline:`), and dispersion (`band:`). A research figure
without those is not finished.
"""
import csv
import math
import os

from . import core
from .core import TYPE, band as band_op, hline, poly, rect, text


class ChartError(Exception):
    pass


def _read_csv(path, base_dir):
    full = path if os.path.isabs(path) else os.path.join(base_dir, path)
    if not os.path.isfile(full):
        raise ChartError("data file not found: %s" % path)
    with open(full, newline="", encoding="utf-8-sig") as fh:
        rows = [r for r in csv.reader(fh) if r and any(c.strip() for c in r)]
    if len(rows) < 2:
        raise ChartError("data file has no rows: %s" % path)
    return [c.strip() for c in rows[0]], rows[1:]


def load_series(spec, base_dir):
    """Return (labels, [(name, values)], {name: (lo, hi)})."""
    bands = {}
    if spec.get("data"):
        head, rows = _read_csv(spec["data"], base_dir)
        labels = [r[0].strip() for r in rows]
        mode = str(spec.get("band") or "").lower()
        suffixes = tuple(" std,_std".split(",")) if mode == "std" else ()
        wanted = spec.get("series")
        if not wanted:
            wanted = [c for c in head[1:]
                      if not any(c.endswith(s) for s in (" std", "_std", " lo", "_lo", " hi", "_hi"))]
        out = []
        for name in wanted:
            if name not in head:
                raise ChartError("column %r not in %s" % (name, os.path.basename(spec["data"])))
            vals = _col(rows, head.index(name))
            out.append((name, vals))
            if mode == "std":
                col = _find(head, name, suffixes)
                if col is not None:
                    sd = _col(rows, col)
                    bands[name] = ([_sub(v, s) for v, s in zip(vals, sd)],
                                   [_add(v, s) for v, s in zip(vals, sd)])
            elif mode in ("bounds", "minmax"):
                lo = _find(head, name, (" lo", "_lo"))
                hi = _find(head, name, (" hi", "_hi"))
                if lo is not None and hi is not None:
                    bands[name] = (_col(rows, lo), _col(rows, hi))
        return labels, out, bands
    labels = [str(x) for x in (spec.get("labels") or [])]
    if spec.get("values") is not None:
        return labels, [(spec.get("name", ""), [_num(v) for v in spec["values"]])], bands
    series = spec.get("series") or []
    if isinstance(series, dict):
        series = [{"name": k, "values": v} for k, v in series.items()]
    out = [(s.get("name", ""), [_num(v) for v in s.get("values", [])]) for s in series]
    if not out:
        raise ChartError("chart block has no values, series or data")
    return labels, out, bands


def _find(head, name, suffixes):
    for s in suffixes:
        if name + s in head:
            return head.index(name + s)
    return None


def _col(rows, i):
    return [_num(r[i]) if i < len(r) else None for r in rows]


def _add(v, s):
    return None if v is None else v + (s or 0.0)


def _sub(v, s):
    return None if v is None else v - (s or 0.0)


def _num(v):
    if v is None or v == "":
        return None
    try:
        return float(v)
    except (TypeError, ValueError):
        raise ChartError("non-numeric value %r" % v)


def fmt(v, unit=""):
    if v is None:
        return "—"
    if abs(v - round(v)) < 1e-9:
        s = "%d" % round(v)
    elif abs(v) >= 10:
        s = "%.1f" % v
    else:
        s = ("%.2f" % v).rstrip("0").rstrip(".")
    return s + unit


def fmt_delta(v, base, mode, unit=""):
    if v is None or base in (None, 0):
        return ""
    if mode == "pp":
        d = v - base
        return "%+.0fpp" % d if abs(d) >= 1 else "%+.1fpp" % d
    d = (v - base) / abs(base) * 100.0
    return "%+.0f%%" % d if abs(d) >= 1 else "%+.1f%%" % d


def nice_ticks(lo, hi, count=4):
    """Ticks that always bracket the data — the top tick is >= hi, or the
    series would be drawn outside the plot box."""
    if hi <= lo:
        hi = lo + 1.0
    raw = max((hi - lo) / max(1, count), 1e-12)
    mag = 10 ** math.floor(math.log10(raw))
    for mult in (1, 2, 2.5, 5, 10):
        step = mult * mag
        if raw <= step:
            break
    ticks = [math.floor(lo / step) * step]
    while ticks[-1] < hi - 1e-9:
        ticks.append(round(ticks[-1] + step, 10))
    return [round(t, 10) for t in ticks]


def render(spec, box, th, base_dir):
    kind = (spec.get("type") or "bar").lower()
    fn = {"bar": _bar, "column": _bar, "bar-h": _barh, "barh": _barh,
          "line": _line, "curves": _line, "matrix": _matrix, "heatmap": _matrix}.get(kind)
    if fn is None:
        raise ChartError("unknown chart type %r" % kind)
    x, y, w, h = box
    ops = []
    if spec.get("title"):
        ops.append(text(x, y, w, 15, spec["title"], TYPE["small"], th["ink"]))
        y, h = y + 19, h - 19
    note = spec.get("note")
    if note:
        h -= 15
    ops += fn(spec, (x, y, w, h), th, base_dir)
    if note:
        ops.append(text(x, y + h + 4, w, 13, note, TYPE["meta"], th["ink3"], wrap=False))
    return ops


def _baseline_ops(spec, th, px, pw, y, plot_h, tmin, span, unit):
    b = spec.get("baseline")
    if b is None:
        return []
    if not isinstance(b, dict):
        b = {"value": b}
    v = _num(b.get("value"))
    if v is None:
        return []
    by = y + plot_h - (v - tmin) / span * plot_h
    label = b.get("label") or ""
    ops = [hline(px, by, pw, th["ink3"], 0.9)]
    if label:
        ops.append(text(px + 3, by - 12, pw * 0.7, 12, "%s %s" % (label, fmt(v, unit)),
                        TYPE["meta"], th["ink3"], wrap=False))
    return ops


def _barh(spec, box, th, base_dir):
    x, y, w, h = box
    labels, series, _ = load_series(spec, base_dir)
    values = series[0][1]
    unit = spec.get("unit", "")
    delta = spec.get("delta")
    hi = spec.get("max") or max(v for v in values if v is not None)
    n = len(values)
    lab_w = min(150.0, max(56.0, max((core.measure(s, TYPE["small"]) for s in labels), default=56.0) + 8))
    val_w = 44.0
    d_w = 46.0 if delta else 0.0
    track_x = x + lab_w + 10
    track_w = max(40.0, w - lab_w - val_w - d_w - 22)
    gap = 10.0
    bar_h = min(17.0, max(7.0, (h - gap * (n - 1)) / max(1, n)))
    pitch = bar_h + gap if n > 1 else bar_h
    y0 = y + max(0.0, (h - (bar_h * n + gap * (n - 1))) / 2)
    hi_idx = int(spec.get("highlight", 0))
    base = values[int(spec.get("delta_base", 0))] if delta else None
    ops = []
    for i, v in enumerate(values):
        cy = y0 + i * pitch
        ops.append(text(x, cy - 1, lab_w, bar_h + 2, labels[i] if i < len(labels) else "",
                        TYPE["small"], th["ink2"], valign="m"))
        ops.append(rect(track_x, cy, track_w, bar_h, th["rule_soft"], 1.5))
        frac = 0.0 if v is None or hi == 0 else max(0.0, v / hi)
        color = th["accent"] if i == hi_idx else th["ladder"][min(3, 1 + i % 3)]
        ops.append(rect(track_x, cy, max(2.0, track_w * frac), bar_h, color, 1.5))
        ops.append(text(track_x + track_w + 8, cy - 1, val_w, bar_h + 2, fmt(v, unit),
                        TYPE["small"], th["ink"], valign="m", font="mono"))
        if delta and i:
            ops.append(text(track_x + track_w + 8 + val_w, cy - 1, d_w, bar_h + 2,
                            fmt_delta(v, base, str(delta), unit), TYPE["meta"],
                            th["accent_deep"], valign="m", font="mono"))
    return ops


def _bar(spec, box, th, base_dir):
    x, y, w, h = box
    labels, series, _ = load_series(spec, base_dir)
    values = series[0][1]
    unit = spec.get("unit", "")
    delta = spec.get("delta")
    axis_h = 18.0
    plot_h = h - axis_h - (16 if delta else 14)
    lo = min([v for v in values if v is not None] + [0.0])
    ticks = nice_ticks(lo, max(v for v in values if v is not None))
    tmin, tmax = ticks[0], ticks[-1]
    span = (tmax - tmin) or 1.0
    lab_w = 38.0
    px, pw = x + lab_w, w - lab_w
    ops = []
    for t in ticks:
        ty = y + plot_h - (t - tmin) / span * plot_h
        ops.append(hline(px, ty, pw, th["rule_soft"] if t != tmin else th["rule"]))
        ops.append(text(x, ty - 6, lab_w - 7, 12, fmt(t, unit), TYPE["meta"], th["ink3"],
                        align="r", font="mono"))
    ops += _baseline_ops(spec, th, px, pw, y, plot_h, tmin, span, unit)
    n = len(values)
    slot = pw / max(1, n)
    bw = min(46.0, slot * 0.5)
    hi_idx = int(spec.get("highlight", n - 1))
    base = values[int(spec.get("delta_base", 0))] if delta else None
    for i, v in enumerate(values):
        if v is None:
            continue
        bh = (v - tmin) / span * plot_h
        bx = px + slot * i + (slot - bw) / 2
        by = y + plot_h - bh
        ops.append(rect(bx, by, bw, max(2.0, bh), th["accent"] if i == hi_idx else th["ladder"][3], 1.5))
        ops.append(text(bx - slot * 0.25, by - 14, bw + slot * 0.5, 12, fmt(v, unit), TYPE["meta"],
                        th["ink"] if i == hi_idx else th["ink2"], align="c", font="mono"))
        if delta and i:
            ops.append(text(bx - slot * 0.25, by - 26, bw + slot * 0.5, 12,
                            fmt_delta(v, base, str(delta), unit), TYPE["meta"],
                            th["accent_deep"], align="c", font="mono"))
        ops.append(text(bx - slot * 0.25, y + plot_h + 6, bw + slot * 0.5, 14,
                        labels[i] if i < len(labels) else "", TYPE["meta"], th["ink2"], align="c"))
    return ops


def _line(spec, box, th, base_dir):
    x, y, w, h = box
    labels, series, bands = load_series(spec, base_dir)
    unit = spec.get("unit", "")
    end_w = min(120.0, max((core.measure(n, TYPE["meta"]) + 13 for n, _ in series), default=40.0))
    lab_w = 38.0
    axis_h = 20.0
    px, pw = x + lab_w, w - lab_w - end_w
    plot_h = h - axis_h
    flat = [v for _n, vs in series for v in vs if v is not None]
    flat += [v for lo, hi in bands.values() for v in (lo + hi) if v is not None]
    if not flat:
        raise ChartError("line chart has no numeric values")
    ticks = nice_ticks(min(flat), max(flat))
    tmin, tmax = ticks[0], ticks[-1]
    span = (tmax - tmin) or 1.0
    n = max(1, len(labels) - 1)

    def pt(i, v):
        return px + pw * (i / n), y + plot_h - (v - tmin) / span * plot_h

    ops = []
    for si, (name, _vals) in enumerate(series):
        if name in bands:
            lo, hi = bands[name]
            up = [pt(i, v) for i, v in enumerate(hi) if v is not None]
            dn = [pt(i, v) for i, v in enumerate(lo) if v is not None]
            if len(up) > 1 and len(dn) > 1:
                ops.append(band_op(up + dn[::-1], th["band"][si % len(th["band"])]))
    for t in ticks:
        ty = y + plot_h - (t - tmin) / span * plot_h
        ops.append(hline(px, ty, pw, th["rule_soft"] if t != tmin else th["rule"]))
        ops.append(text(x, ty - 6, lab_w - 7, 12, fmt(t, unit), TYPE["meta"], th["ink3"],
                        align="r", font="mono"))
    ops += _baseline_ops(spec, th, px, pw, y, plot_h, tmin, span, unit)
    for si, (name, vals) in enumerate(series):
        color = th["series"][si % len(th["series"])]
        pts = [pt(i, v) for i, v in enumerate(vals) if v is not None]
        if not pts:
            continue
        ops.append(poly(pts, color, 1.8 if si == 0 else 1.4))
        lx, ly = pts[-1]
        ops.append(rect(lx - 2.2, ly - 2.2, 4.4, 4.4, color, 2.2))
        ops.append(text(lx + 8, ly - 6, end_w - 9, 13, name, TYPE["meta"], color, valign="m"))
    step = max(1, int(math.ceil(len(labels) / 8.0)))
    xlabel = spec.get("xlabel")
    # reserve the axis-name strip and drop any tick that would run into it
    guard = px + pw - (core.measure(xlabel, TYPE["meta"]) + 12 if xlabel else 0)
    for i in range(0, len(labels), step):
        cx = px + pw * (i / n)
        if xlabel and cx + core.measure(labels[i], TYPE["meta"]) / 2 > guard:
            continue
        ops.append(text(cx - 28, y + plot_h + 6, 56, 12, labels[i],
                        TYPE["meta"], th["ink3"], align="c", font="mono"))
    if xlabel:
        ops.append(text(px, y + plot_h + 6, pw, 12, xlabel, TYPE["meta"], th["ink3"], align="r"))
    return ops


def _matrix(spec, box, th, base_dir):
    x, y, w, h = box
    labels, series, _ = load_series(spec, base_dir)
    unit = spec.get("unit", "")
    cols = [name for name, _ in series]
    grid = [[series[c][1][r] for c in range(len(cols))] for r in range(len(labels))]
    flat = [v for row in grid for v in row if v is not None]
    lo = spec.get("min", min(flat) if flat else 0.0)
    hi = spec.get("max", max(flat) if flat else 1.0)
    span = (hi - lo) or 1.0
    lab_w = min(160.0, max(70.0, max((core.measure(s, TYPE["small"]) for s in labels), default=70.0) + 10))
    head_h = 20.0
    gap = 2.5
    cw = (w - lab_w - gap * (len(cols) - 1)) / max(1, len(cols))
    ch = (h - head_h - gap * (len(labels) - 1)) / max(1, len(labels))
    best = spec.get("mark_best", True)
    ops = []
    for c, name in enumerate(cols):
        ops.append(text(x + lab_w + c * (cw + gap), y, cw, head_h - 5, name,
                        TYPE["meta"], th["ink2"], align="c", valign="b"))
    for r, rname in enumerate(labels):
        ry = y + head_h + r * (ch + gap)
        row = [v for v in grid[r] if v is not None]
        top = max(row) if row and best else None
        ops.append(text(x, ry, lab_w - 8, ch, rname, TYPE["small"], th["ink2"], valign="m"))
        for c in range(len(cols)):
            v = grid[r][c]
            cx = x + lab_w + c * (cw + gap)
            k = 0.0 if v is None else max(0.0, min(1.0, (v - lo) / span))
            shade = th["heat"][min(len(th["heat"]) - 1, int(k * len(th["heat"])))]
            ops.append(rect(cx, ry, cw, ch, shade, 2.0))
            ops.append(text(cx, ry, cw, ch, fmt(v, unit), TYPE["small"],
                            th["bg"] if k > 0.62 else th["ink"], align="c", valign="m", font="mono"))
            if top is not None and v == top:
                ops.append(rect(cx, ry + ch - 2, cw, 2, th["accent_deep"]))
    return ops
