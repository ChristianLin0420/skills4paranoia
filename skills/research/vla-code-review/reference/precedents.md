# 同型案例

每條檢查對應到真實 repo 裡實際發生過的 bug。用途有兩個：讓報告裡的發現有份量（「這裡可能有問題」和「openvla-oft#160 就是這個」是兩回事），以及讓清單能持續長大。

**看到新案例就往這裡加。** 格式：檢查編號 → repo#issue → 一句話講清楚它怎麼壞的。連結必須是公開 issue，不要放內部連結。

---

## 精度與學習率

**2.1 純低精度訓練沒有 fp32 master weights**
[Physical-Intelligence/openpi#989](https://github.com/Physical-Intelligence/openpi/issues/989) — 同一份資料、同一套評估協定微調 `pi0.5_base`，JAX 版 82.6、PyTorch 版 71.9。README 自承 JAX 走混合精度而 PyTorch 只支援全 bf16 或全 fp32，且全 bf16 的 loss 會偏高。

**9.1 缺梯度裁剪**
[openvla/openvla#333](https://github.com/openvla/openvla/issues/333) — LoRA 微調 LIBERO-Spatial，第 6000 步 loss 由 2.2 跳到 5.2，action accuracy 崩到接近零且再也沒回來，最終成功率 0/50。回報者指向 `finetune.py` 缺少 `clip_grad_norm_`。

## 硬體與 kernel

**1.4 SDPA 靜默 fallback**
[openvla/openvla#333](https://github.com/openvla/openvla/issues/333) — 同一篇還帶出另一件事：**作者自己的 checkpoint** 在 ARM64 GH200 上只跑出 74%，論文報 84.7%。差別是 flash-attn 的預編譯 wheel 只有 x86 版，容器裡沒裝成功。十個百分點純粹來自 attention backend 換掉，沒有任何錯誤訊息。

**1.1 精度與 compute capability**
[unslothai/unsloth#4082](https://github.com/unslothai/unsloth/issues/4082) — V100（SM70）無法對 bf16 模型做全參數微調。跨機器搬 config 時最容易踩到。

## 分散式與參數

**4.4 DDP 被 `.module` 繞過**
[moojink/openvla-oft#160](https://github.com/moojink/openvla-oft/issues/160) — action head 被 DDP 包起來，但 `finetune.py` 呼叫 `action_head.module.predict_action(...)`。繞過 `DDP.forward()` 使 reducer 未註冊，action head 的梯度不會 all-reduce，每個 rank 只用自己的 local batch 更新自己的頭。

**4.5 LoRA 合併後崩潰**
[moojink/openvla-oft#151](https://github.com/moojink/openvla-oft/issues/151) — 直接用官方 checkpoint 有 93.2%，用 repo 自帶的 `merge_lora_weights_and_save.py` 重新合併之後，成功率掉到零。

## 評估正確性

**6.8 評估時 env 跨 episode 重用**
[openvla/openvla#342](https://github.com/openvla/openvla/issues/342) — `run_libero_eval.py` 每個 task 只建一個 env，`env.seed()` 只叫一次。`env.reset()` 從已前進的 RNG 串流取樣家具擺位並寫進 `sim.model.body_pos`，但 `set_init_state()` 只還原 `qpos`/`qvel`。`libero_10` task 2 的爐台在 episode 之間位移 3.0mm。在 episode 迴圈內補一次 `env.seed(cfg.seed)` 就完全消除。

**6.7 成功判準過寬（假陽性）**
[simpler-env/SimplerEnv#129](https://github.com/simpler-env/SimplerEnv/issues/129) — WidowX 任務在物體只是靠近目標、機器人還沒鬆手、甚至物體即將掉落時就判定成功。
[Lifelong-Robot-Learning/LIBERO#149](https://github.com/Lifelong-Robot-Learning/LIBERO/issues/149) — LIBERO-10 Task 6 在布丁接觸桌面之前就可以判成功。

**6.7 成功判準過嚴（假陰性）**
[Lifelong-Robot-Learning/LIBERO#145](https://github.com/Lifelong-Robot-Learning/LIBERO/issues/145) — `SiteObject.in_box()` 沒有考慮 site 的旋轉。容器在 rollout 中被轉動時，中心明明在區域內的物體會被判定在外。

**6.3 前處理與 checkpoint 內嵌設定矛盾**
[huggingface/lerobot#4548](https://github.com/huggingface/lerobot/issues/4548) — 文件裡的 `rename_map` 與 checkpoint 內嵌的 preprocessor 不一致，加上評估指令本身就落在分布外，導致模型被系統性低估。

**6.9 統計計算掃到非數值欄位**
[octo-models/octo#163](https://github.com/octo-models/octo/issues/163) — 自訂 RLDS dataset 含 `language_instruction` 字串欄位，計算 dataset statistics 時整個掛掉（`Cast string to float is not supported`）。

**6.1 正規化統計與 checkpoint 沒有綁定**
[moojink/openvla-oft#156](https://github.com/moojink/openvla-oft/issues/156) — 詢問 unnorm stats 與微調 checkpoint 的耦合關係。
[Physical-Intelligence/openpi#1025](https://github.com/Physical-Intelligence/openpi/issues/1025) — 社群直接要求加一份「唯讀的正規化相容性報告」，可見這是反覆踩的坑。

## 復現與載入

**10.5 載入失敗靜默回傳未訓練模型**
[huggingface/lerobot#4577](https://github.com/huggingface/lerobot/issues/4577) — `PI0Policy.from_pretrained` 在無法套用 checkpoint 時印個 warning 然後照樣回傳模型，`strict=True` 也擋不住。回報者當時在驗證匯出模型與原模型是否一致，兩邊都是同一個未訓練模型，數字完美吻合，一整批量測在他發現前就已作廢。

**10.3 分數無法復現**
[NVlabs/vla0#29](https://github.com/NVlabs/vla0/issues/29) — 論文報 LIBERO 94.7，重現得到約 92.5；作者重新訓練與評估後得到 92.2。
[moojink/openvla-oft#150](https://github.com/moojink/openvla-oft/issues/150) — LIBERO-Spatial 成功率低於論文值。

**資料本身的品質**
[Lifelong-Robot-Learning/LIBERO#148](https://github.com/Lifelong-Robot-Learning/LIBERO/issues/148) — LeRobot 格式的資料品質稽核：920 可讀 / 773 缺失（loader bug），另有 action 與 tracking 異常尚未解決。所有基於這份資料的結論都受影響。

## 泛化是不是記憶

**LIBERO-PRO** — 在 LIBERO 上拿到 90%+ 的模型，只要在同一個模擬器內做擾動（物體擺位、改寫指令、初始狀態、環境），成功率會崩到接近零。研究者把它歸因為對動作序列與版面的死記。

這條沒有對應到單一檢查項，但它決定了你怎麼讀 held-out 分數：**如果你的 held-out 只換任務名稱沒換分布，那個數字量的是記憶不是泛化**（見 `checklist.md` 6.2）。

---

## 怎麼用在報告裡

每條發現底部加一行「同型案例」，連到這裡對應的 issue。沒有對應案例的發現就不加 —— 不要為了看起來有根據而硬掛不相關的連結。

新案例的收錄標準：**公開、可驗證、而且是靜默失敗**。單純的安裝錯誤、版本衝突、CUDA OOM 不收，那些會自己報錯，不需要 review 來抓。
