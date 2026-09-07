# The bisection

Two artifacts, two harnesses, four cells. Run them in this order and each one rules out a half of what is left.

```
                 their eval harness        your eval harness
their weights    ①  environment            ②  your evaluator
your weights     ③  your trainer           ④  the gap you started with
```

## ① their weights, their harness

**Run this first.** It feels like it proves nothing — you are just re-running someone else's code — and it is the only cell that establishes whether anything downstream is interpretable.

| Result | Means |
|---|---|
| Matches their number | Your machine and environment are sound. Everything below is now meaningful |
| Misses | The gap is in the environment or the machine, and no amount of work on your model will close it |

A miss here is good news, not bad: you have localised the problem to a layer that is entirely configuration, before spending a GPU-week on the model.

## ② their weights, your harness

Same policy, different measurement. Any delta is **your evaluator**, and it is a delta you introduced.

This is the cell that catches a success criterion you rewrote, an episode limit you changed, a reset distribution you widened, a chunk you execute open-loop where they re-plan.

## ③ your weights, their harness

Same measurement, different policy. Any delta is **your training** — or a checkpoint difference, which is worth eliminating before blaming the trainer.

Reach this cell and `vla-code-review` is the next tool: the failures that never raise and only make numbers worse.

## ④ your weights, your harness

Where you started. Its value is only as the sum: ② and ③ should roughly account for ④. **When they do not, something is interacting**, and that is worth knowing before you fix either one.

## When their code is not released

The table collapses to ④, every axis opens as `unknown`, and no cell can be run.

You can still do useful work — reconstruct their protocol from the paper into `experiment-prereg`'s fields, and every field the paper does not determine is an `unknown` row. But the strongest verdict available is **cannot be attributed**. Reporting your number with your protocol attached is honest and useful; reporting it as a failure to reproduce is neither.

## When their weights are not released but their code is

Run ③ only. It confounds your training with the checkpoint, so treat any gap as jointly attributed until you can separate them — usually by training their own recipe from scratch, which is expensive and worth pricing before starting.
