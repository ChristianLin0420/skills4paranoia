# Surveying the code

## First, whose code is it

Before anything else, establish authorship, because it changes the meaning of every finding.

| | What a finding means |
|---|---|
| **Official** — an author's account, or linked from the paper or project page | Evidence about the paper. A gap between code and text is a finding about the paper. |
| **Third-party** — anyone else | Evidence about **the reimplementation**. A gap is a finding about the code, and tells you about the paper only where the two agree. |

Record owner, stars, last commit, licence, the commit SHA you read, and the authorship verdict.
Put the verdict in the report header, not in a footnote — a reader who misses it will misattribute
every divergence you list.

**Never merge the two into one narrative.** "RoboTTT gates the TTT output with tanh(α)" and "this
implementation applies the residual twice" are claims about different artefacts. Writing them in one
paragraph makes the second look like a property of the paper.

## Then read all of it

End to end means end to end. A single-file 800-line implementation is two hours. A framework-scale
repo is not, so scope it: the module that implements the paper's mechanism, its call sites, the
training step, and the config that reaches them. State what you did not read.

Take notes as `file:line` as you go, and **verify every citation against the file before shipping**.
Line numbers written from memory or counted off a terminal scroll are wrong at a rate around 1 in 7,
and a wrong line number is worse than none — it costs the reader the trust they extended to the rest.

## Then run it

Reading tells you the shape of the intent. Running tells you what the tensor does. The minimum bar:

1. Import the package and construct the main object.
2. One forward pass on random inputs of the documented shape.
3. **One assertion per mechanism the paper claims**, each printing its measurement.

Write it as `probes.py`, keep it, and ship its output in the report. A measurement in the report that
a reader can re-run is worth more than a paragraph of your confidence.

```python
# the shape of a good probe: state the hypothesis, print the number, name both outcomes
hooked = model(video_hiddens = vh)
plain  = policy(vh.reshape(B * T, N, D)).reshape(B, T)
ratio  = hooked / plain
print(f"hooked/unhooked ratio: {ratio.min():.6f}..{ratio.max():.6f}")
print("expect 1.0 if O = attn + tanh(a)*TTT ; 2.0 if the residual is added twice")
```

Zero the learnable parts you are not testing. A gate set exactly to zero turns a question about
three interacting terms into a question about one, and turns a suggestive number into `2.000000`.

**Probes worth writing for almost any method paper:**

| Claim | Probe |
|---|---|
| An update descends a loss | Measure that loss before and after one update |
| A residual/gate has a stated form | Zero the gate; compare the module's output to its input |
| Gradients are truncated | Give each timestep its own leaf tensor; count how many receive gradient |
| A sampling scheme matches a distribution | Draw 10⁵ and compare the mean to the closed form |
| Only some parameters train | Count `finetune_parameters()` against the total |
| A loss mask does not stop state updates | Run with a mask; check the recurrent step counter still reached T |

If you cannot run it — no wheels for the platform, a dependency on hardware you do not have — say
so plainly in the report and mark every code claim `stated`. Do not let an unrun repo produce
`verified` claims.

## The correspondence table

One row per mechanism the paper describes. This is the centre of the code section.

| Column | Contents |
|---|---|
| Paper | Equation or section number, and the claim in a few words |
| Code | `file:line`, and the identifier |
| Verdict | `match` / `differs` / `absent` / `beyond` |
| Tier | `verified` / `stated` / `inferred` |
| Note | For `differs`: the exact difference, in numbers |

`beyond` is a real and useful verdict: the code implements something the paper explicitly left to
future work. It is not a defect and should not be listed as one.

**Sort by verdict, not by file order.** A reader wants the divergences; the matches are the
reassurance they read afterwards.

## Grading a divergence

Three grades, and the distinction is the whole value of the table:

- **Cosmetic** — absorbed by something learnable, or a difference of convention. A fast-weight loss written as a sum in the paper and a mean in the code differs by a constant factor that a learnable learning rate eats. Say it once; do not inflate it.
- **A choice** — a defensible decision the paper did not make. A forget gate the paper never mentions is a choice; report it, note that its effect is unmeasured here, and do not call it a bug.
- **A defect** — the code does not do what it is trying to do. Requires a runtime measurement, not a reading. This is the only grade that should ever be stated flatly.

**Do not grade a defect from a reading.** The double-residual in the RoboTTT example looks like one
on the page and *is* one at runtime — but the sign convention in the same file looks wrong on the
page and is correct at runtime, because a negated loss and an added gradient compose to a descent
step. Two plausible readings, opposite verdicts; only the probe separates them.

## Reporting upstream

If you find a defect, the useful thing is an issue on the repo with the probe attached. **That is
publishing, and it is the user's call, not yours.** Offer it, hand over the probe, and let them
decide whether and how to file. The same goes for anything you would post about the paper's authors.
