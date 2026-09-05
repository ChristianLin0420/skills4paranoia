"""CLI: deck.md -> deck.pptx (+ optional SVG preview)."""
import argparse
import os
import sys

from . import charts, core, layouts, parser, render_pptx, render_svg, strings, validate


def compile_deck(deck, theme):
    slides = list(deck["slides"])
    has_evidence = any(s["layout"].startswith("E") for s in slides)
    if has_evidence and not any(s["layout"] == "D" for s in slides):
        idx = max((i for i, s in enumerate(slides) if s["layout"] in ("P1", "P2", "P3")), default=-1)
        if idx >= 0:
            n = sum(1 for s in slides if s["layout"].startswith("E"))
            st = strings.pick(deck["meta"].get("lang"))
            div = parser._new_slide("D", "", slides[idx]["line"])
            div["title"] = st["divider_title"]
            div["subtitle"] = st["divider_sub"] % n
            slides.insert(idx + 1, div)
    deck = dict(deck, slides=slides)

    ops_per_slide = []
    page = 0
    for slide in slides:
        if slide["layout"] not in ("F0", "D"):
            page += 1
        ctx = {"th": theme, "meta": deck["meta"], "base_dir": deck["base_dir"],
               "s": strings.pick(deck["meta"].get("lang")),
               "page": page if slide["layout"] not in ("F0", "D") else None}
        try:
            ops_per_slide.append(layouts.render_slide(slide, ctx))
        except charts.ChartError as exc:
            raise SystemExit("行 %d（%s）: %s" % (slide["line"], slide["name"], exc))
    return deck, ops_per_slide


def main(argv=None):
    ap = argparse.ArgumentParser(prog="deckkit", description="deck.md → Keynote 可編輯的 .pptx")
    ap.add_argument("source", help="輸入的 deck.md")
    ap.add_argument("-o", "--out", help="輸出 .pptx（預設與輸入同名）")
    ap.add_argument("--theme", help="配色主題名或 json 路徑，預設讀 front-matter 的 theme")
    ap.add_argument("--typeface", help="字體組：plex / plex-full / inter / system")
    ap.add_argument("--preview", nargs="?", const="", help="另外輸出 SVG 預覽 html")
    ap.add_argument("--check", action="store_true", help="只做結構檢查，不產檔")
    ap.add_argument("--force", action="store_true", help="有錯誤也照樣產檔")
    args = ap.parse_args(argv)

    try:
        deck = parser.parse_file(args.source)
    except (parser.DeckError, OSError) as exc:
        print("解析失敗：%s" % exc, file=sys.stderr)
        return 2

    issues, problems = validate.check(deck)
    text, errors = validate.report(issues)
    print(text)
    if problems:
        print("\n問題佐證統計")
        for key, info in sorted(problems.items()):
            print("  %s  %-26s %d 個小問題  %d 頁佐證" % (
                key, validate._clip(info["text"], 24), info["subs"], info["cited"]))
    if args.check:
        return 1 if errors else 0
    if errors and not args.force:
        print("\n%d 個錯誤，未產生檔案。修正後重跑，或加 --force 強制輸出。" % errors, file=sys.stderr)
        return 1

    theme = core.load_theme(args.theme or deck["meta"].get("theme") or "slate-blue",
                            args.typeface or deck["meta"].get("typeface") or "plex")
    deck, ops = compile_deck(deck, theme)

    out = args.out or os.path.splitext(args.source)[0] + ".pptx"
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    render_pptx.build(deck, ops, theme, out)
    print("\n產出  %s  (%d 頁, %s + %s)" % (out, len(deck["slides"]), theme["name"],
                                             theme["typeset"]))

    if args.preview is not None:
        prev = args.preview or os.path.splitext(out)[0] + ".preview.html"
        render_svg.build(deck, ops, theme, prev)
        print("預覽  %s" % prev)
    return 0


if __name__ == "__main__":
    sys.exit(main())
