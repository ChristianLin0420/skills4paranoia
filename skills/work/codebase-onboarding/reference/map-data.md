# The MAP object

`templates/map.html` reads one object and nothing else. Replace `MAP`, change nothing below it.

Two worked examples are in `examples/` — [openvla](../examples/openvla.html) and [openpi](../examples/openpi.html), both built from real repositories. Starting from one of those beats starting from the template.

```js
const MAP = {
  repo: "openvla @ c8f03f4",             // name @ short commit — the map expires with it
  entry: "vla-scripts/finetune.py (train) · predict_action (eval)",
  framework: "pytorch · bf16 · LoRA r32 · DDP",   // free text, shown in the header
  verified: false,                       // false ⇒ the red banner, see verification.md
  verifiedNote: "Built by reading source at c8f03f4 — no GPU and no data, so no forward pass was run.",
  note: "Optional. Anything the reader needs before believing the picture.",
  terms: ["DINOv2", "SigLIP", "Llama-2 7B"],   // architecture names, bolded and coloured everywhere

  stages: ["SOURCE", "NORMALISE", "TOKENISE", "BATCH", "ENCODE", "SPLICE", "LOSS"],
  lanes:  [{id: "vision", label: "vision"}, {id: "language", label: "language"}],
  groups: [{label: "DATA PIPELINE", note: "runs in the loader", stages: ["SOURCE", "NORMALISE", "TOKENISE", "BATCH"]},
           {label: "MODEL",         note: "",                   stages: ["ENCODE", "SPLICE"]},
           {label: "OBJECTIVE",     note: "",                   stages: ["LOSS"]}],
  nodes: [ ... ],
  edges: [ ... ]
};
```

## Three levels of block

The map is read at three scales, and getting a node onto the right one is most of what makes it legible.

| Level | What it is | How it looks |
|---|---|---|
| **Group** | A phase — the loader, the encoders, the objective | A titled container with a one-line note and a live node count |
| **Stage** | One step within a phase | A labelled row inside the group. **A stage whose label repeats its group's name is drawn without the label** — `BACKBONE` inside a group called `BACKBONE` says the same thing twice, and two nested headings of one name read as two different things |
| **Node** | One operation | A card, in its lane's column |

And a node sits in one of three positions inside its stage:

| Placement | Declare | For |
|---|---|---|
| **Lane** | `lane: "vision"` | Anything belonging to one stream. Keeps the same column all the way down |
| **Span bar** | `span: true` | Only where streams genuinely merge — the collate, the fused backbone. Renders full width, in a heavier style |
| **Free** | neither | A row of peers with no stream meaning, e.g. three loss terms. Centred |

**Reach for `span` sparingly.** It is tempting for anything that operates on the whole batch, but every bar breaks a lane's column and forces the edges around it. A vision-only operation is a `vision` lane node even if it happens to sit alone in its row — that empty language column is what lets the language edge run straight past it.

## Why lanes

The first version placed nodes inside a row by a barycentre heuristic. Columns therefore meant nothing from one row to the next, and an edge from the action stream to the loss could cross the entire graph. Measured on the openvla map: **27 crossing pairs across 34 edges, with the longest single edge longer than the graph was tall.**

Lanes fix it by construction. A stream keeps its column, so most edges become short vertical hops and the only things left to draw are the genuine merges.

| | barycentre rows | lanes and groups |
|---|---|---|
| crossing pairs (all edges) | 27 | 10 |
| crossing pairs (visible on one path) | — | **2** |
| paths running under a card | 3 | **0** |
| labels covered by a card | 4 | **0** |
| median edge length | 161 px | 32 px |

Aim for **one node per lane per stage**. Two nodes in one cell is fine when they are a genuine pair — the two vision towers, a train and an eval variant — and the renderer lays them out as a chain if an edge joins them and side by side if not. Three or more usually means the stage should be split.

## Node

```js
{ id:   "atok",                   // unique, short — also the deep-link anchor (#atok)
  stage: "TOKENISE",              // must appear in stages[]
  kind: "data" | "transform" | "module" | "loss",
  name: "ActionTokenizer",
  meta: "256 bins → last 256 vocab ids",   // the card's second line: what it emits
  file: "prismatic/vla/action_tokenizer.py:38",   // required — no citation, no node
  params: "frozen" | "lora" | "trained" | "quantised",   // modules only
  grad:  "trains" | "flows" | "blocked" | "metric",      // see below
  paths: ["train"],               // from evidence once verified, not from guessing
  conf:  "verified" | "static" | "inferred",
  detail: "One or two sentences: what it does to the tensor.",
  watch:  "Optional. The specific way this node bites. Renders as a red corner on the card and a highlighted block in the panel.",
  notes: ["Short, specific, each citing a line where possible."] }
```

### `conf` — the evidence ladder

| Mark | Means | Renders as |
|---|---|---|
| `verified` | Observed at runtime by a probe | normal border |
| `static` | Read from source, unambiguous — a literal in the file | normal border |
| `inferred` | Your reading of the code; could be wrong | **dashed border** |

Default to `inferred` and earn the others. A map where everything is `verified` because it looked right is the failure this ladder exists to prevent.

### `name` and `meta` — write them for a stranger

These two lines are the whole card, and an abbreviation that is obvious to you after an afternoon in the repo is opaque to the person the map is for. `split 6ch → 2 × 3ch` is a note to self; `split the channel-stacked image` with `(B, 6, 224, 224) → two (B, 3, 224, 224), one per tower` is a map.

`name` is what the step does, in words. `meta` is what comes out of it, with shapes. Neither should need the source file open to decode.

### `terms` — the names worth finding fast

`MAP.terms` is a list of architecture names — `DINOv2`, `PaliGemma`, `LeRobot`. They are bolded and coloured wherever they appear, in cards and panel alike, so the question "where does the vision tower live" is answered by scanning rather than reading.

Keep the list to **proper nouns of models and components**. Adding `LoRA`, `DDP`, `bfloat16` and every other acronym colours half the map, and a highlight that lands everywhere points at nothing.

### `watch` — the field that carries the value

`detail` says what a node does. `watch` says how it bites. It is the difference between a diagram and a map worth keeping, so **write it only when you can name a specific failure**, and name the mechanism rather than the symptom:

> np.digitize returns indices in [1, 256], but 256 bin edges bound only 255 intervals. The file documents the off-by-one at `action_tokenizer.py:53` and works around it on decode by clipping to [0, 254]. Training and inference each do half of this arithmetic, in different files — change `bins` and both must move.

> `train=False` is hardcoded at `pi0.py:114`, and `embed_prefix` is what `compute_loss` calls during training. The image tower therefore never runs in training mode no matter what you pass to `compute_loss`.

Both of these are true, checkable, and change what the reader does next. "Be careful with normalisation" is none of those — delete it.

A node with no trap gets no `watch`. Flagging everything is the same as flagging nothing.

### `grad` — what a loss term actually reaches

Click a `kind: "loss"` node and the map answers *which components learn from this term*. That answer comes from `grad`, and it is **not** the same as walking the data path backwards.

| Value | Means |
|---|---|
| `trains` | Has parameters that this loss updates |
| `flows` | Gradient passes through; nothing of its own is updated |
| `blocked` | The autograd boundary — a dataloader worker, a `detach`, a host round-trip, numpy |
| `metric` | On a loss node: nothing calls `backward` on it |

Defaults if absent: `kind === "data"` is `blocked`, everything else is `flows`. **Set it explicitly on every node anyway** — the interesting cases are exactly the ones the default gets wrong.

The walk stops *at* a `blocked` node and shows it as the boundary. That boundary is the single most useful thing on the map for someone new to the repo: in openvla it lands on `PaddedCollator`, which makes it obvious at a glance that every transform above it — the action tokenizer, the normalisation, the augmentation — is outside the differentiable graph and cannot be tuned by the loss no matter what you do to it.

`metric` is worth hunting for. openvla computes an L1 on decoded actions every step, which looks like a loss, sits next to the loss, and is plotted with the loss — and nothing backpropagates through it. Marking it `metric` makes clicking it say so.

**One honest limit.** `flows` is a claim about the graph, not about what the compiler does. A frozen module with nothing trainable upstream of it is on the gradient path in the diagram sense, but XLA or autograd will prune the backward through it. Where that matters — it is the difference between an activation you must keep and one you need not — say so in `notes` rather than inventing a fifth value.

### `parts` — one module, inputs routed inside it

Some modules are not a single destination. openpi's backbone is one attention stack carrying two disjoint sets of weights: image and language tokens are processed by the PaliGemma parameters, state and action tokens by the action expert's, and the two meet only through attention. Drawn as one undivided card, an edge into it claims nothing more than "this arrives somewhere in here" — and a reader will reasonably conclude the action expert is fed images.

```js
{ id: "llm", span: true, name: "Gemma 2B + 300M action expert",
  parts: [
    {id: "prefix", label: "PaliGemma expert", meta: "image + language tokens",     params: "lora"},
    {id: "suffix", label: "action expert",    meta: "state + noisy action + time", params: "trained"}
  ],
  join: "one attention: every token attends across both halves, but a token only ever touches its own expert's weights" }
```

Edges then name the end they reach:

```js
{from: "siglip", to: "llm", toPort: "prefix",   label: "image tokens"}
{from: "suffix", to: "llm", toPort: "suffix",   label: "(B, 50, w)"}
{from: "llm",    to: "vout", fromPort: "suffix", label: "suffix_out"}
```

**The test: if two inputs reach different parameters, they are different ports.** Anything else and the map is asserting they are interchangeable.

An edge naming a port **terminates on that part**, not on the card's outer edge, and the card's header collapses to one line so the parts sit near the top. That short last run inside the card is deliberate: it is the difference between "arrives at this module" and "arrives *here*". Landing every edge on the outer edge instead leaves the correspondence to be guessed from horizontal position across a card that may be two hundred pixels tall — which is the same failure as having no ports at all.

`join` is what binds the parts, and with exactly two of them it is **drawn between them**, as a linked pair, rather than described underneath. Say what they share — one attention, one router, one normalisation — because that is what a reader cannot see from two boxes standing side by side, and without it they read as two separate models.

Keep it to a few words. It sits in the gap between the parts and a sentence there wraps into a column too narrow to read; the full version belongs in `detail` or `watch`. With three or more parts it falls back to a line underneath, since repeating it in every gap adds nothing.

### Parts or separate nodes?

Both are available and they mean different things.

| | Use |
|---|---|
| **Separate nodes** | The pieces are separately callable modules. openvla's two vision towers each take their own tensor and return their own; nothing binds them but a `torch.cat` afterwards, which is its own node |
| **`parts` on one node** | The pieces cannot be invoked apart — one attention pass, one kernel, one router — and the split is which weights a given input touches |

Getting this wrong in either direction is a real error. Two towers drawn as parts hide a concatenation that has a shape and a dimension argument; two experts drawn as separate nodes invent an interaction point that does not exist and lose the fact that they share attention.

### `kind: "control"` — a mask, not the tensor

```js
{from: "pad", to: "dit", kind: "control", label: "action mask"}
```

Renders dashed. Use it for something that shapes the computation without being the data: a mask, a position index, a router decision, a length. A control input drawn like a data edge overstates it, and the reader starts looking for a tensor that is not there.

### And the converse: do not draw a description as a stage

openpi's `make_attn_mask` was a node on an earlier draft of that map, sitting full width between the token producers and the backbone. It is not a stage — it is assembled from the per-segment `ar_mask` lists as the tokens are built, and describes the sequence rather than transforming it. Drawing it in the path claimed every token flowed through it, and forced four edges out to a gutter to get round it.

If a thing has no tensor passing through it, it is a note or a control edge, not a node.

## Edge

```js
{ from: "atok", to: "prompt", label: "action tokens", paths: ["train"],
  at: "action",            // borrow a lane for a long bar-to-bar carry
  toPort: "suffix",        // land on a named part of the target
  kind: "control" }        // dashed: a mask or an index, not the tensor
```

`at` is optional and only does anything between two span bars. Those have no lane of their own, so the edge would anchor at their centres and detour around whatever is in the middle; `at` lends it a lane to run down instead. Reach for it when a long carry bypasses a whole section — VITRA hands the action targets straight from the collator to the diffusion model without them ever entering the VLM, and saying `at: "action"` turns that from a 2694 px detour into a straight line down an empty column that shows exactly what is being claimed.

`label` is what physically flows — a tensor with a shape, not a description of the step. Omit `paths` when the edge is on both.

**Edges are how the reader traces.** Hovering a node lights everything up- and downstream of it, which is only as good as the edge list: an edge you did not declare is a path the reader will not find.

## Collapse rules

Target **8–16 nodes per path**. The count that matters is per path, not per file, because the toggle means the reader never faces both at once.

**Collapse** when the step changes neither shape, dtype, nor semantics: a residual block inside an encoder, a dropout, a plain `.to(device)`, a `nn.Sequential` of uniform parts.

**Keep** anything with a bug behind it:

- a shape or dtype change — every one
- anything reading from a file (stats, vocab, a checkpoint)
- anything conditional on `training`
- a parameter-state boundary — frozen next to trained
- a fusion point where two paths meet
- the mask, from where it is built to where it is consumed

Collapsing is a claim that nothing interesting happens inside. **Note what you collapsed in the parent's `detail`** so the next reader can disagree with you.

### When a path will not fit

The openvla example runs to 21 nodes on the train path. Nothing was collapsed, because 13 of them carry a `watch` that a collapsed node would hide — the pipeline really is that spiky.

That is allowed, and it is not free. **Say so in `note`**, and point the reader at the path filter, the search box and the diff view instead of letting them read top to bottom. What the guideline actually limits is how much a reader must hold in their head at once; the interaction is what raises that ceiling, so a map over the line without those affordances is just a hairball.

## What the reader gets

Worth knowing while you write, because it changes what is worth annotating:

| | |
|---|---|
| `train` / `eval` / `both` | Filters to one path; off-path nodes stay in place, faded, so the layout does not jump |
| **train ⇄ eval diff** | Lists every node and edge on one path only — computed from `paths`, nothing to maintain |
| Click | **Pins** the node's cone. Everything feeding it lights fully; everything it feeds drops to half; the rest fades out. The distinction matters: upstream is what you have to trust to believe this node, downstream is only a consequence. Hover previews the same thing; the background clears it |
| Click a loss | **Gradient mode**: components that update from it fill accent and read `∂ trains`, pass-through nodes read `∂ through`, the autograd boundary goes red with `∂ stops`, and everything the term never reaches fades out |
| `/` | Filters on name, meta, file, detail and watch |
| Panel | Sectioned rather than run together: DEFINED AT, SIGNAL, WHAT IT DOES, WORTH A SECOND LOOK, NOTES, gradient reach, then upstream and downstream side by side |
| `#node-id` | Deep link — shareable, and it opens with that node selected |
