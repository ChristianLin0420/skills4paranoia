# The delta axes

Most of a reproduction gap is not in the model. It is in what "success" was counted as, and in the dozen inference-time constants that never appear in training.

Work down the list. Each row gets `same` / `differs` / `unknown` and a cheapest test. Rows are ordered roughly by how often they turn out to be the answer.

## Measurement — where most of it lives

| Axis | Why it moves the number | Cheapest test |
|---|---|---|
| **Success criterion** | "Object lifted" vs "lifted and held 10 steps" vs "within 5cm of goal" are different benchmarks with one name | Read the criterion function |
| **Episode limit** | A short limit turns slow successes into failures; a long one lets a flailing policy stumble into the goal | Config constant |
| **Timeout vs failure** | Whether a timeout counts in the denominator | Read the aggregation |
| **Number of episodes** | 50 episodes has a ±7pp standard error at p=0.5. Half of a "3-point gap" is noise at that n | Count them |
| **Same episodes?** | Fixed initial states vs freshly sampled ones are different variance regimes, not just different draws | Is the reset seeded |
| **Reset distribution** | Object placement ranges, distractors, lighting. A narrower reset is an easier benchmark | Read the env config |
| **Aggregation** | Mean over tasks, mean over episodes, or task-weighted give different numbers from the same rollouts | Read the reporting code |
| **Seeds, and what is a seed** | Rollouts from one checkpoint are not independent samples — the replication unit is the training seed. See `experiment-prereg` | Count checkpoints, not rollouts |

## Environment

| Axis | Why it moves the number | Cheapest test |
|---|---|---|
| **Simulator version** | Physics changes between releases. Contact and friction solvers are not stable across major versions | `pip freeze`, both sides |
| **Asset version** | Mesh, mass, friction, scale. A benchmark's asset pack gets revised | Asset commit or checksum |
| **Camera** | Pose, FOV, resolution, render backend. A policy trained on one view degrades on another with no error anywhere | Env config; and see the map from `codebase-onboarding` |
| **Control frequency / action repeat** | Doubling the control rate halves the effective horizon of an action chunk | Config constant |
| **Observation space** | Which cameras, which proprio dimensions, in which order | Batch probe: print one observation's keys and shapes |

## Policy and inference

The constants here are the ones that exist **only at inference** and therefore appear nowhere in the training config — which is exactly why they get lost.

| Axis | Why it moves the number | Cheapest test |
|---|---|---|
| **Checkpoint identity** | Released vs final vs best-on-val. And **EMA vs live weights** — where an EMA is kept, it is usually the one that was evaluated | Checkpoint metadata |
| **Sampling constants** | Denoising steps, guidance scale, temperature, samples drawn. openpi defaults to 10 Euler steps and VITRA to 10 DDIM steps with `cfg_scale=5.0`; none of the three appears in training. They change the policy without changing a weight | Read the inference script |
| **Action chunk execution** | Open-loop replay of a chunk vs receding-horizon re-planning every step are different controllers on identical weights | Read the rollout loop |
| **Normalisation statistics** | The single most common silent one. openvla keys its denormalisation by `unnorm_key`, openpi by a flag choosing between mean/std and q01/q99, VITRA by one statistics file per source dataset. The wrong file gives plausible, smoothly wrong actions and raises nothing | Diff the stats file, not the code |
| **Action space convention** | Delta vs absolute, gripper sign, joint order, degrees vs radians | Print one action from each side |
| **Inference precision** | bf16 rollouts diverge from fp32 rollouts over a long horizon even with identical weights | Read the cast |

## Training — only if you retrained

Skip this whole section until the bisection says the gap survives your weights under their harness.

| Axis | Cheapest test |
|---|---|
| Dataset version, split, filtering | Manifest or row count |
| Mixture weights across sources | Config |
| Total gradient steps, batch size × steps | Log |
| Augmentation | Config, and the map |
| What was frozen | Trainable parameter count — and confirm it is the number you chose, not the one a default landed on |

## Reporting

| Axis | Why it moves the number |
|---|---|
| **Best-of-N vs mean** | A maximum over checkpoints or seeds is not an expectation, and beats one by roughly σ·√(2·ln N) |
| **Selected on the test set** | Choosing the checkpoint by the number you then report inflates it, and the amount is not small |
| **Error bars over what** | Over episodes, over seeds, or over both, are three different intervals |

## The ones that are usually not it

Worth saying, because they attract effort out of proportion to how often they are the answer:

- **Optimiser and schedule details.** They move final numbers, but rarely by the size of a reproduction gap, and never as cleanly as a protocol delta.
- **Architecture minutiae.** If the checkpoint loads and the shapes match, the architecture matches.
- **Framework version.** Except where it changes physics or a default; then it belongs under Environment.

Start where the answer usually is: what got counted.
