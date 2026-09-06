# The evaluation protocol

Leave these four unfixed and your numbers cannot be compared with anyone's, including your own three months from now. Each one has a real reproduction failure behind it; see `vla-code-review/reference/precedents.md`.

## 1. Which layer held-out is cut at

Four different levels, weakest to strongest:

| Level | Meaning | What it measures |
|---|---|---|
| Task name | Reword the instruction | Almost nothing |
| Object instance | Same category, different item (a different mug) | Within-category generalisation |
| Scene | Different layout, lighting, background | Visual generalisation |
| Demonstrator | Data collected by a different person | Generalisation over operating style |

**State which level in the report.** Change only the task name and the number measures memorisation, not generalisation — LIBERO-PRO found that models scoring 90%+ on LIBERO collapse toward zero under in-simulator perturbation of object placement or paraphrased instructions.

Cut the split **at the layer that generates the data**, not on task names. Then verify: the intersection of asset ids, scene ids and demonstrator ids should be empty.

## 2. The full success criterion

A complete criterion needs at least four things:

1. **The geometric condition** — object centre inside the target region, or contact? How is the region defined?
2. **Hold duration** — how many consecutive frames must satisfy it? Without this the criterion fires while the object is still falling.
3. **End state** — has the gripper released? Has the arm withdrawn?
4. **Rotation invariance** — does the test still hold when the container is rotated?

Missing the first two **over-reports** (SimplerEnv#129: success while the object is merely near the target and the robot has not released; LIBERO#149: success before the object touches the table). Missing the fourth **under-reports** (LIBERO#145: `in_box` ignores site orientation, so an object whose centre is inside a rotated container reads as outside).

**Implement the criterion once.** Training-time eval and final eval must import the same function, or the two sets of numbers will not agree.

When you change the criterion, re-run an old checkpoint and see how far the score moves. If it moves a lot, every past number needs reinterpreting.

## 3. The eval seed protocol

Three rules:

- **A fixed set**, e.g. `range(100)`, written into the config.
- **Independent of training step** — otherwise different checkpoints are evaluated on different initial states and the comparison is fake.
- **Reseed every episode**, not once per task.

The third is the one that gets missed. OpenVLA#342: `run_libero_eval.py` builds one env per task and seeds once, so the RNG stream advances across episodes; `reset()` samples fixture placement from it into the simulator geometry while `set_init_state()` restores only `qpos`/`qvel`. The stove moved 3.0mm between episodes. Reseeding inside the episode loop removed the effect entirely.

## 4. Perturbation testing

Without it you do not know whether 90% is capability or rote learning.

Four kinds at minimum, each reported separately:

- **Object placement** — randomise the starting position within a reasonable range
- **Instruction rewording** — synonyms, different phrasings
- **Initial state** — the arm's starting pose
- **Visual** — lighting, materials, background

**The perturbed success rate is the number you should be leading with**; the unperturbed one is an upper bound. Report both — the gap is itself informative, and a large gap means the model memorised the layout.

## 5. What this looks like in the document

```
Evaluation protocol
  Held-out level     object instance + scene (asset and scene ids disjoint, verified)
  Success criterion  object centre in target box, 10 consecutive frames, gripper released,
                     rotation-invariant. Implemented in envs/criteria.py:success(),
                     shared by training-time and final eval
  Eval seeds         range(100), fixed, independent of training step, reseeded each episode
  Rollouts           100 per task × 12 tasks × 3 seeds
  Perturbation       placement ±3cm, 3 instruction rewrites, 3 initial poses, 2 lightings
  Headline number    mean success under perturbation; unperturbed reported as an upper bound
```

This block goes straight into the deck's setup page in `research-deck`.
