# Input

What the user said:

> 幫我讀 RoboTTT 這篇，https://arxiv.org/abs/2607.15275
> 公式要看得懂，有 code 的話也一起看

That is all the input this skill needs. Everything else — the LaTeX source, the figures, the
licence, the absence of an official code release, the existence of a third-party
reimplementation — is the skill's job to find, not the user's job to supply.

## What it went and got

| | |
|---|---|
| `arxiv.org/e-print/2607.15275` | 26 `.tex` files, 16 figure PDFs, `00README.json` naming `main.tex` as the entry point |
| `arxiv.org/abs/2607.15275` | Authors, affiliations from the `\author` block, and the licence — **CC BY 4.0**, so figures may be embedded with attribution |
| `arxiv.org/pdf/2607.15275` | Used only to check the figure and table numbers against the printed document |
| project page | Rollout videos. **No code release.** |
| GitHub search | `lucidrains/robo_ttt` (72★, MIT, 770 lines) and `Bala-la-la/lerobot-pi0-ttt` (13★). Neither owner is an author. |

## Decisions it made without asking

- **Survey the third-party code anyway**, labelled on every claim it supports. "No official release, here is what the community built and where it diverges" is the common case in this field, and refusing to look would have thrown away the report's strongest section.
- **Run it rather than read it.** No macOS wheels exist for the required torch on the host's default interpreter; a runtime was assembled on top of an existing environment rather than giving up and marking everything `stated`.
- **Draw four diagrams**, for the four things the prose states and does not show.

## Output

`index.en.html`, `index.zh.html`, `assets/` (11 figures, 724 KB), `probes.py` and `probes.out`.
