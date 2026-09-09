# work

Communication and record-keeping. Unlike `research/`, these **follow you to a new job**.

| Skill | What it covers |
|---|---|
| [`grill-deeper`](grill-deeper) | Interrogates your plan, and accumulates an understanding of your work |
| [`codebase-onboarding`](codebase-onboarding) | Maps the data path through a repo you have just met, and verifies the map against a real run |
| [`research-deck`](research-deck) + [`deck-design-system`](deck-design-system) + [`research-figures`](research-figures) | Research decks |
| [`html-design-system`](html-design-system) | The shared tokens, two layout modes, and the primitives every interactive HTML deliverable is built on |

## grill-deeper

Interrogates until every branch of the design tree has been visited, then remembers what the session taught it.

Questions are scheduled on a **frontier**: the ring whose prerequisites are settled, asked one round at a time with a recommended answer attached to each. The mechanism comes from `grilling` in [mattpocock/skills](https://github.com/mattpocock/skills).

What this adds is **memory**, and it meshes with the frontier rather than sitting beside it: **a known fact is a settled node**, so the first round's frontier starts further out. With no store, round one asks how your evaluation works; with one, round one asks whether the perturbation stays at last time's ±3cm. Same round, two levels deeper.

The global layer separately accumulates **the categories of question you go vague on**. After five sessions it knows you get vague every time evaluation protocol comes up, puts that question first in the round, and **gives it no recommended answer** — supplying one is how you skate past it.

Two layers: project facts in `<project>/.grill/` (gitignored), your blind-spot profile in `~/.claude/grill/profile.md`. Blind spots follow the person; project facts do not.

The decision log lives here too: decision, alternative considered, what evidence would reverse it, date. The reversal condition is also how a decision expires — age does not stale one, its condition coming true does.

## codebase-onboarding

Week one on a large repo, the question is not what classes exist — a file tree answers that. It is **what happens to a batch between disk and the loss**. This produces one self-contained interactive HTML map of exactly that, in the same palette as the decks.

What is on it is chosen by where bugs hide: the tensor shape on every edge, whether each module is frozen / LoRA / trained, which file normalisation statistics are read from, and what is on the train path but not the eval path. **The train/eval toggle is the point** — flipping it turns "are the two paths the same" from a code read into a visual diff.

### Click a loss, see what learns from it

The question a data-flow diagram usually cannot answer. Click any loss term and the map fills in every component whose parameters that term updates, marks the nodes gradient merely passes through, puts a red boundary where the autograd graph ends, and fades out everything the term never reaches.

In the openvla example that boundary lands on the collator — which makes it obvious in one glance that the action tokenizer, the Q99 normalisation and the augmentation are all outside the differentiable graph, and no amount of tuning the loss reaches them. It also catches the reverse: openvla's L1 on decoded actions looks like a loss, is plotted next to the loss, and nothing backpropagates through it. Click it and the map says so.

### Read at three scales

A flat sequence of equal-weight cards becomes a hairball the moment a repo has more than one data stream. The map is built in three levels instead: a **group** is a phase (the loader, the encoders, the objective), a **stage** is one step inside it, and a **node** is one operation — placed in its stream's **lane**, which it keeps for the whole map.

That is what keeps the wires readable. A stream owning a column turns most edges into short vertical hops, and full-width bars appear only where streams genuinely merge. Measured on the openvla map, moving from heuristic row ordering to lanes took crossing pairs from 27 to 10 — and to 2 among the edges actually visible on a single path — while median edge length fell from 161px to 32px.

Selecting a node lights what feeds it at full strength and what it feeds at half, because those are different questions: upstream is what you must trust to believe this node, downstream is only a consequence.

It is not a call graph. The [C4 model](https://c4model.com/)'s lowest level, the code level, is the one practitioners skip, because a complete call graph is a hairball nobody reads. So the map is 8–14 nodes, and anything that changes neither shape nor dtype nor semantics gets collapsed.

### Three worked examples

All built by reading the real repositories, and all are the artifact the skill produces, not a mock-up. GitHub shows HTML as source — [`examples/README.md`](codebase-onboarding/examples) has view links and a tour.

| Example | What it shows |
|---|---|
| [`openvla.html`](codebase-onboarding/examples/openvla.html) | [openvla](https://github.com/openvla/openvla) at `c8f03f4`. Actions are language tokens; two vision towers are channel-stacked into one six-channel image; LoRA lands on every linear layer including the towers; and the training script has no eval loop at all, so the toggle compares `finetune.py` against `predict_action` in a different file. |
| [`openpi.html`](codebase-onboarding/examples/openpi.html) | [openpi](https://github.com/Physical-Intelligence/openpi) at `215abfb`. Flow matching in JAX, where t=1 is noise and t is drawn from Beta(1.5, 1); a prefix/suffix attention split assembled from a hand-built list of booleans; and a frozen/trainable split that is also an fp32/bf16 split. |
| [`vitra.html`](codebase-onboarding/examples/vitra.html) | [VITRA](https://github.com/microsoft/VITRA) at `b355172`. A DDPM diffusion policy over a 192-dim two-hand pose — of which 90 channels are dead — conditioned on exactly **one** hidden state gathered out of a 3B PaliGemma. Also the clearest example of why the map is worth drawing: three `if` statements that each read the same config key with a different default. |

Three architecture families, one drawing convention: openvla predicts the action as discrete language tokens, openpi regresses a flow-matching velocity field, VITRA denoises. Between them they carry 38 flagged nodes — each one a specific, cited way that part of the pipeline bites.

### The map is verified, or it says it isn't

A map you cannot verify is a plausible fiction, and you will trust it. So the map is checked against a real forward pass — forward hooks on every module for the model, a batch probe for the dataset transforms hooks cannot see, run once under train and once under eval.

Six pass criteria; the one that repays the exercise is **`training` and `trainable` matching the frozen claim** — `requires_grad=False` set without `.eval()` leaves dropout and BN live in a module you have been calling frozen, and the two calls are in different files, so a code read does not catch it.

A mismatch is a bug in the map, not a reason to weaken the map: fix it and rerun.

Not every framework has hooks. On JAX there are no module objects left after tracing, so "did this module fire" has no equivalent — but `jax.eval_shape` checks every shape with no data, no weights and no accelerator, which is often the only tier available in week one and is a real one. The map records which check ran, not just that one did.

When the code cannot run at all — week one, no data, no cluster — the map still ships, with `verified: false`, a **red banner at the top of the file**, and unconfirmed nodes rendered with a dashed border. It still tells you which seven files matter out of four hundred. Rerunning later flips the banner, which is why the map is a data object rather than hand-written HTML.

## The research-deck trio

Three skills that reference each other and can also be used alone. Use `research-figures` on its own to plot one paper figure; use `deck-design-system` on its own to review an existing deck's appearance.

| Skill | What it covers |
|---|---|
| [`research-deck`](research-deck) | Structure and process: problem → solution → results, and how evidence attaches |
| [`deck-design-system`](deck-design-system) | Palette, type scale, grid, typeface, layout geometry |
| [`research-figures`](research-figures) | Curves with error bands, matrices, ablation deltas, reference lines, conditions footnotes |

### The claim

**The front three pages carry the whole argument; everything after them is evidence.**

1. **Problem** — one big problem, split into 2–4 mid-level problems (Q1…Q4), each with 2–3 measurable technical obstacles
2. **Solution** — the mechanism in a sentence, then one row per Q
3. **Results** — a method-by-metric table that **keeps the cell that is not solved**, plus one key figure

Every page from the fourth on declares `solves=Qn`. Anything attaching to no Q is deleted.

No "here is what I need you to decide" page — that is an internal proposal, not a research deck. No wall of numbers — results go in a table, and showing only wins is promotion.

### Density

One page carries one complete piece of evidence: the figure, the numbers, and the conditions they were measured under. Every figure and table needs a `~ ` conditions footnote and two or three analysis lines; multiple seeds need dispersion drawn; a baseline needs a reference line; a comparison needs a delta; numbers are monospaced.

Where the analysis sits is decided by how much width the figure needs — few horizontal slots put it on the right so the figure keeps its height, many put it underneath so it keeps its width.

### Examples

**[Six sample pages](research-deck/examples/preview)** — the front three plus three evidence pages, rendered from the English example.

`research-deck/examples/` has complete decks in both English and Chinese covering every layout, with the CSVs in `data/`. Starting from an example beats starting from blank.
