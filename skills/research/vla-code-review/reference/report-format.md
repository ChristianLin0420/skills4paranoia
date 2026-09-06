# Report format

`templates/report.html` is ready to adapt. This is the specification, and why each region exists.

## Order of regions

Top to bottom, not interchangeable — it matches the reader's decision order.

| Region | Answers |
|---|---|
| Title and environment | Whose code, which commit, what hardware |
| **Verdict** | Can I launch right now |
| Four tallies | How bad, and how much |
| Tier 0 gate table | Which of the ten fatal items passed |
| Findings, by severity | What each problem is, how to confirm it, how to fix it |
| Coverage matrix | How much you actually checked |
| Beyond static review | What is still uncovered |

## The verdict

One sentence in plain language, at the top, in a bordered and tinted block.

Write "do not launch: the multi-GPU gradients are not synchronised and the checkpoint may not have loaded, so the conclusions from this batch are unusable", not "7 issues found, 2 serious". The counts are the next region; this one is a judgement.

Three verdicts: `do not launch` (any blocker), `launch, but read these first` (any high), `clear` (only medium and watch).

## The environment row

Commit, GPU model and compute capability, framework version, review time. Monospaced.

**These four are not decoration.** Precision compatibility, kernel availability and TF32 defaults all depend on them, and the report gets pasted elsewhere — out of context, these four are the only way to reconstruct the situation.

## The four tallies

Blocker / high / medium / pass. Monospaced numerals, a 2pt colour bar above each: brick for blocker, accent for high, grey for the rest.

Do not add an N/A tally. N/A belongs in the coverage matrix, and putting it here dilutes the visual weight of severity.

## The Tier 0 gate table

Its own table, because it answers "can I press launch", which is a different question from the other findings. Per row: number, check, result, location. Failures in brick and medium weight; passes and N/A both grey — **do not make passes green**, that draws the eye to the least important information.

## Finding cards

A 3pt colour bar on the left for severity. Header row: severity tag, check number, title, `file:line`. Body is a definition list: symptom, cause, how to confirm, fix. A rule, then the precedent link.

**Titles state the phenomenon, not the rule.** Write "action-head gradients are not synchronised across ranks in multi-GPU training", not "violates DDP usage guidelines".

`file:line` monospaced and in the accent colour, so it is findable at a glance.

## The coverage matrix

Eleven categories by checked / pass / found / N/A. Zeros in pale grey, no symbol other than 0.

The purpose of this region is **to make visible what you did not check**. If some category's checked count is conspicuously low, that is a weakness in the report and it should be seen.

## Beyond static review

Last, with an accent bar on the left. List each check that needs an actual run, and why.

**This region cannot be dropped.** Not checked and checked-clean are different things, and a blank reads as a pass.

## Visual specification

Follows `deck-design-system`: bg `#F1F2F3`, ink `#14171A`, secondary `#5F656B`, footnote `#8A9096`, hairline `#DCE0E3`, accent `#3A6183`. Severity adds one brick `#8C4A3C`, used only for blockers.

IBM Plex Sans plus Noto Sans TC; every number, path, line number and command in IBM Plex Mono.

No green. Passing is the expected state and needs no visual reward; save colour for the things that need someone to act.
