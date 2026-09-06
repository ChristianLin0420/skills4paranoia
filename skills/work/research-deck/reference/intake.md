# Phase 0: inventory and clarification

The input is a folder that may hold `figures/`, run logs, experiment and model design notes, meeting notes. The output is a deck plan both sides agree on.

**Do not start writing before finishing this phase.** The material will not tell you what matters — that lives in the user's head, and only questions get it out.

## 0.1 Inventory first, ask nothing

Scan the whole folder and build a list. Read every `.md` in full; sample logs for their columns and scale rather than reading them in; note figure filenames and dimensions without guessing at content.

Then lay out what you found:

```
Figures (7)
  figures/scaling.png            1600×1000
  figures/ablation_ctx.png       1600×1000
  figures/arch_v2.png            2400×1200
  figures/rollout_*.png          5-frame sequence
Documents (3)
  exp_design.md                  three ablations: context length, data mixing, frozen encoder
  model_design.md                three-stage architecture, frozen encoder + shared world model
  meeting_0903.md                meeting notes; long-horizon performance was challenged
Records
  runs/2026-09/*/eval.jsonl      14 runs, columns task / seed / success / steps
```

**Ask nothing during inventory.** Let the user see what you found first, so their answers have something to stand on — and so they notice what you failed to read.

## 0.2 Interview rules

- **Propose; do not ask openly.** "What do you want to say?" gets a vague answer. "`exp_design.md` reads as solving A, but the ablations look more like B — which is this deck about?" gets a decision. Derive candidates from the material every time and let the user reject or correct them.
- **One group at a time**, three to five questions. Not ten at once, and not one at a time either.
- **Do not ask what the material already answers.** It signals you did not read.
- **Land every answer in a slot immediately**; do not collect loose information and assemble at the end.
- **"They are all important" is not an answer.** Force a ranking: "if you could keep only three figures, which three?"
- **When the user says "you decide", propose something specific** for them to accept or reject rather than actually deciding.

## 0.3 Five groups

### Group 1 — the big problem and its decomposition

Derive two or three candidate framings from the material and ask the user to pick or rewrite. Then propose your Q decomposition and ask which are real and which are noise.

> Three framings come out of the material:
> (a) sample efficiency — data cost is the core, and every ablation compares demos to target
> (b) generalisation — held-out performance carries the most weight, the matrix dominates
> (c) deployability — but there is only one latency measurement; the thinnest evidence
>
> Which is this deck actually about? Are the other two sub-problems, or not mentioned at all?

### Group 2 — a verdict on every figure

**The most important group.** Every figure has one of three fates, and each one needs a clear answer. Leave nothing undecided.

| Fate | When | Result |
|---|---|---|
| **Redraw** | The underlying data exists (CSV, jsonl, log) | Redrawn to the theme, uniform throughout |
| **Place the original** | Cannot be reproduced: architecture, pipeline, rollout frames, on-robot capture, external | Placed as-is, style differs from other pages |
| **Drop** | Hangs off no Q | Not in the deck |

The test: **redraw if the underlying data exists, place if it does not.** That way everything that can be unified is, and everything that cannot be is still there. Statistical figures — curves, bars, matrices, ablations — can almost always be redrawn if the CSV or log can be found.

Go figure by figure, asking both "which Q" and "redraw or place":

> - `scaling.png` — supports Q1? There is a matching eval.jsonl under `runs/2026-09/`, so I can redraw it to the theme, or do you want the original?
> - `ablation_ctx.png` — which Q? Do the raw numbers exist? If so I would redraw it as an ablation table, which adds a Δ column.
> - `arch_v2.png` — an architecture figure with no underlying data, so I place it. Solution page or evidence page?
> - `rollout_*.png`, five frames — cannot be reproduced. Filmstrip with all five, or pick three?

Follow up on each with two questions:

**"If this were deleted, which conclusion would stop standing?"** Cannot answer, so delete it. A researcher's default is to include everything; this question exists to fight that default.

**"What do you want the reader to see here?"** The answer becomes that page's two or three analysis lines. You can see the curve splits at 50k; you cannot see what it means for their research. Skip this and every figure page ends up with a figure and no reading. When the answer is vague, press for specifics: which point, which interval, compared against which line.

When something is obviously a statistical figure but the numbers cannot be found, raise it:

> `loss_curve.png` looks like a training curve, but I cannot find matching numbers in the folder. Does the original log still exist? If it does I will redraw it and the styling will match the rest; if not I will place it, and that page's type and colour will differ from its neighbours.

A placed original will not match its neighbours. That is unavoidable — do not crop or filter it to hide the difference, that only makes it worse. Redraw everything that can be redrawn, place what is irreplaceable, and keep the title and footnote format consistent so the framework's uniformity carries the style's inconsistency.

### Group 3 — results and what is unsolved

> - Which metric did you not actually solve this round? The results table must keep that cell.
> - Is there a number you do not fully believe yourself? (too few seeds, too small an eval set, run once)
> - Is any result a coincidence you have not ruled out?

"What is still unsolved" is the most valuable question in the interview and the one users most avoid. Press until the answer is concrete. Showing only the wins turns the deck into marketing.

### Group 4 — audience

> - Who reads this? What do they already know?
> - What are they most likely to challenge?
> - Is there a conclusion they heard last time that does not need repeating?

Cut what they already know; pre-place evidence for what they will challenge. If the folder has meeting notes, answer this group from them rather than asking again.

### Group 5 — backfilling gaps

Once you have laid it out mentally, check back:

> Q3 has one supporting figure and it came out of a log. Do you have other evidence? If not, should Q3 drop to a sub-problem under Q2?

Better to remove a Q than to keep one with no evidence.

## 0.4 Convergence

Do not start writing until all of this is settled:

1. The big problem, one sentence, confirmed by the user
2. Two to four Qs, each with two or three measurable sub-problems
3. **Every figure has a verdict** — redraw, place, or drop
4. **Every surviving figure has been asked "what should the reader see"** — that is its page's analysis
5. The results table columns are fixed, and include at least one unsolved metric
6. Who the audience is and what they already know

Keep asking until you get there. Do not fill gaps by guessing — a wrong guess costs a full re-layout, because every page hangs off a Q.

## 0.5 Confirm the plan

Before writing, lay out the plan for the user to approve:

```
Big problem: <one sentence>

Q1 <mid-level problem>
   Evidence: data-scaling curve (E11, redrawn from runs/*/eval.jsonl)
             context ablation (E19, redrawn from ablation.csv, adds a Δ column)
Q2 <mid-level problem>
   Evidence: held-out matrix (E12, redrawn from eval.jsonl)
             rollout frames (E13, placing figures/rollout_{0,2,4}.png)
Q3 <mid-level problem>
   Evidence: latency breakdown (E10, from bench.log into a table)
Method figure: figures/arch_v2.png (placed, on the solution page)

Results table columns: method × demos to target / held-out / long-horizon / latency
Unsolved: long-horizon at 34%, kept on the table

Redrawing 4, placing 4, dropping 2
Dropping: figures/loss_curve.png (hangs off no Q)
          figures/rollout_1,3.png (filmstrip keeps three)

Estimated 13 pages: cover + three + 9 evidence
```

Only start once the user agrees. This step looks redundant, but it is the only place a framing error gets caught before the effort of producing files.

## 0.6 When to skip

Two cases only:

- The user explicitly says "do not ask, just do it". Comply, but afterwards tell them which judgements you made on their behalf, especially which figures you dropped.
- This is an update of last week's deck and `deck.md` already exists. Then only ask about the changes: which figures are new, which Q moved, which cell of the results table updates. Do not re-interview.
