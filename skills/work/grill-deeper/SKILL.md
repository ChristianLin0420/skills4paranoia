---
name: grill-deeper
description: >-
  Interrogate a plan, design or decision until every branch of it has been visited — and
  remember the person you are interrogating. Questions are scheduled on a design tree, and a
  store accumulates your vocabulary, settled decisions, open assumptions, constraints, and the
  kinds of question you go vague on, so the questions get sharper and more specific to your work
  each time. Two modes: the default hunts holes, the ordered mode cuts (question the
  requirement, delete, simplify, accelerate, automate, no skipping). Use when someone wants
  their plan, design, hypothesis or decision stress-tested before committing to it, says
  challenge this / is this right / what am I missing, or asks what they decided before and why.
  Chinese triggers: 幫我挑戰這個 / 拷問我 / 這樣想對嗎 / 有沒有漏掉什麼 / 我當初為什麼這樣決定 / 用馬斯克那套問我 / 幫我砍.
---

# grill-deeper

Interrogate until every branch of the design tree has been visited, then remember what this session taught you.

> The design-tree and frontier mechanism is taken from `grilling` in [mattpocock/skills](https://github.com/mattpocock/skills) (MIT). What this adds is a memory layer that persists across sessions.

**Language.** Write in whatever language the user writes in. These instructions are in English because English is this repo's source language, not because the output must be English. A Chinese user gets Chinese questions and a Chinese summary; the structure is identical either way.

## The design tree and the frontier

Lay the thing out as a **design tree**: every decision branches into the decisions that hang off it.

The **frontier** is the ring of questions whose prerequisites are already settled — the ones you can ask *now* without guessing at answers you have not heard yet.

**Ask the whole frontier in one round.** Number each question, attach your recommended answer, then wait. The answers reshape the tree: settled decisions push the frontier outward and unblock questions that depended on them. Recompute, ask the next round.

**A question whose answer depends on another question still open this round belongs to a later round.** This is the point of the whole mechanism; break it and you ask things the user cannot answer yet.

**The session ends when the frontier is empty** — every branch visited, nothing silently assumed. Do not act on any of it until the user confirms you have reached a shared understanding.

## How memory shrinks the tree

This is what separates it from stateless interrogation. **A known fact is a settled node**, so the first round's frontier starts further out.

| In the store | On the tree |
|---|---|
| Vocabulary and constraints in `context.md` | **Settled nodes** — do not ask, just use them |
| Decisions in `decisions.md` still marked active | **Settled**; reopened when the reversal condition fires |
| `open-questions.md` | **Unsettled nodes**, already on the tree from the start |
| Blind spots in the profile | Do not reshape the tree; they order questions **within a round** |

Concretely: with no store, round one asks "how does your evaluation work". With one, that node is already settled and round one asks "does the perturbation stay at last time's ±3cm". **Same round, two levels deeper.**

Each session also sweeps for stale entries (rules below). A stale node goes from settled back to unsettled and rejoins the frontier — but **reopen at most one per round**, or the session turns into an inventory review.

## Question format

```
❓ **Q1** — **<title>**: <body, may be several paragraphs, may offer choices>

➡️ <your recommended answer>

---

❓ **Q2** — **<title>**: <...>

➡️ <your recommended answer>
```

The recommended answer lets the user say "yes to all but Q3" and move a long way in one round.

**Exception for blind-spot questions: give no recommended answer.** When the profile shows this is a category the user goes vague on, supplying an answer is exactly how they skate past the thing they need to face. Ask, and offer no ledge.

## Finding facts is your job

**Never the user's.** When a question on the frontier needs a fact from the environment — a file, a config, a run record — go and get it. Do not ask the user for anything you could look up.

**Do not block on it**: a running lookup is an unsettled prerequisite, so only the questions downstream of it wait. Ask the rest of the frontier now.

Write what you find into `context.md`. **Look something up once and it never gets looked up again** — this is the memory layer's most direct payoff.

## Two modes

**Default** — design tree and frontier, for hunting holes. The six kinds of node are in `reference/lines-of-attack.md`.

**Ordered** — switch when the user says "use the Musk algorithm", "from first principles", or "help me cut". Five steps in strict order, no skipping: see `reference/musk-order.md`. This mode sets the design tree aside, because its order is fixed rather than derived from dependencies.

Use the ordered mode to cut. **Do not use it on an idea that is still growing** — it is built to remove things and it will kill a seedling.

## Pairing with plan mode

**Grill first, then plan.** Once plan mode produces an implementation you anchor on it, and every later question attacks whether the implementation is right rather than whether the thing should exist at all.

Two practical limits: **plan mode is read-only**, so writeback to `.grill/` will fail — do the grilling outside it. And feed the closing summary into plan mode as input; the plan comes out noticeably better when the requirements have already been cut once.

Exception: the plan already exists (someone handed it to you, or you wrote it last week). Then grill the plan.

## Input and output

**Input**: the thing to be interrogated — a paragraph, a design doc, a PR, an idea you have not started. The store at `<project>/.grill/` and `~/.claude/grill/profile.md` are read automatically. On the first run in a project, bootstrap first: see `reference/bootstrap.md`.

The input does not need to be tidy. **A half-formed idea is exactly the right thing to interrogate**; by the time you have tidied it you are too invested to cut it.

**Output**: one round of questions at a time; once the frontier is empty, a short summary — what holds up, what needs filling in, what got written back. Side effect: at most five entries into `.grill/` plus one session record.

**What it does not output**: answers, decisions, or a plan. It asks and records; the judgement is the user's.

## Two layers of knowledge

| Layer | Location | Holds | Why separate |
|---|---|---|---|
| Project | `<project>/.grill/` | Vocabulary, decisions, open assumptions, constraints | Belongs to the project |
| Global | `~/.claude/grill/profile.md` | Blind spots, habitual deflections, repeated pitfalls | **Follows the person** across projects and jobs |

`.grill/` **must be in `.gitignore`**. It will hold internal project names, compute quotas and unpublished results. Structure in `reference/store.md`.

## Answer quality and writeback

Mark every question crisp, vague, or unknown:

| Mark | Test |
|---|---|
| Crisp | A specific number, name, file location, or an explicit trade-off |
| Vague | Only a category or an adjective: "roughly", "should be fine", "still tuning" |
| Unknown | Says outright they do not know, or defers |

**Unknown is healthier than vague.** Unknown is actionable; vague leaves misplaced confidence standing. Do not press someone who says they do not know.

**Write back at most five entries.** Pick the ones that will change the next session's questions: new vocabulary, a decision just settled, an assumption overturned, a clear blind spot.

**Stop raising a blind spot after the third time with no progress.** On the fourth, say once: "this is the fourth time — shall we just deal with it", then drop it. The way an interrogation tool dies is by nagging, and once you stop opening it, it is worth nothing.

## Decisions live here

Record four things for every non-obvious decision: **the decision, the alternative considered, what evidence would reverse it, and the date.**

The third field is the important one, and it is also how a decision expires: **age does not stale a decision, its reversal condition coming true does.**

## Memory rots

An unmaintained store lets the skill ask confident questions from premises that expired, which is worse than knowing nothing.

| Type | Marked for reconfirmation when |
|---|---|
| Fact / vocabulary | 90 days without reconfirmation |
| Decision | Never by age; when its reversal condition fires |
| Open assumption | 60 days unresolved → ask once whether it is still open |
| Blind spot | Only the last 10 sessions count; older ones fade out |

## What this is not

- **Not meeting minutes.** Store only what will change the next session's questions, never a transcript.
- **Not project management.** No progress tracking, no todos.
- **Not a decision-maker.**

## Files

- `reference/store.md` — structure and fields of both layers
- `reference/lines-of-attack.md` — the six kinds of node that appear on the tree
- `reference/musk-order.md` — the ordered mode
- `reference/bootstrap.md` — first run in a project
- `templates/` — starting skeletons for `.grill/` and the profile
