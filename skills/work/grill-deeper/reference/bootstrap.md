# First run in a project

The point is to make the first session more useful than generic interrogation, rather than waiting five sessions to become worth anything.

## Order

**1. Check the gitignore.** If `.grill/` is not in it, add it and say why in one line: it will hold internal detail, and this repo may be public.

**2. Read; do not ask.** No questions in this phase.

- `README.md`, `docs/`, experiment and model design notes
- The last 30 commit messages — they show what is being worked on and where it is stuck
- Past decks or reports, if any
- Config files — they show compute scale, data scale, evaluation setup

**3. Extract two kinds of thing and show them for confirmation.**

```
Pulled these out of the material — confirm or correct:

Vocabulary
  held-out means asset ids are disjoint, not that task names differ   (from scripts/check_split.py)
  the primary metric looks like mean success under perturbation        (from eval/run_eval.py, unsure)

Constraints
  64 H100s                                                            (from configs/cluster.yaml)
  12 tasks, 100 rollouts each                                         (from the eval config)

Guessed, not confident
  Seed count reads as 3, but runs/ has 6 directories at the same setting —
  is it 3 or 6?
```

**4. Write into `context.md`.** Only what the user confirmed becomes a fact. Do not write the guesses.

**5. Do not interrogate during bootstrap.** Bootstrap is bootstrap. The user is proof-reading facts here, not being challenged; mixing the two does neither well.

## How long

Under fifteen minutes. Longer means you are reading too much — you do not need to understand the codebase, only to acquire enough vocabulary and constraints to ask specific questions.

## Afterwards

`profile.md` is not part of bootstrap. Blind spots can only accumulate from real interrogation, so the first session has none. That is expected.
