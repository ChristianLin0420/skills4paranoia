# Input

What the user said:

> 再把 LingBot-VA2 這篇也做一樣 skill 的產出

A model name, nothing else — no link, no code URL, no indication that a code
repository exists. Everything below is the skill's job to find.

## What it went and got

| | |
|---|---|
| Identify the paper | `LingBot-VA2` → **arXiv:2607.08639**, *Native Video-Action Pretraining for Generalizable Robot Control* |
| `arxiv.org/e-print/2607.08639` | 10 `.tex` files, 12 figure PDFs, `00README.json` naming `main.tex` |
| `arxiv.org/abs/2607.08639` | 29 authors, Robbyant / Ant Group, **CC BY 4.0** — figures may be embedded with attribution |
| `arxiv.org/pdf/2607.08639` | Used only to check figure and table numbers against the printed document |
| project page | `technology.robbyant.com/lingbot-va-v2`, named in the paper's own metadata block |
| GitHub | `Robbyant/lingbot-va` — the authors' own org, Apache-2.0, 1,863★, and **it implements version 1.0** |

## The finding that shaped the report

The repository looks exactly like the right one. Correct organisation, permissive
licence, healthy star count, recent commits, and this paper's PDF committed at the
root. Every signal a reader uses to conclude "this is the code for that paper" fires
correctly — and the conclusion is wrong.

`probes.py` audits it against the paper's four design principles. All five mechanisms
are absent; all four markers of the model being departed from are present; the only
arXiv id referenced anywhere in the repository is **2601.21998**, which is LingBot-VA
1.0. Useful as the baseline. Not a reproduction.

## Decisions it made without asking

- **No model was executed.** The paper's weights were never released, the released
  checkpoints are Wan-scale, and constructing the released architecture would have
  meant fighting the host's conda environment. The audit is static, this is stated in
  the report, and no behavioural claim is made anywhere in the code section.
- **Two new diagram kinds** were written for this paper — `routing` for the sparse MoE
  and `streams` for the asynchronous inference loop — because both generalise past it.
- **Two arithmetic slips reported**, each with the interval that rules it out, after
  checking that no values consistent with the printed table could produce them.

## Output

`index.en.html`, `index.zh.html`, `assets/` (11 figures, 869 KB), `probes.py`, `probes.out`.
