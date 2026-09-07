> ## ⚠ MOCK EXAMPLE
> **Kestrel-VLA, TaskSuite-40 and every number below are invented.** There is no such
> baseline and no such benchmark. What is real is the shape of the failure: the axes,
> the bisection, and the two conventions that turn out to account for the gap. Do not
> cite anything here.

# Reproduction — Kestrel-VLA vs our reimplementation

**Verdict.** We are measuring something else. Two conventions in **our own** eval harness
account for the gap; the method reproduces.
63.2% reported · 51.4% measured · 11.8pp gap · 10.5pp recovered by changing two constants

**Scope.** Testing one claim: Table 3, "ours, 7B, fine-tuned", 63.2% mean success on
TaskSuite-40. Not testing their training recipe, their data, or any other row of that table.

---

## What accounts for the gap

Two ordinary conventions compounding. Neither is a mistake, and neither is dramatic —
which is the usual shape, and the reason "their number is optimistic" was the wrong
first hypothesis.

| Factor | Theirs | Ours | Cost to close | Recovered |
|---|---|---|---|---|
| Episode limit | 400 steps | 300 steps | one constant | 4.8pp |
| Chunk execution | re-plan each step | replay all 8 open-loop | one loop | 5.7pp |
| | | | | **10.5pp of 10.9** |

**Episode limit.** Our harness caps every policy at 300 steps so cross-model comparisons
stay consistent. Any success slower than 300 steps is silently reclassified as a failure,
and Kestrel's policy is slower than our own baselines, so the cap costs it more than it
costs us.

**Chunk execution.** They predict 8 actions and re-plan after executing one; we execute
all 8 before predicting again. Identical weights, different controller — open-loop replay
cannot recover a grasp that slips at step 2. **This one has no trace in any config.** It
lives in the shape of the rollout loop, where a config diff would never have found it.

## Bisection

| Cell | Weights | Harness | Number | Reading |
|---|---|---|---|---|
| ① | theirs | theirs | **62.8%** | Environment sound; everything below is interpretable |
| ② | theirs | yours | **51.9%** | **Gap is in our evaluator** — same policy, 10.9pp lost |
| ③ | yours | theirs | 62.1% | Our training is fine, within noise of ① |
| ④ | yours | yours | 51.4% | ② and ③ account for ④; nothing interacting |

Two hours of compute, against two days budgeted. It closed the question before any of it
was spent: the model was never the problem, and the training code already read twice did
not need a third pass. Training rows were therefore never opened.

## Ledger

20 rows, 19 closed, all 19 without compute. Only the rows below are worth reading.

| Axis | Theirs | Ours | State | Explains gap | Cheapest test |
|---|---|---|---|---|---|
| Episode limit | 400 steps | 300 steps | `differs` | **yes** | config constant · free |
| Chunk execution | re-plan each step | 8 open-loop | `differs` | **yes** | read the rollout loop · free |
| Asset pack | their v3 | ours | `unknown` | possibly | checksum · 20 min |

<details><summary>17 rows checked and identical</summary>

Success criterion (in-region ≥10 steps) · timeout counted as failure · 50 episodes per
task · seeded fixed initial states · reset ±8cm with no distractors · mean over tasks ·
3 training seeds · SimEnv 2.4 · camera 224² fixed pose · 5 Hz control · 1 camera and 7
proprio dims · released final checkpoint · no EMA kept · greedy decoding, 7 tokens ·
`unnorm_key=tasksuite` · delta EE with gripper +1 open · bf16 inference.

</details>

## Closing them

| | |
|---|---|
| cell ② baseline | 51.9% |
| + episode limit 300 → 400 | 56.7% |
| + receding horizon | **62.4%** |

62.4% against their 63.2%, with ① at 62.8%. The residual 0.8pp is inside the spread of
three seeds and does not need explaining.

## What was easy · what was difficult

**Easy** — weights and code both released, so cell ① could be run at all. Their eval
entry point takes a checkpoint path and nothing else. `pip freeze` matched on the first try.

**Difficult** — the two axes that mattered are both **absences**: an episode limit the
paper does not state, and an execution mode that appears in neither paper nor config. Both
were found by reading their rollout loop against ours, which is not a diff any tool
produces. Budget half a day for that read on the next one.

## Where this bites beyond the one number

Both conventions are **house rules in our harness, not mistakes** — and they apply to every
model that harness has ever run. Every internal cross-model comparison we have published
carries the same 300-step cap and the same open-loop execution, and both penalise slower
policies uniformly. Defensible as a house rule; indefensible as an unstated one.

We found this because one comparison happened to be against a public number with public
weights. Nothing would have surfaced it otherwise.

## Action items

| # | Action | Owner | By |
|---|---|---|---|
| 1 | Emit episode limit and execution mode in the harness's result metadata, so a number cannot travel without them | eval owner | next harness release |
| 2 | Re-check past comparisons where the losing policy was the slower one | me | end of month |
| 3 | Close the asset-pack row, or record that it stays open | me | with (2) |

## Still unknown

**Asset pack version.** Not closed. At the precision three seeds give it cannot account
for the residual 0.8pp, so it stays `unknown` rather than being written `same`.

---

The issue-tracker reports of a low number are consistent with this and do **not**
corroborate the paper being optimistic — the same house rules are common. Nothing here
supports writing that Kestrel-VLA does not reproduce; the draft sentence saying so was cut.
