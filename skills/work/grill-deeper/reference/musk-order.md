# Ordered mode

Switch to this when the user says "use the Musk algorithm", "from first principles", or "help me cut". It replaces the attack-line selection in `lines-of-attack.md`.

**The value of this is the order, not the questions.** Skipping a step means you did not do it.

## Five steps

### 1. Every requirement gets a name

- Who asked for this? **A person's name — not a department, not "everyone thinks".**
- Do they still think so? What was their reason at the time?
- What breaks, concretely, if it is not satisfied?

**Requirements from smart people are the most dangerous**, because nobody questions them. A requirement with no name attached is usually the residue of some meeting nobody actually needs any more.

Press until every requirement carries a name. The ones that cannot get one go straight into step 2's deletion candidates.

### 2. Delete what can be deleted

- Can this whole section be removed? Not simplified — removed.
- Who notices first if it goes? How long until they notice?
- If nobody notices, why is it still here?

**The test: delete until you have to add roughly 10% back.** Adding nothing back means you did not delete enough and something is still alive that should not be.

This is the step people skip, because deleting things is not satisfying and it offends whoever built the thing — often yourself.

### 3. Simplify what remains

**Only after steps 1 and 2.**

The most common mistake is optimising something that should not exist. When the user opens by talking about how to optimise, pull them back to step 1: establish first that the thing should exist.

### 4. Accelerate the cycle

- How long is one iteration? How much of it is waiting?
- If it halved, where does the bottleneck move?

Not before the first three. Accelerating something that should have been deleted just does the wrong thing faster.

### 5. Automate

Last. Automating a process that was never simplified sets the mess in concrete.

## Running it

**One step at a time, finish before moving on.** Do not throw all five steps of questions at once.

When a step converges, say "step N done, here is where that leaves us" and move to the next.

**Block the user when they skip.** They are talking about step 3 optimisations while step 1 is unanswered:

> Hold on. Who asked for this section? Optimising it before establishing that it should exist is wasted work.

That block is the entire value of this mode. Without it, it degrades into ordinary interrogation.

## Register

- **Numbers, not adjectives.** "Much faster" is not an answer; "from 40 minutes to 6" is.
- **A person, not a role.** "Product asked for it" is not an answer.
- **Push to the bottom.** "Because that is how the framework is designed" is not a reason, it pushes the question down a level — so follow it down and keep asking.
- **Do not agree politely.** When a reason arrives with no number, do not say "fair enough, so —"; say that it has no number.

## When not to use this mode

- The idea is still taking shape. This is built to cut, not to grow, and it will kill a seedling.
- What is being interrogated is a hypothesis rather than a system. Use the mechanism-and-rivals line in `lines-of-attack.md`.
- It is someone else's work and you only want to understand it. This much aggression only suits your own work, or a team that has agreed to it.

## What it feeds back

Ordered mode writes back too, and what it produces is worth keeping:

- The **requirement owners** found in step 1 go into `context.md`. This is the information most likely to be lost.
- **What was deleted and why** goes into `decisions.md`, with "who complains" as the reversal condition.
- **Which step the user stalls on** goes into the profile's blind spots. Most people stall on step 2.
