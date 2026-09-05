---
name: deck-design-system
description: 簡報的設計規格：低飽和淺色配色、小字級高密度的字階、16:9 格線與精確幾何、IBM Plex 字體組。任何要產生或檢查投影片外觀的工作都先讀這份。Use when producing or reviewing slide visuals, deck colours, typography, or layout geometry.
---

# deck-design-system

規格不是建議。所有數值以 pt 為單位，畫布 960 × 540 pt（= 13.333 × 7.5 in，16:9），原點在左上。

做整份簡報時，`research-deck` 會在產檔前自動載入這份，使用者不需要單獨呼叫。單獨用的時機：檢查既有簡報的外觀、查色票 hex、加新版式時對照幾何。

## 1. 格線

| 位置 | y | 說明 |
|---|---|---|
| 頁首文字 | 38 | 左為版式標籤與 eyebrow，右為簡報名 |
| 頁首橫線 | 62 | 0.75pt |
| 內容區上緣 | 88 | 標題從這裡開始 |
| 內容區下緣 | 446 | 所有內容不得超過 |
| 條件註腳 | 452 | 9.5pt，寫 n=／seeds／硬體 |
| 頁尾橫線 | 476 | 0.75pt |
| 頁尾文字 | 483 | 左為出處，右為頁碼 |

左右邊界 56，內容寬 848。欄距 18–28，視欄數而定。

留白是結構不是裝飾：欄與欄之間留白，段與段之間用 0.75pt 細線而不是空行。

## 2. 字階

| 角色 | pt | 用在 |
|---|---|---|
| display | 34 | 封面標題 |
| statement | 26 | P1 的大問題那一句 |
| title | 21 | 一般頁標題 |
| subtitle | 13.5 | 副標 |
| lead | 15 | 條列主句 |
| body | 12.5 | 內文、表格主要欄位 |
| small | 11 | 表格儲存格、圖表標籤 |
| meta | 9.5 | 條件註腳、軸刻度、頁碼、Q 編號 |

行高：標題 1.26，內文 1.45，註腳 1.4。字距：標題 −0.2，大數字 −0.8，eyebrow +0.5，其餘 0。

只用兩個字重：Regular 與 Medium。**所有數字用等寬字**（表格、圖表、頁碼、Q 編號），這樣跨列才對得齊，也是研究簡報和行銷簡報最直接的視覺差別。

## 3. 配色

三套，一份簡報只用一套，不混。全部是淺色底、低飽和、灰階階梯加單一重點色。

### slate-blue（預設）

```
bg          F1F2F3      頁面底色
surface     FAFBFB      卡片
ink         14171A      主要文字
ink2        5F656B      次要文字
ink3        8A9096      註腳、軸刻度
rule        DCE0E3      主要細線
rule_soft   E8EBED      次要細線
accent      3A6183      唯一重點色（鋼藍）
accent_deep 27435C      重點色文字
accent_soft DBE4EB      標籤底
accent_wash EAF0F4      區塊底
ladder      20242A 4B5158 787E85 A6ACB2 CDD2D6    資料灰階階梯
series      3A6183 20242A 6E8FA8 787E85 A6ACB2    多數列
band        DDE5EB DFE1E3 E7ECF0 E5E7E8 EBEDEE    誤差帶
heat        EDF1F4 CFDCE6 A8C0D2 7C9EB8 3A6183    熱度五階
```

### linen（暖中性，對外簡報）

```
bg F4F1EB · ink 1E1D1A · ink2 6A665E · ink3 938E83
rule DFDAD0 · rule_soft E9E5DC · accent 4A6274 · accent_deep 334654
series 4A6274 7C8B6B B08A6B 6F6580 9C6B62
```

### mist（冷中性，技術與財務）

```
bg F1F3F5 · ink 16191D · ink2 5C6570 · ink3 89929C
rule DCE1E6 · rule_soft E9EDF0 · accent 3F6480 · accent_deep 2B4659
series 3F6480 5E8A80 7B7392 A98A66 8C5F5A
```

規則：

- 重點色只有一個，用在最重要的那一根柱、那一條線、那一格。其餘走灰階階梯。
- 資料顏色由主題決定，不在內容裡指定顏色。
- 不用漸層、陰影、外框、3D、emoji。
- 深色格子上的文字用 `bg` 色，不用純白。

## 4. 字體

字體與配色互不相干，各自獨立切換。

| 名稱 | 拉丁 | 中日韓 | 等寬 | 取得 |
|---|---|---|---|---|
| `plex`（預設） | IBM Plex Sans | Noto Sans TC | IBM Plex Mono | Google Fonts，OFL |
| `plex-full` | IBM Plex Sans | IBM Plex Sans TC | IBM Plex Mono | TC 需從 github.com/IBM/plex 取 |
| `inter` | Inter | Noto Sans TC | JetBrains Mono | Google Fonts，OFL |
| `system` | Helvetica Neue | PingFang TC | Menlo | macOS 內建，免安裝 |

選 IBM Plex 的理由：它本來就是為技術溝通設計的字族，克制但字形有辨識度；Plex Mono 讓密集數值對齊。

**.pptx 只記字型名稱**，開檔的機器沒裝就會被 Keynote 靜默替換、版面位移。要傳給沒裝字型的人（尤其 Windows）就改用 `system`。HTML 產出用 `<link>` 從 Google Fonts 取字，不需安裝。

## 5. 元件規格

**頁首**：左邊是 Q 編號標籤（`accent_soft` 底、`accent_deep` 字、9.5pt 等寬、圓角 2.5、左右內距各 7.5），接著 eyebrow（9.5pt、`ink2`、字距 +0.5）。右邊是簡報名（9.5pt、`ink3`、右對齊）。下方 62 處一條 `rule`。

**表格**：欄標題 9.5pt `ink2` 字距 +0.5，數值欄右對齊；標題列下方一條 `rule`，每列下方一條 `rule_soft`；列高 ≤32，數值用等寬字；`*` 前綴的儲存格用 `accent_deep`；標記最佳列時在左側 x−8 處畫一條 2.5 寬的 `accent` 直條。

**條列**：項目符號是 5pt 圓點，用 `series` 的對應色，不用符號字元。主句 15pt `ink`，補述 11pt `ink2`。上限 5 條。

**大數字**：只在解法頁的關鍵數字用，等寬、`accent_deep`、11pt。**不要做整頁只有大數字的版式** —— 那是宣傳頁。成果一律用表格。

**圖片缺檔**：畫一個 `accent_wash` 底、圓角 2.5 的框，中央置中寫檔名與「檔案未找到」，9.5pt `ink3`。不要留空白。

## 6. 檢查

1. 有沒有任何元素超出 88–446 的內容區？
2. 數字是不是全部用等寬字？
3. 重點色是不是只出現在一個地方？
4. 軸刻度有沒有涵蓋到資料的最大值？（刻度上限必須 ≥ 資料最大值，否則線會畫到框外）
5. 文字對比夠嗎？`ink3` 是最淺可用的文字色，不要再淺。
6. 有沒有漸層、陰影、emoji、Title Case？
