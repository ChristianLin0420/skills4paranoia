"""Structural rules for the front-loaded research deck.

The first three pages are the whole argument: what problem, how we solve it,
how far we got. Everything after them is evidence, and evidence that addresses
no sub-problem is deleted rather than tolerated. These are checks, not
suggestions — `build.py` refuses to write a deck with any ERROR.
"""
from . import core
from .layouts import PROBLEM_KEYS, problem_parts
from .parser import split_fields

MAX_BULLETS = 5
MAX_PROBLEMS = 4

# Structural pages carry no argument of their own, so they address no problem.
NO_CLAIM_NEEDED = {"E01", "E16"}
NEEDS_CHART = ("E06", "E07", "E11", "E12")
NEEDS_FOOTNOTE = ("E06", "E07", "E11", "E12", "E17", "E19", "E20", "E21")
NEEDS_IMAGE = {"E20": 1, "E21": 2, "E14": 1, "E15": 1}


def check(deck):
    slides = deck["slides"]
    issues = []
    body = [s for s in slides if s["layout"] != "F0"]
    order = [s["layout"] for s in slides if s["layout"] in ("P1", "P2", "P3")]
    if order != ["P1", "P2", "P3"]:
        issues.append(("ERROR", None,
                       "前三頁必須依序是 P1 問題 / P2 解法 / P3 成果，目前是 %s" %
                       (" → ".join(order) or "（缺）")))
    for want, s in zip(("P1", "P2", "P3"), body[:3]):
        if s["layout"] != want:
            issues.append(("ERROR", s["line"],
                           "第 %d 張應為 %s，實際是 %s（佐證不得插進前三頁）" %
                           (body.index(s) + 1, want, s["layout"])))

    problems = {}
    p1 = next((s for s in slides if s["layout"] == "P1"), None)
    if p1 is not None:
        if not p1["title"]:
            issues.append(("ERROR", p1["line"], "P1 缺少那個大問題（用 # 開頭那行）"))
        elif len(core.wrap_text(p1["title"], 23.0, core.CW)) > 2:
            issues.append(("WARN", p1["line"], "P1 的大問題過長，兩行講不完就還沒收斂"))
        if not p1["bullets"]:
            issues.append(("ERROR", p1["line"], "P1 至少要把大問題拆成一個中問題"))
        if len(p1["bullets"]) > MAX_PROBLEMS:
            issues.append(("ERROR", p1["line"],
                           "P1 中問題上限 %d 個，目前 %d 個" % (MAX_PROBLEMS, len(p1["bullets"]))))
        for i, raw in enumerate(p1["bullets"][:MAX_PROBLEMS]):
            key, headline, subs = problem_parts(raw, i)
            problems[key] = {"text": headline, "subs": len(subs), "cited": 0, "solved": False}
            if not headline:
                issues.append(("ERROR", p1["line"], "%s 沒有中問題描述" % key))
            if not subs:
                issues.append(("WARN", p1["line"],
                               "%s 沒有拆出小問題，中問題底下應該有具體的技術障礙" % key))

    p2 = next((s for s in slides if s["layout"] == "P2"), None)
    if p2 is not None:
        if not p2["title"]:
            issues.append(("ERROR", p2["line"], "P2 缺少一句話解法（用 # 開頭那行）"))
        for raw in p2["bullets"]:
            key, mech, _metric = split_fields(raw, 3)
            key = key.strip().upper()
            if key in problems:
                problems[key]["solved"] = True
            elif key:
                issues.append(("ERROR", p2["line"], "P2 對應了未宣告的問題 %s" % key))
            if not mech:
                issues.append(("WARN", p2["line"], "P2 每列格式為「Q編號 | 機制 | 關鍵數字」"))
        for key, info in sorted(problems.items()):
            if not info["solved"]:
                issues.append(("ERROR", p2["line"],
                               "%s「%s」在 P2 沒有對應的解法" % (key, _clip(info["text"]))))

    p3 = next((s for s in slides if s["layout"] == "P3"), None)
    if p3 is not None:
        if not p3["table"]:
            issues.append(("ERROR", p3["line"],
                           "P3 需要一張成果表（方法 × 指標）。單獨幾個大數字不算成果展示"))
        elif len(p3["table"].get("cols") or []) < 3:
            issues.append(("WARN", p3["line"], "P3 成果表少於 3 欄，資訊密度偏低"))
        if not p3["footnote"]:
            issues.append(("WARN", p3["line"], "P3 沒有實驗條件註腳（用 `~ ` 開頭那行）"))

    for s in slides:
        if not s["layout"].startswith("E"):
            continue
        keys = _keys(s["attrs"].get("solves") or s["attrs"].get("supports"))
        if not keys and s["layout"] not in NO_CLAIM_NEEDED:
            issues.append(("ERROR", s["line"],
                           "%s 沒有宣告 solves=，佐證不得孤立存在" % s["layout"]))
        for key in keys:
            if key in problems:
                problems[key]["cited"] += 1
            else:
                issues.append(("ERROR", s["line"], "%s 對應了未宣告的問題 %s" % (s["layout"], key)))
        if len(s["bullets"]) > MAX_BULLETS:
            issues.append(("WARN", s["line"],
                           "%s 有 %d 條列，上限 %d" % (s["layout"], len(s["bullets"]), MAX_BULLETS)))
        if s["layout"] in NEEDS_CHART and not s["chart"]:
            issues.append(("ERROR", s["line"], "%s 需要一個 ```chart 區塊" % s["layout"]))
        if s["layout"] == "E17" and len(s["charts"]) < 2:
            issues.append(("ERROR", s["line"], "E17 需要 2–4 個 ```chart 區塊"))
        if s["layout"] == "E18" and not s["bullets"]:
            issues.append(("ERROR", s["line"], "E18 需要至少一組設定（`- 群組 | 鍵=值 | …`）"))
        want_img = NEEDS_IMAGE.get(s["layout"])
        if want_img and len(s["images"]) < want_img:
            issues.append(("ERROR", s["line"],
                           "%s 需要 %d 張圖（用 ![說明](path) 指定）" % (s["layout"], want_img)))
        if s["layout"] in ("E10", "E19") and not s["table"]:
            issues.append(("ERROR", s["line"], "%s 需要一個表格" % s["layout"]))
        if s["layout"] in NEEDS_FOOTNOTE and not s["footnote"]:
            issues.append(("WARN", s["line"],
                           "%s 沒有實驗條件註腳（用 `~ ` 開頭寫 n=／seeds／硬體）" % s["layout"]))

    for key, info in sorted(problems.items()):
        if info["cited"] == 0:
            issues.append(("ERROR", p1["line"] if p1 else None,
                           "問題 %s「%s」沒有任何佐證頁對應" % (key, _clip(info["text"]))))
    return issues, problems


def _keys(s):
    return [p.strip().upper() for p in str(s or "").replace(",", " ").split() if p.strip()]


def _clip(s, n=18):
    s = str(s)
    return s if len(s) <= n else s[:n] + "…"


def report(issues):
    errors = sum(1 for lvl, _l, _m in issues if lvl == "ERROR")
    lines = []
    for lvl, line, msg in issues:
        lines.append("%-5s %s%s" % (lvl, msg, "  行 %d" % line if line else ""))
    if not issues:
        lines.append("OK    結構檢查全數通過")
    return "\n".join(lines), errors
