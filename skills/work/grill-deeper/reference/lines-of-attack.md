# The six kinds of node on the tree

This is **not** a menu to pick one from. Question order comes from the frontier — prerequisites settled first — not from choosing.

These six are a **completeness check**: once the design tree is laid out, sweep them and confirm no whole category is missing from it. A missing category usually means the user has not considered that dimension, not that the dimension does not apply.

**How blind spots are used**: a category the profile shows as recently vague goes early **within a round**, and gets no recommended answer. It changes the order inside a round, not the shape of the tree.

## 1. Mechanism and rival explanations

- What causal claim do you believe? One sentence of "A therefore B".
- What else explains the same observation?
- **Do your explanation and that rival predict different things?** If not, your evidence does not distinguish them.

The third question is the core of this category. The common failure is a hypothesis and its negation predicting the same thing — "adding X improved it" follows just as well from "X's mechanism works" as from "X only added capacity".

## 2. Measurement and criteria

- Which is the primary metric? Only one.
- What result would make you say this path does not work?
- What is the unit of replication? (Repeated evaluations of one training run are not independent samples.)
- Was the criterion set before or after the fact?

## 3. Scope and trade-offs

- What are you **not** doing? Why is that safe to leave out?
- If you could only do half, which half gets cut?
- What does this approach assume will not change?

## 4. Dependencies and assumptions

- What does someone else have to do first? Do they know?
- Which assumption, if wrong, brings the whole thing down?
- Is there a number here that came from someone else and you have not verified?

## 5. Failure modes

- How is this most likely to fail?
- How soon would you know?
- Is there a failure that looks like success?

The last one is the most valuable, because that kind of failure does not surface on its own.

## 6. Audience and delivery

- Who reads this? What do they already know?
- What are they most likely to challenge?
- What do you want them to do afterwards?

## Propose, do not ask openly

Once `context.md` exists, questions should be specific enough to use the vocabulary in it:

- Weak: "how does your evaluation work?"
- Strong: "is held-out still cut at the object-instance level, or did that change this time?"

The second gets a decision; the first gets a description. This is the most direct payoff of accumulating knowledge.

## Dependencies that usually order these

Useful when computing the frontier. If the left side is unsettled, the right side cannot be asked:

```
Mechanism and rivals   →  Measurement       You cannot fix a primary metric without knowing what you are verifying
Scope and trade-offs   →  Dependencies      Without a scope you do not know who you will depend on
Measurement            →  Failure modes     Without criteria, "failure" has no definition
Scope and trade-offs   →  Audience          What you deliver depends on what you did
```

These are common cases, not laws. The real dependencies come from the user's specifics; when they differ, order by the real ones.

## When to stop

**When the frontier is empty** — every branch visited, nothing silently assumed.

Not when you run out of questions (you never will), and not when the user gets impatient. When there are no unsettled nodes left.

Then give a short close: what holds up, what needs filling in, what got written back. Do not restate the conversation.
