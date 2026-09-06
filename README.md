# skills4paranoia

Agent skills，依主題分層。純 markdown 規格，沒有要安裝的相依套件。

名字不是玩笑。這裡每一個 skill 做的都是同一件事：**強迫你證明那件你跳過的事**。

簡報 skill 不准你留下掛不到任何問題的頁；code review skill 專找不會拋錯、只會讓數字低幾個百分點的靜默失敗；實驗設計 skill 不准你在跑之前沒定義好什麼結果算失敗。這些紀律你本來就知道，只是趕的時候會跳過 —— 這個 repo 把它們變成擋得住的檢查。

```
skills/
  work/                     ← 主題：溝通與記錄
    research-deck/          ← skill
    deck-design-system/
    research-figures/
  research/                 ← 主題：做研究本身
    experiment-prereg/
    vla-code-review/
```

新增主題就在 `skills/` 底下開一個資料夾，把 skill 放進去，再把路徑加到 `.claude-plugin/plugin.json` 的 `skills` 陣列。不需要動其他東西。

## 安裝

兩條路，選一條就好，兩個都裝會拿到重複的 skill。

### Claude Code（受管、自動更新）

```bash
claude plugin marketplace add ChristianLin0420/skills4paranoia
claude plugin install skills4paranoia
```

或在 session 裡：

```
/plugin marketplace add ChristianLin0420/skills4paranoia
/plugin install skills4paranoia
```

### Codex 或其他 agent（可編輯的副本）

```bash
npx skills@latest add ChristianLin0420/skills4paranoia
```

安裝程式會問你要裝哪幾個 skill、裝到哪個 agent。想只裝一個：

```bash
npx skills@latest add ChristianLin0420/skills4paranoia --skill research-deck --agent claude-code
```

### 手動

```bash
git clone https://github.com/ChristianLin0420/skills4paranoia
cp -R skills4paranoia/skills/*/* ~/.claude/skills/
```

`skills/*/*` 會把所有 topic 底下的 skill 都攤平複製過去 —— agent 的 skill 目錄本身不分 topic，分層只存在於這個 repo 裡。只給單一專案用就複製到專案的 `.claude/skills/`。

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

### research

做研究本身用的 skill。

| Skill | 管什麼 |
|---|---|
| [`experiment-prereg`](skills/research/experiment-prereg) | 鎖死量測契約並凍結 |
| [`vla-code-review`](skills/research/vla-code-review) | 專找不會拋錯只會讓數字變差的工程層錯誤 |

兩個互補：一個管「你有沒有定義清楚什麼叫做對」，一個管「code 有沒有偷偷做錯」。

清單十一類約 60 項，從精度與學習率的交互作用到評估環境的狀態外洩。每條檢查都掛一個真實 repo 出貨過的案例，所以報告裡的發現有份量：「這裡可能有問題」和「openvla-oft#160 就是這個」是兩回事。

詳見 [skills/research/README.md](skills/research/README.md)。

## tools/

`tools/deck-renderer` 是一份可跑的 Python 參考實作（markdown → `.pptx` + SVG 預覽），**不是 skill 的一部分，安裝時不會被複製**。留著是因為 skill 裡那些幾何數值是從它來的，也可以拿來驗證 agent 產出的排版對不對。

```bash
cd tools/deck-renderer
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/python -m deckkit.build examples/meridian-1.zh.md -o out/deck.pptx --preview
```

## 授權

MIT
