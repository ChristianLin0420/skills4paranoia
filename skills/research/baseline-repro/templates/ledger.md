# Reproduction — <baseline> vs <ours>

**Verdict.** <One sentence. The reader should be able to stop here.>
<their number> reported · <yours> measured · <gap> · <what accounts for it>

**Scope.** Testing <the exact claim, table and row>. Not testing <what you are not>.

---

## What accounts for the gap

<Contributing factors, not a root cause. Two ordinary things compounding is the
common case; one dramatic thing is not.>

| Factor | Theirs | Ours | Cost to close | Recovered |
|---|---|---|---|---|
| | | | | |
| | | | | **total** |

<One short paragraph per factor: what it is, and why it costs what it costs.
Name the ones with no trace in any config — those are the ones a diff misses.>

## Bisection

| Cell | Weights | Harness | Number | Reading |
|---|---|---|---|---|
| ① | theirs | theirs | | |
| ② | theirs | yours | | |
| ③ | yours | theirs | | |
| ④ | yours | yours | | |

<Which half it localised the gap to, and what that saved. An unrun cell is not a
passing cell — say which and why.>

## Ledger

<n> of <n> rows closed, <n> without compute. Full table below; only rows that are
not `same` are worth reading.

| Axis | Theirs | Ours | State | Explains gap | Cheapest test |
|---|---|---|---|---|---|
| | | | `differs` | | |
| | | | `unknown` | | |

<details><summary><n> rows checked and identical</summary>

<Name them in one line each, or one comma-separated line. They are evidence that
the ledger was actually worked, and they are not worth a reader's attention.>

</details>

## What was easy · what was difficult

<Two lists, kept separate because they are co-dependent rather than opposite:
released weights can make the start trivial while an unstated eval convention
makes the middle expensive. This is what tells the next person what to budget.>

**Easy** —
**Difficult** —

## Where this bites beyond the one number

<The findings that outlive this comparison. A house rule in your own harness
applies to every model that harness has ever run; a convention you inferred from
one repo you will infer again.>

## Action items

| # | Action | Owner | By |
|---|---|---|---|
| 1 | | | |

<Each one traceable to a factor above. No owner and no date is a wish.>

## Still unknown

<Every row left `unknown` that could account for the gap. While this list is
non-empty, "does not reproduce" is not an available verdict.>
