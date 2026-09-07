# 交給 skill 的東西

> **⚠ 虛構。** Kestrel-VLA 跟 TaskSuite-40 不存在。真實的是這個請求的形狀。

真實的輸入就是這麼亂。Skill 不需要你先整理好——它的工作有一大半，就是把「我們的數字比較差」
變成一份可以逐條查證的清單。

---

> Kestrel-VLA 論文 Table 3 報 TaskSuite-40 平均成功率 **63.2%**（"ours, 7B, fine-tuned"），
> code 跟 weights 都公開。
>
> 我在我們的 stack 上重實作，跑出來 **51.4%**。一樣 40 個 task、每個 50 個 episode、3 個 seed。
> 訓練的 code 我來回看了兩遍，找不到哪裡有問題。**開始覺得他們的數字是灌水的**——
> issue tracker 上也有一兩個人講一樣的話。
>
> 我們的 stack：自家 trainer、自家 eval harness（所有 VLA 都走同一套，這樣比較才一致）、
> SimEnv 2.4、自家的 asset pack。
>
> 我大概只有兩天可以查這個，之後就得往下走了。
