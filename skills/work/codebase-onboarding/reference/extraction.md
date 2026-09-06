# Building the skeleton

The failure mode of this step has a name: **drawing the architecture these repos usually have.** You have read a lot of VLA and world-model code, the shapes rhyme, and a confident wrong map is indistinguishable from a right one until it costs someone a week.

The defence is mechanical. **Every node carries a `file:line` you opened.** If you cannot cite it, it is not a node.

## Order of work

Follow the data, not the file tree. Start at the entry point's step function and walk outward in both directions.

```
train.py:step()  ──► what does it call?          ──► model.forward
                 ──► where does `batch` come from? ──► DataLoader ──► Dataset.__getitem__ ──► disk
```

Backwards to disk first, forwards to the loss second. Backwards is where the surprises are: the transform chain is usually spread over three files and applied in an order nobody wrote down.

## What to read, in order

1. **The entry point's step/train loop.** One function. It names the model, the loader, the loss, and the optimiser.
2. **`Dataset.__getitem__` and the collate function.** The whole preprocessing chain hangs off these two. Record the order transforms are applied in — the order is part of the answer.
3. **The eval loader's construction.** Usually a different call site with different arguments. Diff it against the train one by hand; this is where `train only` and `eval only` come from.
4. **`Model.__init__`.** Submodule composition, and every `requires_grad`, `.eval()`, `freeze()`, LoRA wrap, or `.half()` in it.
5. **`Model.forward`.** Call order and the tensor names. This is the spine of the map.
6. **The loss.** What it reduces over, and whether a mask reaches it.
7. **The config that was actually used.** Not the default YAML — the one the entry point loads, plus any CLI override in the launch script.

## Grep list

These find the annotations that matter, and they are fast:

```bash
grep -rn "requires_grad\|\.eval()\|\.train()\|freeze\|lora\|peft" --include=*.py
grep -rn "normali[sz]\|mean\|std\|stats" --include=*.py
grep -rn "autocast\|bfloat16\|float16\|\.half()\|GradScaler" --include=*.py
grep -rn "interpolate\|resize\|Resize\|antialias" --include=*.py
grep -rn "permute\|transpose\|reshape\|view(\|einops" --include=*.py
```

The last one is worth reading in full. **A shape bug is almost always inside a `reshape` or a `permute`** that looked obvious when it was written.

## What static reading gives you, and what it does not

| Reliable from source | Needs the runtime |
|---|---|
| Module composition, call order | Which branch a config actually takes |
| Literal shapes and constants in the file | Shapes that depend on data |
| `requires_grad` / `.eval()` call sites | Whether they are still in effect at step time |
| Which file stats are read from | What is in that file |

Mark the second column `inferred` until a probe confirms it. Being wrong is fine; being wrong while marked `verified` is not.

## Conditionals

A branch on config (`if cfg.use_lora:`) means the map is a map **of one configuration**. Resolve it against the config the entry point actually loads, and put that config's path in the header next to the commit. Do not draw both branches — a map with every branch on it is the hairball again.
