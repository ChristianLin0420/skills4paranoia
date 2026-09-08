# Equations

## Compile them

LaTeX → MathML at build time, once, with [`temml`](https://temml.org). The output is plain MathML:
no runtime JavaScript, no CDN, no webfont, no stylesheet dependency. It renders in every current
browser, it is selectable, searchable and it reflows.

```bash
npm install temml
```

```js
const temml = require("temml");
const html = temml.renderToString(tex, { displayMode: true });
```

Feed it **the LaTeX from the paper's own source**, macros expanded. Papers define shorthand
(`\newcommand{\acronym}{\textsc{RoboTTT}}`, `\newcommand{\gdn}{GDN}`); expand them yourself before
rendering, because `temml` will render an undefined macro as an error string in the middle of your
equation and it will look like part of the maths.

**Why temml over KaTeX**: KaTeX's MathML output leans on `mathvariant` for calligraphic letters;
temml emits the actual Unicode codepoint (`ℒ` for `\mathcal{L}`), so it survives a browser with no
maths font installed. Either works; the difference shows up on script and blackboard-bold letters.

An image of an equation fails this skill. It cannot be linked to a symbol table, cannot be searched,
does not reflow, and goes blurry on a retina display.

## Number them as the paper numbers them

Eq. 1 in your report is Eq. 1 in the paper. If the paper leaves an equation unnumbered, give it a
label of your own and mark it as yours (`Eq. A′`, "unnumbered in the source"). A reader with both
documents open must never have to work out the mapping.

## The symbol table

Every equation carries one. Every symbol in the equation appears in it. No exceptions, including the
ones that feel obvious — `t` is obvious until a paper uses it for both the timestep and the
flow-matching time, which is exactly the paper you are reading.

| Column | Contents |
|---|---|
| Symbol | Rendered the same way as in the equation |
| Name | Words, not a restatement of the symbol |
| Shape | `(d,)`, `(b, t, n, d)`, scalar, or "a set of parameter tensors" |
| Provenance | `input` / `learned` / `fast` / `hyper` / `derived` / `index` |
| Note | Its value if it is a hyperparameter; the section that defines it; a gotcha |

Provenance is the column that does the work. A reader who knows that `W` is `fast` and `θ_Q` is
`learned` has understood the paper's central idea without reading another word.

**Write the shape even when the paper does not.** If you had to work it out, that row is `inferred`,
and mark it — the shape you derived is a claim.

## Writing the gloss

Under each equation, three sentences, in this order:

1. **What it does**, mechanically. "One gradient step on the fast weights, using this timestep's key as the input and its value as the target."
2. **Why it is that and not something simpler.** This is the sentence readers actually want, and the one summaries skip.
3. **What would change if a specific symbol were different.** Attach it to a symbol; this is what makes the table load-bearing.

Do not paraphrase the equation left to right in words. `W_t ← W_{t-1} − η∇…` glossed as "W at t is W
at t minus one minus eta times the gradient" has added nothing; the reader could already read it.

## Cross-linking

In the HTML, symbol and table row highlight each other. Implementation: after render, walk the
MathML for `<mi>` nodes whose text matches a symbol key; if the node is the base of an
`msub`/`msup`/`msubsup`, tag the parent instead so `W_t` lights as a unit rather than a bare `W`.

```js
el.querySelectorAll("mi").forEach(mi => {
  const key = mi.textContent.trim();
  if (!SYMBOLS[key]) return;
  const p = mi.parentElement;
  const target = (/^(msub|msup|msubsup)$/.test(p.tagName.toLowerCase()) && p.firstElementChild === mi) ? p : mi;
  target.classList.add("sym"); target.dataset.sym = key;
});
```

Match on the base letter, not the full subscripted form — a paper writes `W`, `W_t`, `W_{t-1}` and
`W_0` for one object, and they should all light together.

## Conventions worth normalising, and worth flagging

Papers differ on whether `‖·‖²` means a sum or a mean, whether a loss is per-sample or per-batch,
and whether an update is written with `←` or `=`. Where the difference is absorbed by a learnable
scale it is a footnote, not a divergence — say so once and move on. Where it is not absorbed, it is
a finding.
