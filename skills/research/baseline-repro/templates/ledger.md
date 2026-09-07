# Reproduction ledger — <paper / baseline> vs <your setup>

**Their number**: <value> on <benchmark>, from <paper §x / repo README / table N>
**Your number**: <value>, <n> episodes × <n> seeds
**Gap**: <value>

## Bisection

| Cell | Weights | Harness | Number | Reading |
|---|---|---|---|---|
| ① | theirs | theirs | | |
| ② | theirs | yours | | |
| ③ | yours | theirs | | |
| ④ | yours | yours | | |

<!-- Not run? Say which and why. An unrun cell is not a passing cell. -->

## Ledger

`same` = checked and identical · `differs` = checked and different · `unknown` = not determined

| Axis | Theirs | Yours | State | Could explain the gap | Cheapest test |
|---|---|---|---|---|---|
| Success criterion | | | | | |
| Episode limit | | | | | |
| Episodes per task | | | | | |
| Reset distribution | | | | | |
| Aggregation | | | | | |
| Seeds | | | | | |
| Simulator version | | | | | |
| Assets | | | | | |
| Camera | | | | | |
| Control frequency | | | | | |
| Observation space | | | | | |
| Checkpoint identity | | | | | |
| EMA or live weights | | | | | |
| Sampling constants | | | | | |
| Chunk execution | | | | | |
| Normalisation statistics | | | | | |
| Action space convention | | | | | |
| Inference precision | | | | | |

<!-- Add training rows only once the bisection puts the gap there. -->

## Verdict

<!-- Exactly one. -->

- [ ] **Accounted for** — <axis> was `differs`; closing it moved the number to <value>
- [ ] **I am measuring something else** — <axes> differ and account for the gap; not a disagreement about the method
- [ ] **Their setup has an advantage** — <what>; not available to me, and named
- [ ] **Real disagreement** — ledger empty, gap survives ①. Reported with this ledger attached
- [ ] **Cannot be attributed** — <n> rows still `unknown`; code or weights unavailable

## Still unknown

<!-- Every row that stayed `unknown` and could account for the gap. If this list is
     non-empty, "does not reproduce" is not available as a verdict. -->
