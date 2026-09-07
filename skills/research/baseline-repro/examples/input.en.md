# What you hand the skill

> **⚠ Mock.** Kestrel-VLA and TaskSuite-40 do not exist. The shape of the request is real.

Real inputs are this untidy. The skill does not need it tidier — a large part of its
job is turning "we get a worse number" into a list of things that can be checked.

---

> Kestrel-VLA reports **63.2%** average success on TaskSuite-40 (paper Table 3, "ours,
> 7B, fine-tuned"). Their code and weights are both public.
>
> I reimplemented the method in our stack and I'm getting **51.4%**. Same 40 tasks,
> 50 episodes each, 3 seeds. I've been through the training code twice and can't find
> anything wrong. Starting to think their number is optimistic — a couple of people on
> the issue tracker have said the same.
>
> Our stack: internal trainer, our own eval harness (we run every VLA through it so
> the comparisons stay consistent), SimEnv 2.4, our own asset pack.
>
> I have maybe two days on this before I have to move on.
