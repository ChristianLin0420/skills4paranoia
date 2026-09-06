# The knowledge store

Two layers. The project layer belongs to the project; the global layer follows the person.

## Project layer: `<project>/.grill/`

**Check it is in `.gitignore` first.** It will hold internal project names, compute quotas and unpublished results. Handle this when the store is first created, not afterwards.

Four files. Do not add more.

### `context.md` — the stable facts

Vocabulary, definitions, environment constraints. These change rarely but every session uses them.

```markdown
## Vocabulary
- held-out: cut at the object-instance level (asset ids disjoint), not by task name  ·2026-09-06
- primary metric: mean success over 12 held-out tasks under perturbation  ·2026-09-06

## Constraints
- Compute: 64 H100s, median cluster queue 6 hours  ·2026-09-06
- Audience: the team on Fridays, a cross-group review at quarter end  ·2026-09-06
- Interfaces: on-robot integration is another group's; latency budget 30Hz  ·2026-09-06
```

Every entry dated. Anything unconfirmed for 90 days becomes one opening question next session: "does this still hold?"

### `decisions.md` — decisions and their reversal conditions

```markdown
## Freeze the WAM-v1 architecture  ·2026-09-05
Decision   No new backbone branches in Q4
Alternative Keep searching (20 weeks, 800 GPU-months)
Reverses if Long-horizon success has not cleared 55% by mid-December
Status     active
```

**The reversal condition is the important field**, and it is also how the decision expires — age does not stale a decision, its condition coming true does. Sweep these at the start of each session and mark any whose condition has fired as `reopen`.

### `open-questions.md` — assumptions still open

```markdown
- [open] Is long-horizon failure lost context or insufficient force control  ·2026-08-20
- [falsified] A larger backbone solves sample efficiency  ·2026-08-14 → bought only 7 points
- [confirmed] 4:1 sim mixing works  ·2026-08-28 → ablation shows +14pp
```

Anything still open after 60 days gets asked once: is it still open, or is there an answer? Keep the falsified and confirmed ones — they stop things being retested.

### `sessions.md` — the session log, append only

```markdown
## 2026-09-06
Line       evaluation protocol
Crisp      primary metric definition, seed count
Vague      the specific perturbation parameters, how the held-out split was verified
Unknown    the baseline's hyperparameter search budget
Wrote back context: primary metric / open-questions: perturbation parameters undecided
```

Marks and writebacks only, never a transcript. This file exists to compute blind spots, not to minute the meeting.

## Global layer: `~/.claude/grill/profile.md`

One file. It follows the person across projects and jobs.

```markdown
## Blind spots (last 10 sessions)
- Evaluation protocol: vague in 4 of 5. Habitual deflection is "same as last time",
  but last time was not written down either.
- Cost estimates: unknown in 3 of 3. Tends to underestimate queue time.
- Mechanism hypotheses: consistently crisp, no need to spend time here.

## Repeated pitfalls
- Caught three times by an unmatched baseline budget  ·2026-04, 2026-06, 2026-08

## Habitual deflections
- When asked for a number they are unsure of, switches to talking about the mechanism.
  Pull the topic back to the number.
```

**Only the last 10 sessions count**; older ones fade out. People improve, and the profile has to keep up rather than relitigating a weakness from six months ago.

The last section is the most useful part of this file and the one that needs the most restraint — it describes a behaviour pattern, it does not rate the person. Write "switches to the mechanism when asked for an uncertain number", never "is bad at quantifying".
