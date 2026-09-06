# Verification

The map claims things about code you have just met. This step decides whether you are entitled to those claims.

## Two probes

Forward hooks fire on `nn.Module.forward`. Dataset transforms are plain functions with no module to hook, so hooks cover the model and nothing before it. Two probes, different mechanisms:

| Probe | Covers | Mechanism |
|---|---|---|
| Batch probe | source → batch | pull one batch, record what is in it |
| Module hooks | encoders → loss | `register_forward_hook` on every named module |

Run both **twice** — once with the train loader and `model.train()`, once with the eval loader and `model.eval()`. The train/eval toggle is a claim about two runs; one run cannot support it.

## Harness

Write it to the repo's scratch directory, not into the repo. **Add it to `.gitignore` if you must keep it** — it is a debugging artifact and it will confuse the next person.

```python
# flowcheck.py — throwaway
import json, torch

RECORD = []

def describe(x):
    if torch.is_tensor(x):
        d = {"shape": list(x.shape), "dtype": str(x.dtype), "device": str(x.device)}
        if x.is_floating_point() and x.numel():
            f = x.detach().float()
            d |= {"min": round(f.min().item(), 4), "max": round(f.max().item(), 4),
                  "mean": round(f.mean().item(), 4)}
        return d
    if isinstance(x, (list, tuple)):
        return [describe(v) for v in x]
    if isinstance(x, dict):
        return {k: describe(v) for k, v in x.items()}
    return type(x).__name__

def instrument(model):
    """Hook every named module. Returns handles — remove them when done."""
    handles = []
    for name, mod in model.named_modules():
        if not name:                      # the root's hook fires last and adds nothing
            continue
        def hook(m, args, kwargs, out, _n=name):
            ps = list(m.parameters())     # recurse: a container's own params are usually empty,
            trainable = sum(p.numel() for p in ps if p.requires_grad)   # and recurse=False would
            total = sum(p.numel() for p in ps)                          # call every wrapper frozen
            RECORD.append({"module": _n, "cls": type(m).__name__,
                           "training": m.training,
                           "trainable": trainable, "params": total,
                           "in": [describe(a) for a in args],
                           "kwin": {k: describe(v) for k, v in kwargs.items()},
                           "out": describe(out)})
        try:
            handles.append(mod.register_forward_hook(hook, with_kwargs=True))
        except TypeError:                 # torch < 2.0 has no with_kwargs
            handles.append(mod.register_forward_hook(
                lambda m, a, o, _h=hook: _h(m, a, {}, o)))
    return handles

def run(model, loader, mode, path):
    """One batch through the model. `mode` is "train" or "eval"."""
    RECORD.clear()
    model.train() if mode == "train" else model.eval()
    batch = next(iter(loader))
    with torch.no_grad():
        h = instrument(model)
        out = model(**batch) if isinstance(batch, dict) else model(batch)
        for x in h: x.remove()
    json.dump({"mode": mode, "batch": describe(batch), "modules": RECORD},
              open(path, "w"), indent=1)
    return out
```

Call it twice:

```python
run(model, train_loader, "train", "flow.train.json")
run(model, eval_loader,  "eval",  "flow.eval.json")
```

`torch.no_grad()` keeps memory down and does not change which modules fire. If the model needs the loss to reach some branch, drop it and take the memory hit — a branch that only runs under grad is exactly the branch worth verifying.

Two things this harness gets right that a naive version does not, and both produce **wrong verifications** rather than obvious errors:

- **`with_kwargs=True`.** A module called as `sub(x=..., mask=...)` has an empty positional `args`, so a hook without kwargs records a module that appears to receive nothing.
- **`parameters()` recursing.** With `recurse=False` a container like `VisionEncoder` owns no parameters directly, so it reports as frozen no matter what is inside it — and check 4 then passes on a module that is fully trainable. Frozen means `trainable == 0`, counted over the subtree.

## Before anything else: is the record non-empty?

```python
assert RECORD, "no hook fired — the map cannot be verified from this run"
```

**Checks 2–6 are all trivially satisfied by an empty record.** If the hooks never registered — the model was wrapped in DDP or `torch.compile` after instrumentation, the forward went through a different object than the one you hooked — every shape comparison passes because there is nothing to compare, and you would ship a green banner backed by nothing. Count the modules first and sanity-check the number against the map.

## Pass criteria

Read both JSON files against the map. **Every one of these must hold.**

| # | Check | A failure means |
|---|---|---|
| 1 | Every node with `kind:"module"` appears in `modules` | The map draws a module that never runs — usually a config branch you resolved wrongly |
| 2 | Every shape on the map matches the recorded shape | You read a `reshape` wrong |
| 3 | Every module in the record is either on the map or deliberately collapsed | Something real is missing; account for it or add it |
| 4 | `training` and `trainable` match the `frozen` claim on both runs | `requires_grad=False` without `.eval()` — dropout and BN are still live in a module you called frozen |
| 5 | Nodes marked `train only` / `eval only` appear in exactly that one record | The map's headline claim is wrong |
| 6 | The batch's dtypes and value ranges match the map's normalisation claim | Inputs are not normalised the way the map says |

Check 4 is the one that repays the whole exercise. It is the same root cause as `vla-code-review` 4.1, and it is invisible in a code read because the two calls are in different files.

## When it fails

**A mismatch is a bug in the map, not a reason to weaken the map.** Fix the map, rerun, until every check passes. Then set `verified: true` and write what you ran into `verifiedNote`.

Do not set `verified: true` with a note like "mostly matched".

## Frameworks without forward hooks

The harness above is PyTorch. On the JAX / Flax path — openpi, and most of Physical Intelligence's stack — `register_forward_hook` has no equivalent, because after tracing there are no module objects left: a jaxpr is a flat list of primitives. Say so on the map rather than quietly downgrading to guesswork.

What you still get, and what you lose:

| Want | JAX equivalent | Strength |
|---|---|---|
| Every declared shape | `jax.eval_shape(model.compute_loss, *specs)` with `jax.ShapeDtypeStruct` inputs | **Strong, and free** — no data, no accelerator, no weights |
| The real op sequence | `jax.make_jaxpr(fn)(*args)`, or `.lower(...).as_text()` for StableHLO | Strong, but flat — primitives, not your module names |
| "Did this module fire?" | Nothing direct. Needs `self.sow(...)` added to the model | **Weak** — you are editing the code you came to read |

`eval_shape` is the one worth reaching for first. It runs abstractly, so it verifies the whole shape contract on a laptop before the cluster account arrives — openpi already builds the input specs you need at `src/openpi/models/pi0_config.py:80`.

So a JAX map can honestly reach `verified` on shapes while every module node stays `static`. That is a real tier, and it is better than the alternative of claiming a hook run you cannot do. **Put which one you ran in `verifiedNote`**, not just that you ran something.

## The tier in between: audit what you wrote

Between "no check at all" and a forward pass there is a third thing, and it is cheap, mechanical, and catches the failure mode a map is most prone to. **Read every citation back against the source.**

```python
# for every file:line on the map, and every one buried in a detail or a note
line = open(path).read().splitlines()[n - 1]
print(node_id, path, n, line.strip())
```

Then check the graph itself, which needs no source at all:

| Check | A failure means |
|---|---|
| Every `file:line` resolves, and the line says what the node claims | A citation drifted, or was never read |
| No cycles on either path | You drew a dependency backwards |
| No **dead edge** — `paths(edge) ∩ paths(from) ∩ paths(to)` is empty | An edge that can never be live; usually a path label copied from a neighbour |
| No node **isolated** on a path it claims to be on | The node is on that path in name only — something it connects to was drawn as a separate node |
| Every node traces back to a source and forward to a sink | A fragment left over from an earlier draft |
| Inferential claims re-derived in isolation | The claim was plausible rather than checked |

This tier was worth doing. Run across the three example maps it found **19 wrong line numbers** out of 137 citations, and two real modelling errors that reading alone had missed: a backbone drawn with no edges at all on the eval path, because `generate()` had been drawn beside the language model rather than downstream of it; and an edge marked eval-only whose source node was train-only, so it could never appear.

A map that passes this is still `verified: false` — no shape has been observed. Say which check you ran in `verifiedNote`, because "audited but not run" and "not checked at all" are as different as "checked clean" and "not checked".

## When it cannot run

Common in week one: no data, no cluster, half the dependencies missing. Ship the map anyway, with:

- `verified: false` — this puts the red banner at the top of the file
- every unconfirmed node at `conf: "inferred"`, so it renders dashed
- a note in the summary saying exactly what blocked the run

An unverified map is still worth having — it tells you which seven files matter out of four hundred. It is only dangerous when it is dressed as a verified one.

**Do not fabricate a batch to get a green banner.** A `torch.randn` batch verifies the model's plumbing and tells you nothing about the data path, which is half the map and the half where the bugs are. If you use synthetic input to sanity-check shapes, that is fine — but the map stays `verified: false` and the note says the input was synthetic.

Upgrade later: when the environment works, rerun and flip the banner. That is a two-minute job, and it is the reason the map is a data object rather than hand-written HTML.
