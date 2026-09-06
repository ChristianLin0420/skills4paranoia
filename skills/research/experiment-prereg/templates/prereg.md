# Pre-registration — <one-line title>

```
Status     draft | frozen (once frozen, the primary metric and null definition do not change)
Frozen on  YYYY-MM-DD
Commit     <sha at freeze>
Budget     <GPU type × count × hours> = <GPU-hours>
```

## 1. The yes/no question

<One sentence. It must be answerable "no".>

## 2. Baseline and budget matching

| Arm | Setting | Data | Compute | Params | HP search trials |
|---|---|---|---|---|---|
| Control | | | | | |
| Treatment | | | | | |

Dimension let go, and why: <all four rarely line up; say which one and why>

**The search-trial column is the one that gets missed.** Your method tuned over 100 configurations against a baseline on defaults invalidates the comparison even with the first three matched.

## 3. Primary metric and minimum detectable effect

```
Primary metric      <only one>
Unit of replication seed (training run). Rollouts are not the unit.
Existing σ          <across seeds, not across rollouts. Source:>
Difference sought   <how large is meaningful>
Seeds needed        <invert 2.80 × σ × √(2/n)>
Seeds affordable    <what the budget allows; agreed in advance, all reported>
Rollouts per seed   <enough that each seed's mean is stable; more buys no power>
Actually detectable <recomputed from the affordable seed count>
```

Aggregation: each seed's own mean first → then mean and standard deviation across seed means. `n` = seed count.

When "actually detectable" exceeds "difference sought", write it here: **this experiment cannot detect an effect below <X>.**

Exclusion rule (defined in advance, identical for both arms): <e.g. diverged with NaN loss>

Secondary metrics: <list them, and state in advance that they cannot overturn the primary>

## 4. What counts as null

<Concrete, with numbers. e.g. the mean difference on the primary metric is under 5 percentage points, or the 95% interval crosses zero.>

## 5. Stopping and decision rules

```
Stop when   <steps / time / convergence test>
Result > X  → <next step>
Result null → <next step>
In between  → <next step>
```

Three identical next steps means the run carries no information.

## 6. Evaluation protocol

```
Held-out level      <task name / object instance / scene / demonstrator>
Intersection check  <verified / not verified>
Success criterion   <geometry + hold duration + end state + rotation invariance>
Criterion lives at  <file:function, shared by training-time and final eval>
Eval seeds          <fixed set, independent of training step, reseeded each episode>
Rollouts            <n per task × tasks × seeds>
Perturbation        <placement / instruction rewrites / initial pose / visual>
Headline number     <the perturbed value; unperturbed as an upper bound>
```

## 7. Execution environment

```
Node assignment  <does every arm span every node; do not put control on A and treatment on B>
Time span        <are the arms concurrent; far apart lets drivers and cluster load in>
Actual record    <run id → node → start and end time>
```

## 8. The most likely way this is wasted

1. <>
2. <>
3. <>

Come back and check against these.

---

## After the run

```
Result             <primary metric>
Which band         <good / null / in between>
Action taken       <does it match section 5; explain if not>
Waste cause        <did anything in section 8 land>
Protocol changes   <any post-hoc edits; if so, record them in the decision log with the reason>
```
