"""Chrome strings per deck language. Set `lang: zh` or `lang: en` in front-matter."""

STRINGS = {
    "zh": {
        "front_1": "問題 · 我們要解什麼",
        "front_2": "解法 · 我們怎麼解",
        "front_3": "成果 · 解到什麼程度",
        "divider_title": "以下為佐證",
        "divider_sub": "%d 頁，每頁對應前三頁的一個子問題",
        "solves": "對應 %s",
        "missing_file": "%s\n（檔案未找到）",
        "thanks": "謝謝",
        "baseline": "基準",
        "setup": "實驗設定",
        "delta": "Δ",
    },
    "en": {
        "front_1": "Problem · what we are solving",
        "front_2": "Solution · how we solve it",
        "front_3": "Results · how far we got",
        "divider_title": "Supporting evidence",
        "divider_sub": "%d pages, each tied to one sub-problem above",
        "solves": "addresses %s",
        "missing_file": "%s\n(file not found)",
        "thanks": "Thank you",
        "baseline": "baseline",
        "setup": "Setup",
        "delta": "Δ",
    },
}


def pick(lang):
    return STRINGS.get(str(lang or "zh").lower()[:2], STRINGS["zh"])
