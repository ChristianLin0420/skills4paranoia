# VLA / WAM / RL 程式碼審查清單

專找**不會拋錯、只會讓數字變差**的工程層錯誤。方法本身的問題不在這份清單裡 —— 那是你的專業。這份負責的是「方法對了但實作把它吃掉了」的那一類。

每一項的格式：**症狀** → **怎麼查** → **正解**。

---

## Tier 0 — 開跑前三十分鐘必查

跑兩個月之前先過這八題。這幾項單獨一項就足以讓整批實驗白跑。

| # | 檢查 | 一句話 |
|---|---|---|
| 0.1 | 這張卡支不支援你設的精度 | bf16 需要 SM80+，fp8 需要 SM89/90 |
| 0.2 | master weights 是不是 fp32 | 純 bf16 訓練會讓小更新被靜默丟掉 |
| 0.3 | grad clip 有沒有在 unscale 之後 | 順序錯了 clip 閾值完全沒意義 |
| 0.4 | scheduler.step() 有沒有被 grad accumulation 多叫 | LR 排程跑快 N 倍 |
| 0.5 | 凍結的 encoder 有沒有 `.eval()` | `requires_grad=False` 擋不住 BN 統計與 dropout |
| 0.6 | 正規化統計是不是只用 train 算的 | 最常見的洩漏，且不會報錯 |
| 0.7 | truncation 與 termination 有沒有分開處理 | RL 最貴的 off-by-one |
| 0.8 | eval 的 seed 是不是獨立於訓練步數 | 否則不同 checkpoint 的比較是假的 |
| 0.9 | DDP 包裝後有沒有被 `.module` 繞過 | 梯度不會 all-reduce，多卡等於各學各的 |
| 0.10 | checkpoint 載入失敗會不會拋錯 | 靜默回傳未訓練模型，所有量測作廢 |

最後兩項是查了實際 repo 之後補的 —— 它們不是理論風險，是 OpenVLA-OFT 與 LeRobot 都出貨過的 bug。詳見 `precedents.md`。

---

## 1. 精度與硬體相容

**1.1 bf16 在不支援的卡上**
症狀：跑得動但慢得離譜，或在某些 kernel 上直接報錯。
查：`torch.cuda.get_device_capability()`，SM80 以下沒有原生 bf16（V100 是 SM70、T4 是 SM75）。A100=SM80、H100=SM90、RTX 4090=SM89。
正解：在啟動時 assert compute capability，不要靠 try/except 靜默降級。降級要印在 log 第一行。

**1.2 fp8 的門檻更高**
症狀：`transformer_engine` 匯入成功但 fp8 路徑沒被走到。
查：fp8 需要 SM89（Ada）或 SM90（Hopper）；A100 沒有。而且要確認 recipe（E4M3 前向 / E5M2 反向）真的生效。
正解：印出實際走的 kernel，不要只看設定檔。

**1.3 TF32 的預設值會變**
症狀：同一份 code 在兩台機器 / 兩個 PyTorch 版本上結果不同，差在小數點後三位，累積起來變成一兩個百分點。
查：`torch.backends.cuda.matmul.allow_tf32` 與 `torch.backends.cudnn.allow_tf32`。這兩個的預設值在 PyTorch 版本之間變過。
正解：**明確設定，不要靠預設**，並把設定值寫進 run config。跨 run 比較的前提是這兩個一致。

**1.4 SDPA 實際走了哪個 backend**
症狀：以為在用 FlashAttention，其實 fallback 到 math backend，慢 5–10 倍而且吃更多記憶體。
查：`torch.backends.cuda.sdp_kernel` 的 context，或用 profiler 看實際 kernel 名稱。head_dim 不被支援、有 attention mask、dtype 是 fp32 都會導致 fallback。
正解：在 smoke test 裡 assert 走到預期的 backend。

**1.5 Tensor core 對齊**
症狀：吞吐量莫名比預期低一半。
查：hidden dim、head dim、vocab size 是不是 8 的倍數（fp16/bf16）。1000 vs 1024 差很多。
正解：把維度湊到 8 或 64 的倍數，padding 的成本遠低於掉出 tensor core。

**1.6 `torch.compile` 的重編譯風暴**
症狀：前幾百步慢得詭異，或記憶體週期性暴增。
查：`TORCH_LOGS=recompiles`。變長序列、變動 batch size、Python 物件當條件都會觸發。
正解：固定 shape 或用 `dynamic=True`；把重編譯次數當成一個要監控的指標。

---

## 2. 精度與學習率的交互作用

這一節是你特別問的，也是最少人查的。

**2.1 純低精度訓練會讓小更新消失**
症狀：loss 卡住不動，或訓練後期完全不再進步，但 grad norm 看起來正常。
原理：bf16 的相對精度約 `2^-8`（約三個十進位有效位），fp16 約 `2^-11`。當 `|lr × grad| / |w| < 2^-8`，這次更新加上去之後權重不變，被靜默丟棄。訓練後期權重變大、梯度變小，這個條件很容易成立。
查：抽樣幾個參數，比較 `optimizer.step()` 前後的權重是否真的改變；統計「零位移」的參數比例。
正解：保留 fp32 master weights（AMP 預設就是這樣，純 bf16 訓練不是）。若堅持純 bf16，要用 stochastic rounding 或 Kahan 補償求和的 optimizer。

**2.2 Adam 的 eps 在低精度下歸零**
症狀：更新爆掉或出現 inf。
原理：fp16 的最小正規數約 `6e-5`、最小次正規數約 `6e-8`。預設 `eps=1e-8` 在 fp16 裡就是 0，分母失去保護。
查：optimizer state 的 dtype。
正解：optimizer state 保持 fp32，或把 eps 提到 `1e-6`。AMP 通常已經是 fp32 state，但自訂 optimizer 或 8-bit optimizer 要特別確認。

**2.3 LR warmup 被 GradScaler 吃掉**
症狀：warmup 期間看起來正常，但實際上前幾百步根本沒更新。
原理：fp16 初期容易溢位，GradScaler 偵測到 inf 就跳過該步。跳過的步數不會推進 optimizer，但 scheduler 若照樣 step，warmup 就等於沒發生。
查：記錄 scaler 的跳步次數與 scale 值。跳步率超過 5% 就是有問題；scale 一路掉到 1 表示持續溢位。
正解：只在 optimizer 真的 step 之後才推進 scheduler；把跳步率當成監控指標。

**2.4 梯度累積下的有效批次與 LR**
症狀：換了 accumulation step 數之後結果不可比。
查：`effective_batch = per_device × grad_accum × world_size`。LR 有沒有跟著調（線性或平方根縮放）？loss 有沒有除以 accumulation steps？
正解：把 effective batch 印在 log 裡，比較實驗時對齊的是它而不是 per-device batch。

**2.5 梯度累積用低精度累加**
症狀：accumulation steps 越多，結果越差。
原理：在 fp16 裡把 32 個小梯度加起來，後面幾個會被吃掉。
正解：累加緩衝區用 fp32。

**2.6 clip 與 unscale 的順序**
症狀：grad clip 看似生效（log 出來的 norm 都貼著閾值）但完全沒有保護作用。
原理：GradScaler 把梯度放大了 `S` 倍，此時 clip 到 1.0 等於實際 clip 到 `1.0/S`。
正解：`scaler.unscale_(optimizer)` → `clip_grad_norm_` → `scaler.step(optimizer)`。順序不能換。

**2.7 weight decay 套到不該套的參數**
症狀：訓練不穩，或 norm 層的 scale 被拉向 0。
查：optimizer param group 的切分。bias、LayerNorm/RMSNorm 的 weight 與 bias、embedding 通常要排除。
正解：兩個 param group，decay 與 no_decay 分開。

---

## 3. 混合精度的正確性

**3.1 normalization 沒有在 fp32 算**
症狀：長序列或大 batch 下數值飄移。
查：自訂的 LayerNorm / RMSNorm kernel 有沒有內部升到 fp32。autocast 會處理原生層，自訂 kernel 不會。
正解：在 norm 內部 `.float()` 再算，算完轉回。

**3.2 softmax / attention logits 溢位**
症狀：fp16 下偶發 NaN，bf16 下沒事。
原理：fp16 上限 65504，attention logits 在 head_dim 大或沒有 scale 時很容易超過。
正解：logits 減 max（標準做法，但自訂 kernel 常漏）、在 fp32 算 softmax。

**3.3 loss 在低精度計算**
症狀：小 loss 值的梯度失真。
正解：cross entropy、MSE 的 reduction 在 fp32 做。`autocast` 對 `F.cross_entropy` 有處理，自己寫的沒有。

**3.4 指標聚合用低精度**
症狀：成功率統計有 ±0.5% 的莫名抖動。
原理：把 100 個 0/1 在 fp16 裡累加，到後面 1 加不進去（fp16 在 2048 以上的整數就開始跳號）。
正解：所有 reduction 用 fp32 或 float64。這條特別重要因為它直接汙染你要報的數字。

---

## 4. 凍結、參數群組與 adapter

**4.1 凍結的 encoder 沒有 `.eval()`**
症狀：凍結了但結果還是會變，或 train / eval 表現落差異常大。
原理：`requires_grad=False` 只擋梯度，擋不住 **BatchNorm 更新 running stats**，也擋不住 **dropout**。ResNet encoder 特別致命。
查：`model.vision_encoder.training` 應為 False；BN 的 `running_mean` 在訓練前後應該完全不變。
正解：`requires_grad=False` + `.eval()`，而且要在每個 epoch 開頭重設（`model.train()` 會把整棵樹打開）。

**4.2 adapter / LoRA 參數不在 optimizer 裡**
症狀：LoRA 訓練跑完，權重跟初始化一模一樣。
原理：optimizer 建立時 adapter 還沒注入，param group 就空了。
查：`sum(p.numel() for g in opt.param_groups for p in g['params'])` 對不對得上你以為的可訓練參數量。
正解：先注入 adapter 再建 optimizer；並在啟動時印出可訓練參數量與佔比。

**4.4 DDP 包裝後被 `.module` 繞過**
症狀：不報錯，多卡與單卡的 loss 曲線幾乎一樣，但多卡最終表現不如預期，卡數越多差距越大。
原理：模組被 `DistributedDataParallel` 包起來，但程式呼叫 `head.module.predict(...)`。繞過 `DDP.forward()` 會讓 reducer 沒有註冊，反向時該模組的梯度不會 all-reduce，每個 rank 只用自己的 local batch 更新。
查：訓練幾步後比對兩個 rank 上該模組參數的雜湊值，同步正常時必須相同。
正解：呼叫 wrapper 本身，把邏輯移進 `forward()`。

**4.5 LoRA 合併後沒有驗證**
症狀：合併權重之後成功率崩到接近零，但合併過程沒有任何錯誤。
查：合併前後用同一批輸入比對輸出的最大絕對誤差；合併後跑一次小規模 eval 再發布。
正解：把「合併後 eval 分數與合併前差距 < 1%」寫成 CI 斷言。

**4.3 可訓練參數量沒有被記錄**
正解：每個 run 的 log 第一行印 `trainable / total`，這是最便宜的防呆，很多錯都會在這一行露餡。

---

## 5. Seed 與決定性

**5.1 種子沒有蓋到全部來源**
要蓋：`random`、`numpy`、`torch`、`torch.cuda`（all devices）、**dataloader worker（`worker_init_fn` + `generator`）**、**環境（每個 env instance 各自 seed）**、augmentation pipeline、replay buffer 取樣。
症狀：同一個 seed 兩次跑出不同結果，或不同 seed 跑出相同結果（更糟，代表某處 hardcode 了）。

**5.2 DDP 的種子策略**
正解：**model init 用相同 seed**（否則各 rank 起點不同），**data sampling 用不同 seed**（否則各 rank 看到相同資料）。這兩個弄反都會壞。

**5.3 `persistent_workers=True` 的狀態殘留**
症狀：第二個 epoch 之後 augmentation 的隨機性行為改變。
正解：知道它會保留 worker 的 RNG 狀態，決定這是不是你要的。

**5.4 eval 的 seed 綁到訓練步數**
症狀：不同 checkpoint 的 eval 分數不可比，因為它們評的是不同的初始狀態集合。
正解：eval 用固定的 seed 集合（例如 `range(100)`），與訓練步數無關。這是跨 checkpoint 比較的前提。

**5.5 `use_deterministic_algorithms` 的代價**
注意：開了之後某些 kernel 會報錯或大幅變慢，且 `cudnn.benchmark` 必須關。決定要不要開是取捨，但要**明確決定並記錄**，不要有些 run 開有些沒開。

---

## 6. 資料與評估正確性

**6.1 正規化統計洩漏**
症狀：held-out 分數莫名偏高。
查：action / proprioception 的 mean-std 是在哪個 split 上算的。
正解：只用 train split，存成檔案，train 與 eval 讀同一份。

**6.2 held-out 沒有真的 held out**
VLA 特有：同一個物件 mesh、同一個場景、同一個 demonstrator 出現在 train 與 held-out。任務名稱不同不代表分布不同。
查：比對 asset id、scene id、demonstrator id 的交集。
正解：切分要在**產生資料的那一層**做，不是在任務名稱上做。

**6.3 train / eval 的前處理不一致**
查：resize 的 interpolation mode（bilinear vs bicubic）、crop 策略（random vs center）、normalize 的常數、色彩空間（RGB vs BGR）、值域（0-1 vs 0-255）。
正解：前處理寫成單一函式，train 只在它前面加 augmentation，不另外寫一條路徑。

**6.4 action 正規化的反向沒有對齊**
症狀：sim 裡好、實機上動作幅度不對。
查：推論時的反正規化用的是不是同一組統計。
正解：把統計跟 checkpoint 存在一起，不要放在另一個設定檔。

**6.5 padding 的步沒有被 mask 掉**
症狀：短 episode 多的任務表現異常。
查：loss 有沒有乘上 valid mask；分母是不是有效步數而不是總步數。

**6.6 指標的聚合方式**
`mean over episodes` / `mean over steps` / `mean over tasks` 在任務數量不平衡時差很多。
正解：明確寫在 log 裡是哪一種，且跨方法一致。報告時也要寫。

**6.7 成功判準在兩處實作**
症狀：訓練中的 eval 分數與最終 eval 對不起來。
正解：成功判準只實作一次，兩邊 import 同一個函式。

---

**6.8 評估時整個 suite 共用一個 env**
症狀：同一個 checkpoint 重跑兩次分數不同，episode 序號越後面越不穩。
原理：`env.seed()` 只在建立時呼叫一次，RNG 串流跨 episode 前進。`reset()` 從該串流取樣場景擺位並寫進模擬器的 body position，而還原初始狀態的函式往往只還原 `qpos`/`qvel`，不還原幾何。
查：連續兩個 episode 之間 diff 模擬器的 body position，應為零。
正解：每個 episode 內重新 seed，或每個 episode 重建 env。

**6.9 統計計算掃到非數值欄位**
症狀：計算 dataset statistics 時報 `Cast string to float is not supported`，或更糟：某些欄位被算進正規化統計但不該被正規化。
正解：明確列出要計算統計的欄位白名單，不要對整個 sample dict 遞迴。

## 7. RL 特有

**7.1 truncation vs termination**
最貴的一個。時間上限造成的 `truncated` **必須 bootstrap**（`V(s')` 要算進去），真正的 `terminated` **不能 bootstrap**。gym 新 API 把它們分開了，舊 code 常常都當成 `done`。
症狀：長 horizon 任務的 value 被系統性低估，policy 變得短視。
查：計算 target 的那幾行，看 `done` 是從哪裡來的。

**7.2 GAE 在邊界的 next_value**
查：episode 邊界處 `next_value` 是不是被錯誤地設成 0 或用了下一條 trajectory 的值。

**7.3 reward / observation 正規化的統計在 eval 期間被更新**
症狀：eval 分數會隨著你 eval 幾次而改變。
正解：eval 時凍結 running statistics。

**7.4 replay buffer 存的是正規化前還是後**
症狀：正規化統計漂移之後，舊資料的語意就變了。
正解：存原始值，取用時才正規化；或凍結統計。

**7.5 advantage 正規化的範圍**
per-minibatch 正規化會讓有效 LR 隨 batch 組成波動。per-batch 比較穩。要明確選一個並記錄。

**7.6 target network 更新頻率的單位**
是每 N 個 env step 還是每 N 次 gradient update？改了 update-to-data ratio 之後這兩個會脫鉤。

---

## 8. VLA / WAM 特有

**8.1 action chunk 與控制頻率沒對齊**
症狀：實機上動作抖動或延遲一拍。
查：chunk size、執行幾步後重新推論、控制迴圈頻率，三者的關係。最常見的是 off-by-one：預測 `t..t+H` 但從 `t+1` 開始執行。

**8.2 frame stacking 的順序**
症狀：sim 好實機壞，或反過來。
查：訓練時是 `[t-3, t-2, t-1, t]` 還是 `[t, t-1, t-2, t-3]`，推論時是否一致。這個錯不會報錯，模型會學到一個顛倒的世界。

**8.3 語言 token 的 padding 方向**
causal decoder 在推論時必須 **left padding**，訓練時常用 right padding。不一致會讓推論時的位置編碼錯位。
查：`tokenizer.padding_side` 在兩個路徑分別是什麼。

**8.4 world model 的 teacher forcing 與自迴歸落差**
症狀：一步預測很準，rollout 幾步就崩。
查：訓練時 latent 是從 ground-truth observation 編碼來的，推論時是從自己預測的 latent 來的。這是 exposure bias。
正解：訓練時混入 scheduled sampling 或多步 rollout loss，並且**明確記錄訓練用了幾步 rollout**，那是跟推論表現最相關的超參數。

**8.5 rotation 表示與正規化**
四元數輸出沒有正規化，或用了不連續的表示（euler、單位四元數的雙覆蓋）。
正解：用 6D 連續表示；每步都正規化；低精度下正規化誤差會沿著 rollout 累積。

**8.6 action 的物理單位與精度**
症狀：小幅度動作在 fp16 下被量化掉。
正解：action 在進 head 之前正規化到 `[-1, 1]`，不要讓網路直接輸出公尺或弧度。

**8.7 相機內外參與影像幾何**
sim 與實機的 intrinsics、影像解析度、crop、畸變校正是否一致。這是 sim2real gap 裡最容易被歸咎到「domain gap」但其實是 bug 的一類。

**8.8 proprioception 與影像分開正規化**
兩者的尺度差好幾個數量級，共用統計會讓其中一邊消失。

**8.9 推論延遲的量測條件**
症狀：報告 11ms，實機閉環卻只有 15Hz。
查：量的是 batch=1 warm 的中位數，還是含資料搬運、前處理、通訊、安全檢查的端到端？有沒有量 p99？
正解：報端到端與 p99，並註明量測方式。中位數會騙人。

---

## 9. 訓練穩定與監控

**9.1 grad norm 記錄的是 clip 前還是後**
只記 clip 後的話它永遠等於閾值，看不出任何資訊。
正解：兩個都記。clip 前的 spike 是發散的前兆。

**9.2 NaN 沒有 fail fast**
症狀：跑完才發現後半段都是 NaN。
正解：偵測到 non-finite loss 就中止並 dump 該 batch 與 RNG 狀態。

**9.3 LR schedule 的推進單位**
症狀：LR 提早歸零。
查：`scheduler.step()` 在 accumulation 迴圈內還是外；是 per-step 還是 per-epoch scheduler。

**9.4 EMA 權重與評估的一致性**
比較兩個方法時，一個用 EMA 一個沒用，比較就無效。
正解：明確記錄 eval 用的是哪一份權重。

**9.5 資料載入是否餓到 GPU**
查：GPU utilization 的時間軌跡（不是平均值）。平均 85% 可能是「滿載 / 全空」交替。
正解：看 profiler timeline，或量 dataloader 的 wait time。

---

## 10. Checkpoint 與復現

**10.1 checkpoint 沒存完整狀態**
要存：model、optimizer、scheduler、**GradScaler**、RNG states（含 cuda）、global step、以及**完整 config**。
症狀：resume 之後 loss 跳一下然後走不同的軌跡。少存 scaler 是最常見的。

**10.2 eval 用的是 best 還是 last**
兩個都合理，但要一致，而且要寫在報告裡。用 best 時要確認選 best 的那個指標不是你最後要報的那個（否則是在 test set 上選模型）。

**10.5 checkpoint 載入失敗靜默回傳未訓練模型**
症狀：呼叫看起來成功，沒有例外，回傳正常的 policy 物件，唯一線索是一行捲上去的 warning。
為什麼致命：任何「把載入的模型跟自己比」的驗證都會通過，因為兩邊是同一個未訓練模型，數字完美吻合卻毫無意義。
查：載入後斷言 `missing_keys` 與 `unexpected_keys` 皆為空；或比對權重雜湊與 checkpoint 檔。
正解：載入失敗一律 raise。要容忍缺鍵就顯式列出允許缺的鍵名。

**10.3 config hash 與 commit 沒有綁到結果**
正解：每個 eval 輸出的 CSV 第一行寫 commit sha 與 config hash。沒有這個，跨 run 比較都是在賭。

**10.4 「相同設定」其實不同**
正解：提供一個 config diff 工具，比較兩個 run 的實際生效設定（含環境變數、TF32 旗標、PyTorch 版本、GPU 型號），而不是比較設定檔。

---

## 11. 效能陷阱

- 訓練迴圈裡的 `.item()`、`.cpu()`、`print(tensor)` 造成同步阻塞
- `pin_memory=True` 但 `non_blocking=False`，等於沒有效果
- 每步都寫 wandb，log 的開銷吃掉 5–10%
- 變長序列導致記憶體碎片（考慮 bucketing 或 `expandable_segments`）
- activation checkpointing 與 dropout：重算時 RNG 必須對齊，否則前向與重算的 dropout mask 不同，梯度是錯的（PyTorch 的 `checkpoint` 預設有處理，自訂實作常漏）
- 多卡沒走 NVLink 而 fallback 到 PCIe：`nvidia-smi topo -m` 確認

---

## 給 agent 的回報格式

每一項只有三種結果，不准有第四種：

```
[通過]   2.6 clip 在 unscale 之後   train.py:214
[發現]   4.1 凍結的 encoder 沒有 .eval()   model.py:88
         BN running stats 在訓練中仍會更新
[不適用] 7.1 truncation vs termination   此 codebase 不是 RL
```

不確定的一律回報「發現」並附上行號，讓人判斷。**不要因為看起來像對的就標通過** —— 這份清單的價值在於它抓的是「看起來對的錯」。
