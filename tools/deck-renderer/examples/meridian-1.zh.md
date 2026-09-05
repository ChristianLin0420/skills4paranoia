---
title: Meridian-1 進度回顧
running: Meridian-1 · Q3
subtitle: 架構凍結與 Q4 算力配置提案
author: Your Name
team: Robotics Learning
date: 2026-09-05
lang: zh
theme: slate-blue
typeface: plex
footer: 範例文件 · 所有數據皆為虛構
contact: you@example.com
---

<!-- F0 cover -->

<!-- P1 problem -->
# 機器人策略要在沒見過的任務上可靠執行，但每個新任務的示範資料成本是線性成長的
- Q1 | 樣本效率：每個新任務都要重新收集數千筆示範 | 真實示範約 $40/筆，20 個任務就是 $1.7M | 模擬資料便宜但有 sim2real 落差 | 資料需求隨任務數線性成長，不會攤提
- Q2 | 泛化：訓練分布外的成功率崩掉 | 材質與光照一變就失效 | 長時序任務在第二個子目標後遺失上下文 | 接觸豐富的任務缺力回饋訊號
- Q3 | 可部署性：推論延遲吃不下閉環控制 | 視覺編碼佔掉一半以上延遲 | p99 抖動未量測，安全邊界估不出來 | diffusion 方法 23ms/step，撐不到 30Hz
> 不解決的話，每個新任務都是一次從零開始的資料工程專案。

<!-- P2 solution -->
# 用共享的世界模型把「學物理」和「學任務」拆開，任務端只學殘差
![Meridian-1：凍結視覺編碼器、跨任務共享世界模型、輕量動作解碼器](figures/arch.png)
- Q1 | 世界模型跨任務共享，動作解碼器只學殘差；視覺編碼器凍結，只微調 adapter | 可訓練參數 11%，達標示範數 4200 → 510
- Q2 | 模擬 rollout 以 4:1 混入並隨機化材質與光照；context window 覆蓋整段 episode | held-out 12 類任務平均 68%
- Q3 | 凍結後的視覺編碼器可量化，世界模型在推論時只前向一次 | 11ms/step，閉環 28Hz
~ 三個機制彼此獨立，可以個別關閉做消融，見第 09 頁的 Δ 欄。

<!-- P3 results -->
# 三個機制都生效，長時序仍是唯一沒解掉的
## 同一組權重，未做任何 per-task 微調
| 方法 | 達標示範數 | 未見任務 | 長時序 | 延遲 | 穩定度 |
| --- | --- | --- | --- | --- | --- |
| Baseline BC | 4200 | 31% | 8% | 7ms | 71% |
| Diffusion baseline | 1750 | 41% | 19% | 23ms | 84% |
| Meridian-1 | *510 | *68% | *34% | *11ms | *92% |
```chart
type: line
data: data/curves.csv
band: std
unit: "%"
xlabel: 環境互動步數
note: "20 個 held-in 任務的成功率"
```
~ TaskSuite-20 · 3 seeds · ±1σ · A100×8 · rollouts=100/task · 「長時序」為 >200 步任務子集。

<!-- E01 section index=01 -->
# 樣本效率
## Q1 的佐證：訓練曲線、達標成本、資料規模律、消融

<!-- E18 setup solves=Q1 eyebrow="實驗設定" -->
# 三個方法用的是同一套訓練與評估協定
- 模型 | params=1.24B | vision=ViT-L/14 frozen | action head=6-layer | ctx=256
- 資料 | demos=51k | tasks=20 | sim:real=4:1 | aug=colour+material
- 訓練 | optim=AdamW | lr=3e-4 | bs=256 | steps=200k | warmup=2k
- 評估 | rollouts=100/task | seeds=3 | horizon=200 | hw=A100×8
~ 除了 backbone 以外所有超參數在三個方法之間完全相同；差異僅來自架構本身。

<!-- E11 curves solves=Q1 source="runs/2026-08/curves.csv" -->
# 同樣的資料量，Meridian-1 收斂到 78%
## 陰影為 3 個 seed 的 ±1σ
```chart
type: line
data: data/curves.csv
band: std
unit: "%"
xlabel: 環境互動步數
baseline: {value: 56, label: "Diffusion baseline 收斂點"}
note: "success rate on 20 held-in tasks · rollouts=100/task"
```
- 分岔點在 50k 步 | 在那之前三條線幾乎重疊，效率差異不是來自初始化或前期探索
- Diffusion baseline 在 125k 後走平 | Meridian-1 仍在爬，代表資料還沒吃滿，加資料還有空間
- ±1σ 帶在 100k 後收窄 | 三個 seed 行為一致，不是單一 run 的僥倖
~ TaskSuite-20 · 3 seeds · ±1σ · A100×8 · 每點為 100 次 rollout 的成功率。

<!-- E17 panels solves=Q1 -->
# 資料規模律與時序衰減
```chart
type: line
title: 成功率 vs 示範資料量
data: data/scaling.csv
band: std
unit: "%"
xlabel: demos
note: "log 間距取樣，未做 early stop"
```
```chart
type: line
title: 成功率 vs 任務時序長度
data: data/horizon.csv
band: std
unit: "%"
xlabel: 任務步數
baseline: {value: 55, label: "Q4 門檻"}
note: "同一組權重，未做 per-horizon 微調"
```
- 資料規模仍在線性區 | 2k→51k 沒有出現飽和，Q4 加資料的假設成立
- 衰減在 200 步後轉陡 | 不是漸進退化，是某個機制在該長度失效
- 兩張圖同一組權重 | 所以右圖的衰減不能用「沒針對長時序訓練」解釋
~ 兩張圖用同一批權重（step=200k, seed 平均）；右圖顯示衰減在 200 步後轉陡，這是 Q4 的主要風險。

<!-- E06 chart-full solves=Q1 source="達到 60% 成功率所需的人類示範數量" -->
# 達標成本降到不到三分之一
```chart
type: bar
labels: [Baseline BC, Diffusion baseline, Meridian-1]
values: [4200, 1750, 510]
highlight: 2
delta: pct
note: "demos required to reach 60% mean success"
```
- 資料量降到不足三分之一 | 510 對照 4200，差距大到不需要統計檢定
- 來自世界模型而非規模 | 見消融頁，單純放大 backbone 只換到 7 個百分點
- ±8% 誤差不影響結論 | 取最壞估計仍低於 baseline 的六分之一
~ 以二分搜尋逼近達標所需資料量，每個資料點重跑 3 seeds，誤差 ±8%。

<!-- E19 ablation solves=Q1 delta=成功率 best=max source="200k steps，其餘設定同第 06 頁" -->
# 消融：效率來自共享世界模型，不是來自更大的 backbone
| 變體 | 參數量 | 訓練時數 | 成功率 |
| --- | --- | --- | --- |
| Baseline BC | 0.31B | 42 | 31% |
| + 更大 backbone | 1.24B | 128 | 38% |
| + 共享世界模型 | 1.20B | 96 | 64% |
| + 模擬混入 4:1 | *1.24B | *104 | *78% |
- 更大的 backbone 只換到 7 點 | 參數量翻四倍、訓練時數翻三倍，成功率只從 31% 到 38%
- 世界模型才是主要來源 | 參數量反而更少，成功率一次跳到 64%
- 模擬混入再加 14 點 | 訓練時數只多 8 小時，是三個機制裡性價比最高的
~ Δ 欄為對第一列的百分點差；訓練時數為 A100×8 的 wall-clock。

<!-- E14 architecture solves=Q1 -->
# 效率來自哪裡
![Meridian-1 三段式架構：凍結視覺編碼器、共享世界模型、動作解碼器](figures/arch.png)
共享的世界模型讓動作解碼器不必重新學習物理。
視覺編碼器凍結，只微調 adapter，可訓練參數量降到 11%。
示範資料以 4:1 混入模擬 rollout，緩解真實資料稀缺。
~ 圖中虛線為僅在訓練時存在的路徑；推論時世界模型只前向一次。

<!-- E01 section index=02 -->
# 泛化
## Q2 的佐證：任務矩陣、失敗歸因、rollout

<!-- E12 matrix solves=Q2 source="每格為 100 次 rollout 的成功率，粗線標記該列最佳" -->
# 未見任務的成功率矩陣
## 縱軸為 held-out 任務，訓練時完全未出現
```chart
type: matrix
data: data/matrix.csv
unit: "%"
note: "held-out tasks · 100 rollouts each · seed-averaged"
```
- 前四類任務全部過 60% | 這些是接觸較少、時序較短的任務
- 插入類是唯一有物理原因的落後 | 61%，缺的是力回饋不是視覺
- 長時序 34% 且三法皆低 | 這不是方法差異，是問題本身還沒被解決
~ 同一組權重，未做任何 per-task 微調；長時序任務（最後一列）是唯一未過 50% 的類別。

<!-- E07 chart-side solves=Q2 source="12 個 held-out 任務的失敗歸因" -->
# 剩下的失敗集中在兩種情況
接觸豐富的插入類任務仍然吃虧，主因是力回饋訊號在示範資料裡幾乎缺席。
長時序任務的失敗多發生在第二個子目標之後，模型會遺失早期上下文。
其餘失敗多屬感知邊緣案例，可用資料增強處理。
```chart
type: bar-h
labels: [長時序遺忘, 接觸力控制, 感知邊緣案例, 其他]
values: [41, 28, 19, 12]
unit: "%"
note: "n=384 failed rollouts, 人工歸因，兩人獨立標註"
```
~ 標註者間一致率 κ=0.81；不一致的 7% 歸入「其他」。

<!-- E03 solves=Q2 -->
# 三個確認過的失敗模式
## 各自都有對應的下一步，不需要動架構
- 子目標之後遺失上下文 | 加長 context window 到 512，估計成本 +7% 訓練時數
- 接觸力控制不足 | 補 8k 筆帶力回饋的示範資料，已與硬體團隊排程
- 反光與透明物體感知失效 | 資料增強加上材質隨機化，不需新資料

<!-- E13 filmstrip solves=Q2 source="Long-horizon tidy，成功 rollout，每 40 步取一幀" -->
# 一次成功的長時序 rollout
![t=0](figures/roll0.png)
![t=40](figures/roll1.png)
![t=80](figures/roll2.png)
![t=120](figures/roll3.png)
![t=160](figures/roll4.png)
~ 此為 34% 成功案例中的一次；失敗案例通常在 t=80 之後放開物件。

<!-- E20 figure solves=Q2 source="實機錄影截圖，非模擬環境" -->
# 失敗都發生在同一個瞬間：第二個子目標交接的那一幀
![四個失敗 rollout 的疊圖，方框標出鬆手的位置](figures/failure_grid.png)
- 失敗集中在同一幀 | 不是隨機失敗，是特定時間點的系統性錯誤
- 都發生在鬆手瞬間 | 指向抓取力控制，而非感知或規劃
- 四個案例物件都不同 | 所以不是特定物件的幾何問題
~ 從 384 次失敗中挑出的四個代表案例；此圖為實機錄影截圖，沒有底層數值可重畫，故直接置入。

<!-- E01 section index=03 -->
# 部署
## Q3 的佐證：延遲拆解、路線取捨、時程

<!-- E10 solves=Q3 source="1000 次連續前向取中位數，已排除 warmup" -->
# 延遲拆解：視覺編碼仍是最大的一塊
| 階段 | 中位數 | p99 | 佔比 | 可壓縮性 |
| --- | --- | --- | --- | --- |
| 視覺編碼 | 4.2ms | 5.1ms | 38% | 高，可 INT8 |
| 世界模型前向 | 3.6ms | 4.4ms | 33% | 中 |
| 動作解碼 | 1.9ms | 2.3ms | 17% | 低 |
| 通訊與安全檢查 | 1.3ms | 2.5ms | 12% | 低 |
| *合計 | *11.0ms | *14.3ms | *100% | — |
- 視覺編碼佔 38% | 是唯一有明確壓縮空間的一塊，INT8 估計可再省四成
- p99 只比中位數高 30% | 抖動可控，安全邊界取 2× p99 仍在 30Hz 預算內
- 通訊與安全檢查壓不動 | 那 1.3ms 是硬性成本，不要花力氣在上面
~ A100 batch=1 · 1000 次前向 · 閉環 28Hz，安全邊界取 p99 的兩倍。

<!-- E10 solves=Q3 source="以 64 張 H100 兩個月為基準估算" -->
# 兩條部署路線的取捨
## 建議先走 A，B 留作 Q1 選項
| 項目 | A：凍結架構擴資料 | B：繼續架構搜索 |
| --- | --- | --- |
| 產出時間 | *8 週 | 20 週以上 |
| 算力成本 | *128 GPU-月 | 800 GPU-月 |
| 長時序預期 | *55% | 60%，變異大 |
| 若失敗的退路 | *資料可留用 | 架構分支難回收 |
- A 的時間是 B 的五分之二 | 8 週對 20 週，且風險集中在可控的資料品質
- B 的算力是 A 的六倍 | 800 對 128 GPU-月，會直接排擠實機團隊
- A 失敗仍有殘值 | 產出的資料下一季可留用，B 的架構分支廢棄後難回收

<!-- E04 solves=Q3 -->
# 兩條路線的實際差別
- 凍結架構擴資料 | 8 週交付，風險集中在資料品質 | 產出的資料 Q1 仍可用 | 需要 infra 在 9/20 前給出配額
- 繼續架構搜索 | 20 週以上，風險分散但不可控 | 分支一旦廢棄難回收 | 會排擠實機團隊的算力

<!-- E09 solves=Q3 -->
# Q4 的四個檢查點
- 10 月中 | 資料規模 ×3，長時序成功率過 42%
- 11 月初 | 力回饋資料補齊，插入類任務過 70%
- 11 月底 | 實機閉環連續運行 8 小時無干預
- 12 月中 | 長時序過 55%，否則重啟架構討論
