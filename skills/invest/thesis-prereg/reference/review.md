# Reviews, and detecting drift

The document is dated and **not edited**. Reviews append a block. The value of the whole
exercise is the gap between what you wrote then and what you would write now — editing the
original destroys exactly the thing being measured.

## When to review

**By the horizon, and by thesis events. Never by price.**

- A scheduled cadence set from the horizon — a three-year thesis reviewed quarterly gives
  twelve reviews, most of which will correctly conclude "nothing has resolved"
- An event that bears on a claim: a result, a filing, a competitor's disclosure, a
  regulatory decision, a falsifier's observation window closing

A price move is not information about your thesis; it is information about what other people
think. Wiring reviews to price is how a portfolio ends up managed by whichever holding is
most volatile.

The exception is mechanical, not interpretive: a move large enough to change the position's
size relative to its job is a portfolio event, and belongs to `allocation-jobs`.

## The review block

```
## Review <date>

Since last: <what happened that bears on a claim>

| Claim | Status | Evidence |
|---|---|---|
| 1 | holding / weakened / falsified / resolved | |

Falsifier fired: <which, or none>
Why I hold it today: <in your own words, before rereading the original>
Drift: <yes/no — see below>
Action: <none / trim / close / add>, and which pre-committed condition it matches
```

**Write "why I hold it today" before rereading the original.** Reading first contaminates it,
and that sentence is the entire drift test.

## Drift

Compare today's reason for holding against the frozen claims.

| | |
|---|---|
| Today's reason is in the original | Fine. The thesis is doing its job |
| Today's reason is a *consequence* of the original | Fine, and worth noting the chain |
| **Today's reason is not in the original** | **Drift** |

Drift is not an update. It is a new, untested thesis wearing an old one's clothes — and it
arrives precisely when the original is failing, because that is when a replacement reason is
most needed.

Two honest responses, and neither is "note it and carry on":

1. **Write the new thesis its own document**, with its own claims, falsifiers and horizon, and
   date it today. If it will not survive being written down, it was not a reason.
2. **Close the position.** The original reason is gone.

The tell: the new reason is usually vaguer than the old one, and usually longer-dated.

## Firing a falsifier

When a falsifier fires, the pre-committed action happens. That is the whole point of having
written it down while you had no position at risk.

If you now want to override it, the override gets written into the review with its own
reasoning — because an override you can see is survivable, and one you do silently is how a
process stops existing. Two overrides on one position and the process is not being used.

## What reviews are not

- **Not a place to restate the thesis more persuasively.** Persuading yourself is the failure
  mode, not the goal
- **Not performance attribution.** Whether the price went up is not whether the thesis was right
- **Not a decision meeting.** The decisions were pre-committed; a review checks which
  conditions were met
