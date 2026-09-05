# agent-skills

Agent skills，依主題分層。純 markdown 規格，沒有要安裝的相依套件。

```
skills/
  work/                     ← 主題
    research-deck/          ← skill
    deck-design-system/
    research-figures/
```

新增主題就在 `skills/` 底下開一個資料夾，把 skill 放進去，再把路徑加到 `.claude-plugin/plugin.json` 的 `skills` 陣列。不需要動其他東西。

## 安裝

兩條路，選一條就好，兩個都裝會拿到重複的 skill。

### Claude Code（受管、自動更新）

```bash
claude plugin marketplace add ChristianLin0420/agent-skills
claude plugin install christianlin-skills
```

或在 session 裡：

```
/plugin marketplace add ChristianLin0420/agent-skills
/plugin install christianlin-skills
```

### Codex 或其他 agent（可編輯的副本）

```bash
npx skills@latest add ChristianLin0420/agent-skills
```

安裝程式會問你要裝哪幾個 skill、裝到哪個 agent。想只裝一個：

```bash
npx skills@latest add ChristianLin0420/agent-skills --skill research-deck --agent claude-code
```

### 手動

```bash
git clone https://github.com/ChristianLin0420/agent-skills
cp -R agent-skills/skills/work/* ~/.claude/skills/
```

只給單一專案用就複製到專案的 `.claude/skills/`。

## 主題

### work

研究型簡報。三個互相引用、也可以分開用的 skill。

| Skill | 管什麼 |
|---|---|
| [`research-deck`](skills/work/research-deck) | 結構與流程：問題 → 解法 → 成果，以及佐證怎麼掛 |
| [`deck-design-system`](skills/work/deck-design-system) | 外觀：配色、字階、格線、字體、每個版式的精確幾何 |
| [`research-figures`](skills/work/research-figures) | 圖表：曲線與誤差帶、矩陣、消融表、參考線、條件註腳 |

核心主張是**前三頁講完全部，其餘都是佐證**：第一頁一個大問題拆成 2–4 個中問題，第二頁逐條對應解法，第三頁成果表（含還沒解掉的那一格）。第四頁起每一頁都要宣告 `solves=Qn`，掛不到任何問題的頁就刪掉。

詳見 [skills/work/README.md](skills/work/README.md)。

## tools/

`tools/deck-renderer` 是一份可跑的 Python 參考實作（markdown → `.pptx` + SVG 預覽），**不是 skill 的一部分，安裝時不會被複製**。留著是因為 skill 裡那些幾何數值是從它來的，也可以拿來驗證 agent 產出的排版對不對。

```bash
cd tools/deck-renderer
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/python -m deckkit.build examples/meridian-1.zh.md -o out/deck.pptx --preview
```

## 授權

MIT
