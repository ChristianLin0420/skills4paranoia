# research

做研究本身用的 skill。與 `work/`（溝通與記錄）分開。

| Skill | 管什麼 | 何時用 |
|---|---|---|
| [`experiment-design`](experiment-design) | 開跑前拷問設計，把評估協定釘死 | 花掉算力之前 |
| [`vla-code-review`](vla-code-review) | 專找不會拋錯只會讓數字變差的工程層錯誤 | 開跑前，或重現不出數字時 |

兩個互補：一個管「你有沒有定義清楚什麼叫做對」，一個管「code 有沒有偷偷做錯」。開跑前兩個都跑。

## experiment-design

六個欄位缺一不可：要回答的是非題、匹配預算的基準、主指標與最小可偵測差異、什麼結果算 null、停止與決策規則、最可能白跑的原因。

最會被跳過的是「什麼算 null」。跳過它的代價不是少一份文件，是**跑完之後你一定找得到某個切片是贏的**。

裡面有一張 seed 數與可偵測差異的對照表。大部分 VLA 論文報 3 個 seed 然後宣稱 2–3 個百分點的改進 —— 在 σ=4pp 之下，3 個 seed 只能偵測 9.1 個百分點以上的差異。

## vla-code-review

這類錯的共同特徵：訓練跑得完、loss 曲線正常、沒有錯誤訊息，但最後的數字比它該有的低幾個百分點，然後被誤診成方法不夠好。

清單十一類約 60 項，涵蓋精度與學習率的交互作用、GPU 對 dtype 的支援、混合精度正確性、凍結與參數群組、seed 與決定性、資料與評估正確性、RL 與 VLA 特有的陷阱、訓練監控、復現、效能。

`reference/precedents.md` 把每條檢查掛到真實 repo 出貨過的 bug —— OpenVLA 的評估環境跨 episode 漂移、OpenVLA-OFT 的 DDP 梯度沒同步、LeRobot 的 checkpoint 靜默載入失敗、openpi 的 JAX 與 PyTorch 精度落差。看到新案例就往裡加，清單會隨時間變強。
