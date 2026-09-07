# Reproduction ledger — Kestrel-VLA (paper Table 3) vs our reimplementation

> Illustrative. The numbers are made up; the protocol mechanics are the ones that
> actually bite, and the file references follow the shapes in the three repositories
> mapped by `codebase-onboarding`.

**Their number**: 63.2% avg success, TaskSuite-40, paper Table 3 ("ours, 7B, fine-tuned")
**Our number**: 51.4%, 40 tasks × 50 episodes × 3 seeds
**Gap**: 11.8pp

**Before starting.** Three claims, and the opening one is not the one in the request:
their number being optimistic is the *rare* case, and nothing below has been checked
yet. Until the ledger says otherwise this is "we are measuring something else".

## Bisection

| Cell | Weights | Harness | Number | Reading |
|---|---|---|---|---|
| ① | theirs | theirs | **62.8%** | Environment and machine are sound. Everything below is interpretable |
| ② | theirs | yours | **51.9%** | **The gap is in our evaluator.** Same policy, 10.9pp lost |
| ③ | yours | theirs | **62.1%** | Our training is fine — within noise of ① |
| ④ | yours | yours | 51.4% | ② and ③ account for ④; nothing is interacting |

Two hours of compute. It closed the question the two days were budgeted for: **the
model was never the problem**, and the training code that had been read twice did not
need reading a third time.

Everything below is therefore a measurement axis. Training rows are not opened.

## Ledger

`same` = checked and identical · `differs` = checked and different · `unknown` = not determined

| Axis | Theirs | Ours | State | Could explain | Cheapest test |
|---|---|---|---|---|---|
| **Episode limit** | 400 steps | 300 steps | `differs` | **Yes** — truncates slow successes | Config constant · free |
| **Chunk execution** | re-plan every step | replay all 8 open-loop | `differs` | **Yes** — an 8-step open loop cannot correct | Read the rollout loop · free |
| Success criterion | in-region ≥10 steps | in-region ≥10 steps | `same` | — | Criterion fn · free |
| Timeout counted as | failure | failure | `same` | — | Aggregation · free |
| Episodes per task | 50 | 50 | `same` | — | free |
| Same initial states | seeded, fixed | seeded, fixed | `same` | — | free |
| Reset distribution | ±8cm, 0 distractors | ±8cm, 0 distractors | `same` | — | Env config · free |
| Aggregation | mean over tasks | mean over tasks | `same` | — | free |
| Seeds | 3 training seeds | 3 training seeds | `same` | — | free |
| Simulator | SimEnv 2.4 | SimEnv 2.4 | `same` | — | `pip freeze` · free |
| Assets | their pack v3 | our pack | `unknown` | Possibly | Checksum · 20 min |
| Camera | 224², fixed pose | 224², fixed pose | `same` | — | free |
| Control frequency | 5 Hz | 5 Hz | `same` | — | free |
| Observation space | 1 cam + 7 proprio | 1 cam + 7 proprio | `same` | — | Batch probe · free |
| Checkpoint identity | released final | released final | `same` | — | Hash · free |
| EMA or live | no EMA kept | n/a | `same` | — | free |
| Sampling constants | greedy, 7 tokens | greedy, 7 tokens | `same` | — | Inference script · free |
| Normalisation stats | `unnorm_key=tasksuite` | same key | `same` | — | Diff the stats file · free |
| Action space | delta EE, gripper +1 open | same | `same` | — | Print one action · free |
| Inference precision | bf16 | bf16 | `same` | — | free |

Nineteen of twenty rows closed without a GPU. Both rows that could explain the gap were
constants someone could have read on day one.

### The two that differ

**Episode limit, 400 vs 300.** Our harness caps every policy at 300 steps so runs stay
comparable across models — a reasonable house rule that silently reclassifies any
success slower than 300 steps as a failure. Kestrel's policy is slower than our own
baselines, so the cap costs it more.

**Chunk execution.** They predict 8 actions and re-plan after executing one. We execute
all 8 before predicting again. Identical weights, different controller: open-loop replay
cannot correct for a grasp that slips at step 2. This is the axis with no trace in any
config — it lives in the shape of the rollout loop, and diffing configs would never
have surfaced it.

## Closing them

| Change | Number |
|---|---|
| baseline (cell ②) | 51.9% |
| + episode limit 300 → 400 | 56.7% |
| + receding horizon | **62.4%** |

62.4% against their 63.2%, with ① at 62.8%. The residual 0.8pp sits inside the spread
of three seeds and does not need explaining.

## Verdict

- [x] **We are measuring something else.** Episode limit and chunk execution differ and
      close 10.5 of the 10.9pp that cell ② localised to our harness. This is not a
      disagreement about the method.
- [ ] Accounted for by a single axis
- [ ] Their setup has an advantage
- [ ] Real disagreement
- [ ] Cannot be attributed

## Still unknown

- **Asset pack version.** Not closed. It cannot account for the remaining 0.8pp at the
  precision three seeds give, so it stays open rather than being called `same`.

## What this changes beyond the one number

Both differing axes are **house rules in our harness, not mistakes** — and they apply to
every model we have ever run through it. Every cross-model comparison we have published
internally carries the same 300-step cap and the same open-loop execution, which
penalises slower policies uniformly. That is defensible as a house rule and indefensible
as an unstated one.

Two follow-ups, neither of which was the question asked:

1. Put the episode limit and the execution mode in the harness's reported metadata, so a
   number cannot travel without them.
2. Re-check any past comparison where the losing policy was the slower one.

The issue-tracker reports of a low number are consistent with this and do not corroborate
the paper being optimistic — the same house rules are common. Nothing here supports
writing that Kestrel-VLA does not reproduce, and the draft sentence saying so was cut.
