---
name: codebase-onboarding
description: >-
  Map how data actually moves through an unfamiliar model codebase, and produce an interactive
  HTML flow map that shows tensor shapes on every edge, which modules are frozen or LoRA or
  trained, where normalisation statistics come from, and what differs between the train and eval
  paths. The map is verified against a real forward pass — module hooks and a batch probe — and
  a map that fails verification ships marked NOT VERIFIED rather than silently. Use when
  starting on a new repo, inheriting someone else's training code, or trying to see the data
  path end to end. To understand a METHOD from its paper rather than map a repo you have already
  committed to, use paper-teardown, which hands off to this once you decide to work in the code. Chinese triggers: 幫我看懂這個 codebase / 這份 code 的資料流是什麼 / 畫出模型架構 /
  新專案上手 / train 跟 eval 的前處理一樣嗎.
---

# codebase-onboarding

Produce one artifact: an interactive map of the data path through a model codebase, verified against a real forward pass.

**Language.** Write in whatever language the user writes in. These instructions are English because English is this repo's source language; the map's own labels follow the user.

## What this is for

Week one on a large repo, the question is not "what classes exist" — a file tree answers that. The question is **what happens to a batch between disk and the loss**, and which of the things that happen are load-bearing.

The [C4 model](https://c4model.com/) is worth borrowing one lesson from: its lowest level, the code level, is the one practitioners skip, because a complete call graph is a hairball nobody reads. **So do not draw one.** Draw the data path, at the level where a wrong answer costs you a week — shapes, dtypes, parameter state, and the train/eval delta.

## The honesty rule

A map you cannot verify is a plausible fiction, and you will trust it — that is worse than having no map. So there are two tiers and they look different:

| Tier | When | How it ships |
|---|---|---|
| **Verified** | The forward pass ran and the map matched it | Blue banner naming what was run and when |
| **Not verified** | The code cannot run yet — no data, no cluster, broken deps | **Red banner at the top of the file**, per-node evidence marks |

Never ship a verified banner on a map whose verification failed or was skipped. **A mismatch is a bug in the map**: fix the map, rerun, and only then claim it. If the run cannot happen, say so in the banner and move on — the unverified map still has locating value, as long as it admits what it is.

## Workflow

### 1. Pick one entry point — do not map the repo

Ask which one, or infer it and say which you chose. `train.py` and `serve.py` are different maps, and merging them is how the train/eval delta gets hidden.

### 2. Build the skeleton from source, never from priors

You have seen many VLA and world-model repos. That is the hazard: it is very easy to draw the architecture these repos usually have instead of the one in front of you. Every node needs a `file:line` you actually opened. See `reference/extraction.md`.

### 3. Place every node in a lane

Decide which **stream** each node belongs to — vision, language, state, action — and it keeps that column for the whole map. This is what stops the picture becoming a hairball: a stream that owns a column turns most edges into short vertical hops, and the only things left to draw are the places streams actually merge.

Use a full-width **span bar** only at those merges. Group consecutive stages into phases. Three block sizes, in `reference/map-data.md`.

### 4. Abstract to 8–16 nodes per path

The judgement step, and the only one an LLM is better at than a parser. Collapse anything that does not change the shape, the dtype, or the semantics of the tensor. Keep anything a bug could hide behind.

The count is **per path**, because the toggle means the reader never faces both at once. Going over is allowed when the pipeline is genuinely that spiky — openvla's train path needs 21 — but then say so in `note` and lean on the filter and search rather than pretending the map reads top to bottom. `reference/map-data.md` has the collapse rules.

### 5. Verify — two probes, because one is not enough

Forward hooks only fire on `nn.Module`s, so they cover the model and nothing before it. Dataset transforms are plain functions and need a batch probe instead.

| Probe | Covers | Catches |
|---|---|---|
| Batch probe | source → batch | wrong dtype, unnormalised inputs, a mask that is never built |
| Module hooks | encoders → loss | a module on the map that never fires, a shape you read wrong, `.training` not matching a frozen claim |

Run both under train and under eval. **A node observed on only one path gets `paths:` from evidence, not from guessing.** Harness and pass criteria in `reference/verification.md`.

Not every framework has hooks. On JAX there are no module objects after tracing, so "did this module fire" has no equivalent — but `jax.eval_shape` verifies every shape with no data and no accelerator, which is a real tier and often available in week one when nothing else is. Record **which** check you ran, not just that you ran one.

### 6. Emit

Copy `templates/map.html`, replace the `MAP` object, open it. Nothing below `MAP` needs editing — stage ordering, wire routing and the train/eval diff are all derived from the data.

The reader gets: a train / eval / both filter, hover to light a node's whole up- and downstream cone, click a loss to see what it trains, `/` to search, a **train ⇄ eval diff** that lists everything on one path only, and `#node-id` deep links. Wires are routed around the cards rather than under them, and stages never wrap, so every edge has a visible origin. Two maps built from real repositories are in `examples/`.

## What gets annotated, and why

Every annotation on this map exists because a specific class of bug hides there. This is the same territory `vla-code-review` checks; the map is the visual form of it.

| Annotation | The bug it exposes |
|---|---|
| Tensor shape on every edge | A silent broadcast, a transposed time axis |
| `frozen` / `LoRA` / `trained` per module | `requires_grad=False` set but `.eval()` not — dropout and BN still live |
| Where normalisation stats come from | Stats recomputed over the full set, or a checkpoint denormalised with the wrong file |
| `train only` / `eval only` | Preprocessing divergence — the single most common silent regression |
| Ports on a shared module | Which inputs reach which parameters, when one module holds several — two experts on one attention, a q/kv split, a router |
| `grad` per node | Which components a given loss term actually updates — and where the autograd graph ends |
| Evidence mark per node | Which parts of this map you are entitled to believe |

**The train/eval toggle is the point.** Flipping it turns "are the two paths the same" from a code read into a visual diff.

**Clicking a loss term is the other one.** It fills in every component that updates from that term, marks where gradient stops, and fades everything the term never reaches. Two questions it answers immediately: how far up the pipeline tuning can actually reach, and which of the things plotted next to your loss are metrics that nothing backpropagates through.

## Input and output

**Input**: a repo path and an entry point. Optionally a runnable environment — the map is better with one and still useful without.

**Output**: one self-contained `map.html` (no build step, no server, opens from disk), plus a short written summary of what the map made obvious and what it could not verify.

**Not output**: a review, a refactor plan, or a judgement about the code. Point at what is there. `vla-code-review` is the skill that judges it.

## What this is not

- **Not a call graph.** Complete is the failure mode, not the goal.
- **Not documentation.** It is a working map for one entry point, correct at one commit — put the commit in the header and expect it to expire.
- **Not a substitute for reading the code.** It tells you which files are worth the afternoon.

## Files

- `reference/extraction.md` — building the skeleton without hallucinating it
- `reference/map-data.md` — the `MAP` object, annotation fields, collapse rules
- `reference/verification.md` — the harness, the pass criteria, the two tiers
- `templates/map.html` — the interactive map, deck palette, train/eval toggle
- `examples/README.md` — how to view the three maps, and what to try in them
- `examples/openvla.html` — [openvla](https://github.com/openvla/openvla) at `c8f03f4`: discrete action tokens, fused DINOv2 + SigLIP towers, LoRA on all-linear, and a train path and an inference path that live in different files
- `examples/openpi.html` — [openpi](https://github.com/Physical-Intelligence/openpi) at `215abfb`: flow matching in JAX, a prefix/suffix attention split, and a frozen/trainable boundary that is also a precision boundary
- `examples/vitra.html` — [VITRA](https://github.com/microsoft/VITRA) at `b355172`: a DDPM diffusion policy over a 192-dim two-hand pose, conditioned on exactly one hidden state pulled out of a 3B PaliGemma
