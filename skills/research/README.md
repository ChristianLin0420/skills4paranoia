# research

做研究本身用的 skill。與 `work/`（溝通與記錄）分開。

| Skill | 管什麼 |
|---|---|
| [`vla-code-review`](vla-code-review) | 審查 VLA / WAM / RL 訓練與評估程式碼，專找不會拋錯只會讓數字變差的工程層錯誤 |

## vla-code-review

這類錯的共同特徵：訓練跑得完、loss 曲線正常、沒有錯誤訊息，但最後的數字比它該有的低幾個百分點，然後被誤診成方法不夠好。

清單十一類約 60 項，涵蓋精度與學習率的交互作用、GPU 對 dtype 的支援、混合精度正確性、凍結與參數群組、seed 與決定性、資料與評估正確性、RL 與 VLA 特有的陷阱、訓練監控、復現、效能。

`reference/precedents.md` 把每條檢查掛到真實 repo 出貨過的 bug —— OpenVLA 的評估環境跨 episode 漂移、OpenVLA-OFT 的 DDP 梯度沒同步、LeRobot 的 checkpoint 靜默載入失敗、openpi 的 JAX 與 PyTorch 精度落差。看到新案例就往裡加，清單會隨時間變強。
