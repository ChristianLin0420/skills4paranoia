# Worked examples

Three maps, each produced by running this skill on a real public repository. They are the artifact the skill emits, not mock-ups.

**GitHub will not render these** — it shows HTML as source. To look at one, either download the file and open it (each is self-contained; no build step, no server, no network beyond a webfont), or open it through a renderer:

| Map | Repo | View |
|---|---|---|
| `openvla.html` | [openvla/openvla](https://github.com/openvla/openvla) @ `c8f03f4` | [open](https://htmlpreview.github.io/?https://github.com/ChristianLin0420/skills4paranoia/blob/main/skills/work/codebase-onboarding/examples/openvla.html) |
| `openpi.html` | [Physical-Intelligence/openpi](https://github.com/Physical-Intelligence/openpi) @ `215abfb` | [open](https://htmlpreview.github.io/?https://github.com/ChristianLin0420/skills4paranoia/blob/main/skills/work/codebase-onboarding/examples/openpi.html) |
| `vitra.html` | [microsoft/VITRA](https://github.com/microsoft/VITRA) @ `b355172` | [open](https://htmlpreview.github.io/?https://github.com/ChristianLin0420/skills4paranoia/blob/main/skills/work/codebase-onboarding/examples/vitra.html) |

## Why these three

They are the same problem solved three different ways, which is the point of reading them side by side.

| | How the action is produced | Conditioning | Loss |
|---|---|---|---|
| **openvla** | Discrete language tokens — 256 bins mapped onto the last 256 vocabulary ids | The action is literally the assistant turn of a prompt | Cross-entropy over action tokens |
| **openpi** | Flow matching — regress a velocity field, integrate at inference | Prefix/suffix split inside one attention stack, two sets of weights | MSE on the velocity |
| **VITRA** | DDPM denoising over a 192-dim two-hand pose | One hidden state, gathered from a single position of a 3B backbone | Masked L2 on ε, split into four components |

## What to try

- **Flip `train` / `eval`.** Every map covers two entry points. openvla's are in different files — `vla-scripts/finetune.py` has no eval loop at all.
- **Click a loss term.** The map fills in which components update from it and greys out everything gradient never reaches. On all three that boundary lands on the collator, which makes it obvious in one glance that the whole data pipeline is outside the differentiable graph.
- **Click `L1 on the decoded actions` in openvla.** It looks like a loss, is plotted next to the loss, and nothing backpropagates through it. The panel says so.
- **Click any node.** Its upstream lights fully and its downstream at half — what feeds a node is what you must trust to believe it; what it feeds is only a consequence.
- **Read the red corners.** 38 nodes across the three maps carry a `watch`: a specific, cited way that part of the pipeline bites.

## What they are not

All three ship `verified: false` with a red banner, because none of them was checked against a forward pass — there was no GPU, no dataset and no framework installed where they were produced.

They were **statically audited**, which is a weaker but real tier: all 137 `file:line` citations were read back against the cloned source, the graph was checked for cycles, dead edges and nodes isolated on a path, and the inferential claims were re-derived in isolation. That pass found 19 wrong line numbers and two modelling errors, all fixed. It confirms nothing about shapes or dtypes. `../reference/verification.md` describes all three tiers.
