# The interview

Propose; do not ask openly. Derive candidate answers from the existing material and let the user reject or correct them — "what do you want to test?" gets a vague answer, "the design doc reads as testing A, but the ablation looks more like B; which is it?" gets a decision.

One group at a time, three to five questions. Every answer goes straight into a field of the document.

## Group 1 — the yes/no question

> Three possible questions come out of the material:
> (a) can a shared world model hold success with half the demonstrations
> (b) is a frozen encoder enough to match full finetuning
> (c) where is the optimal sim-mixing ratio
>
> Which is this round actually answering? Are the other two byproducts, or not tested at all?

Follow up once: **"can this question be answered no?"** Anything that cannot be answered no is not a question, it is a slogan.

## Group 2 — baseline and budget

> What is the control? The repo has `baseline_bc` and `diffusion_policy` configs.
>
> How does each of four dimensions line up — data, compute, parameters, hyperparameter search count? All four rarely can; which one are you letting go, and why?

**A comparison with an unmatched budget means nothing.** If the control ran half the steps, you measured steps, not method. Letting a dimension go is a reasonable trade, but say so.

## Group 3 — what counts as null

The most important group and the most avoided. Press until there is a number.

> - Which is the primary metric? Only one.
> - On your existing runs, what is the standard deviation across seeds at the same setting?
> - How large a difference would count as meaningful?
> - What range means the hypothesis did not hold?

With σ and the target difference, use the table in SKILL.md section 2 to get the seed count. When the answer is unaffordable, say so directly:

> You want to detect 3 points, σ is 4pp, and that needs 20 seeds per arm. Your budget covers 3, which detects nothing under 9 points. Either accept that this run only catches large effects, or narrow the scope and go to 10 seeds. Which?

This exchange is the most valuable part of the interview.

## Group 4 — stopping and decision rules

> - What condition stops the run? Steps, time, or metric convergence?
> - If the primary metric lands in the good band, what happens next?
> - In the null band?
> - In the awkward band between them?

**If all three bands lead to the same next step, the run carries no information.** Say so and let the user decide whether to change the design or not run it.

## Group 5 — the most likely way this is wasted

> What is most likely to waste this run? Three guesses:
> (a) the control's data preprocessing differs from the treatment's
> (b) the held-out split actually leaks
> (c) too few seeds, and the result sits inside the noise
>
> Which is closest? Anything I have not thought of?

Write it down and check against it afterwards. The value of this field is retrospective: if what you worried about happened, deal with it first next round.

## Convergence

All fields have concrete content, and the seed count from group 3 fits the budget. Otherwise keep asking — or conclude that this run should not happen yet, which is also a valid output.

## When to skip

When the user says "this is exploratory, let us just try it", neither comply nor refuse. Ask instead:

> Then shall we set the stopping rule at 20k steps and look once, with training loss rather than success rate as the primary metric?

Turn an exploratory run into an exploratory run **with an endpoint**. Open-ended "let us just try it" is the largest leak in a compute budget.
