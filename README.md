# skills4paranoia

Agent skills, organised by topic. Plain markdown, nothing to install.

The name is not a joke. Every skill here does the same thing: **it makes you prove the part you skipped.**

The deck skill will not let a page stay that supports no stated problem. The code review hunts the failures that never raise and only cost you a few points. The pre-registration refuses a run with no definition of what failure looks like. These are disciplines you already know; you skip them when you are in a hurry. This repo turns them into checks that hold.

```
skills/
  work/                     ← topic: the ones that follow you to a new job
    grill-deeper/           ← skill
    research-deck/
    deck-design-system/
    research-figures/
    codebase-onboarding/
  research/                 ← topic: doing the research itself
    experiment-prereg/
    vla-code-review/
```

Add a topic by creating a folder under `skills/` and adding the paths to the `skills` array in `.claude-plugin/plugin.json`. Nothing else changes.

**Language.** English is the source language; every skill states that its output follows the user's language. Ask in Chinese and you get Chinese questions, a Chinese report and a Chinese deck, with the same structure.

## Installing

Two routes. Pick one — installing both leaves you with every skill twice.

### Claude Code (managed, updates automatically)

```bash
claude plugin marketplace add ChristianLin0420/skills4paranoia
claude plugin install skills4paranoia
```

Or from inside a session:

```
/plugin marketplace add ChristianLin0420/skills4paranoia
/plugin install skills4paranoia
```

### Codex and other agents (editable copies)

```bash
npx skills@latest add ChristianLin0420/skills4paranoia
```

The installer asks which skills and which agents. For just one:

```bash
npx skills@latest add ChristianLin0420/skills4paranoia --skill research-deck --agent claude-code
```

### Manually

```bash
git clone https://github.com/ChristianLin0420/skills4paranoia
cp -R skills4paranoia/skills/*/* ~/.claude/skills/
```

`skills/*/*` flattens every topic into the agent's skill directory — the agent does not know about topics, the layering exists only in this repo. Copy into a project's `.claude/skills/` to scope it to one project.

### Updating

```bash
npx skills@latest update -g -y
```

Or, on the plugin route, `claude plugin marketplace update christianlin0420` then `claude plugin update skills4paranoia`, and restart.

## Topics

### work

Communication and record-keeping. These survive a change of role.

| Skill | What it covers |
|---|---|
| [`grill-deeper`](skills/work/grill-deeper) | Interrogates a plan on a design tree, and accumulates an understanding of your work so it gets sharper each time |
| [`research-deck`](skills/work/research-deck) | Structure and process: problem → solution → results, and how evidence attaches |
| [`deck-design-system`](skills/work/deck-design-system) | Appearance: palette, type scale, grid, per-layout geometry |
| [`research-figures`](skills/work/research-figures) | Figures: curves with error bands, matrices, ablation tables, reference lines, conditions footnotes |
| [`codebase-onboarding`](skills/work/codebase-onboarding) | Maps the data path through an unfamiliar model repo, with shapes on every edge, and verifies it against a real forward pass. Worked examples for [openvla](skills/work/codebase-onboarding/examples/openvla.html), [openpi](skills/work/codebase-onboarding/examples/openpi.html) and [VITRA](skills/work/codebase-onboarding/examples/vitra.html) |

**[See six sample pages](skills/work/research-deck/examples/preview)** — the front three, and three evidence pages showing the density this aims at.

The deck trio's claim is that **the front three pages carry the whole argument and everything after them is evidence**: one big problem split into 2–4 mid-level problems, a solution row for each, and a results table that keeps the cell that is not solved. Every page from the fourth on declares `solves=Qn`; anything that attaches to no problem is deleted.

No "here is what I need you to decide" page — that is how an internal proposal is written, not a research deck. No wall of numbers — showing only the wins is promotion.

More in [skills/work/README.md](skills/work/README.md).

### research

Doing the research itself.

| Skill | What it covers |
|---|---|
| [`experiment-prereg`](skills/research/experiment-prereg) | Pin the measurement contract and freeze it |
| [`vla-code-review`](skills/research/vla-code-review) | Hunts the engineering failures that never raise and only make the numbers worse |
| [`baseline-repro`](skills/research/baseline-repro) | Bisects a gap against a published number and ledgers every axis on which the two setups differ, before anyone says "does not reproduce" |

Complementary: one covers whether you defined what "right" means, the other whether the code is quietly wrong.

More in [skills/research/README.md](skills/research/README.md).

## tools/

`tools/deck-renderer` is a working Python reference implementation (markdown → `.pptx` plus an SVG preview). **It is not part of the skills and is not copied on install.** It exists because the geometry in the skills came from it, and because it can verify what an agent produces.

```bash
cd tools/deck-renderer
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/python -m deckkit.build examples/meridian-1.zh.md -o out/deck.pptx --preview
```

## Licence

MIT
