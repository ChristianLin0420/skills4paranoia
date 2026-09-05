---
name: vla-code-review
description: 審查 VLA / WAM / RL 訓練與評估程式碼，專找不會拋錯、只會讓數字變差的工程層錯誤：精度與學習率不匹配、GPU 不支援的 dtype、DDP 梯度沒同步、checkpoint 靜默載入失敗、評估環境狀態外洩、成功判準過寬。產出一份可視化的審查報告。Use when reviewing a robot-learning, VLA, world-model or RL codebase before launching an expensive training run, or when reproduced numbers do not match expectations.
---

# vla-code-review

專找**不會拋錯、只會讓數字變差**的錯。方法本身的問題不在範圍內 —— 那是研究者的專業。這個 skill 負責的是「方法對了但實作把它吃掉了」的那一類。

這類錯的共同特徵：訓練跑得完、loss 曲線看起來正常、沒有任何錯誤訊息，但最後的數字比它該有的低幾個百分點，然後被誤診成方法不夠好。`reference/precedents.md` 裡每一條都是知名 repo 實際出貨過的。

## 1. 三種結果，不准有第四種

```
[通過]   2.6 clip 在 unscale 之後        train.py:214
[發現]   4.4 DDP 被 .module 繞過         train.py:388
         action head 的梯度不會 all-reduce
[不適用] 7.1 truncation vs termination   此 codebase 不是 RL
```

**不確定的一律歸「發現」並附行號，讓人判斷。** 這份清單抓的是「看起來對的錯」，最大的失敗模式是 agent 因為程式碼讀起來合理就標通過。標錯成通過的代價是使用者信了然後燒掉兩個月；標錯成發現的代價是他花三分鐘確認。這兩個不對等。

沒查到的項目要明講「沒查」，不要留白。空白會被當成通過。

## 2. 順序

**先跑 Tier 0。** `reference/checklist.md` 開頭那十題，每一題單獨成立就足以讓整批實驗白跑。任何一題未通過，報告的判決就是「不要開跑」，其餘發現排在後面。

**再逐類掃過十一個分類。** 精度與硬體、精度與學習率、混合精度正確性、凍結與參數群組、seed 與決定性、資料與評估正確性、RL 特有、VLA/WAM 特有、訓練穩定與監控、checkpoint 與復現、效能陷阱。

**不適用的整類標不適用。** 非 RL 的 codebase 就把第 7 類整類標掉，不要硬找。

**最後列出靜態檢查看不出來的。** 有五類項目要實際跑一次才知道（SDPA 實際走哪個 backend、權重零位移比例、種子是否覆蓋 dataloader worker、dataloader 是否餓到 GPU、是否走 NVLink）。這些要單獨列出來，不能混在通過裡。

## 3. 嚴重度

| 級別 | 意思 | 判準 |
|---|---|---|
| **阻斷** | 這批實驗的結論不可用 | 修好之前不要開跑，也不要相信已經跑出來的數字 |
| **高** | 數字被系統性影響 | 方向可能還對，但幅度不可信 |
| **中** | 影響可量測但有限 | 這一輪可以先跑，下一輪之前修掉 |
| **觀察** | 我不確定，需要你判斷 | agent 看到可疑之處但缺乏領域脈絡 |

**「觀察」是刻意留的出口。** agent 看得出成功判準沒有保持幀數要求，但不知道你的任務能不能接受。沒有這個級別，agent 會為了顯得有用而把猜測寫成發現。

## 4. 每條發現要有的欄位

- **症狀** —— 使用者會觀察到什麼。不要寫「這樣寫不對」，要寫「訓練後期停止進步但 grad norm 正常」。
- **成因** —— 為什麼會這樣。一兩句，要有機制不要只有標籤。
- **怎麼確認** —— **一個具體可執行的驗證動作**。比對兩個 rank 的參數雜湊、diff `body_pos`、統計零位移比例。這欄最重要，它讓使用者不必相信報告，可以自己查。
- **修法** —— 改什麼。
- **同型案例** —— 查 `reference/precedents.md`，有對應的就附公開 issue 連結。**沒有對應就不要附**，不要為了看起來有根據而硬掛不相關的連結。

## 5. 報告

`templates/report.html` 是可直接套用的模板，配色與字體跟 `research-deck` 同一套。格式規格見 `reference/report-format.md`。

結構由上而下：判決（一句人話，不是統計數字）→ 四格計數 → Tier 0 閘門表 → 發現（依嚴重度）→ 覆蓋矩陣 → 靜態查不到的部分。

**判決要寫成一句人話。** 不是「發現 7 個問題」，是「不要開跑，因為多卡的梯度沒同步而且 checkpoint 可能沒載進去，這批實驗的結論不可用」。使用者掃一眼就要知道要不要往下讀。

## 6. 收錄新案例

看到新的公開 issue 就往 `reference/precedents.md` 加。收錄標準：**公開、可驗證、而且是靜默失敗**。安裝錯誤、版本衝突、CUDA OOM 不收 —— 那些會自己報錯，不需要 review 來抓。

## 7. 檔案

- `reference/checklist.md` —— 十一類約 60 項，每項「症狀 → 怎麼查 → 正解」
- `reference/precedents.md` —— 每條檢查對應的真實案例
- `reference/report-format.md` —— 報告格式規格
- `templates/report.html` —— 可直接改的報告模板
