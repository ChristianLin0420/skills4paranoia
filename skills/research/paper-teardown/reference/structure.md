# Section order

Front-loaded, for the same reason the decks are: a reader who stops after two minutes should leave
with the argument, not with the background.

## 1 · Header

Title, authors **with affiliations**, date, version, links (arXiv, project page, code), licence, and
the tier legend. The legend goes here, not at the bottom — it is how the rest of the page is read.

If the code is third-party, that belongs here too, in the same size type as everything else.

## 2 · The claim

**One sentence** naming the mechanism and what it buys. Then **three numbers**, no more, each with
its comparison baked in — "79% vs 42% for the single-step baseline", not "79%".

Three is a constraint, not a suggestion. A paper has one argument; the numbers that do not serve it
belong in Results.

## 3 · The problem

What was broken before, in two passes: the authors' framing, then yours. Keep them separate and
labelled. Where you think the framing is generous to the paper, this is the place to say so — once,
in a sentence, without turning the explainer into a review.

## 4 · The method

The body. One block per mechanism, in the order the paper builds them:

- the compiled equation, numbered as the paper numbers it
- the symbol table, every symbol, with provenance
- the gloss: what it does, why not something simpler, what one symbol changes
- the paper's figure for this mechanism, with a reading
- where it lives in the code, if code exists

**One mechanism per block.** When a block needs two equations that are genuinely one idea (an update
and its apply step), keep them together and say why they are one idea.

## 5 · Diagrams

Yours, where the paper has none. Marked `inferred`. Interactive where interaction is the idea.

Place them after the method rather than inside it: a reader working through the equations should not
have to decide whether the picture is the paper's or yours mid-derivation.

## 6 · Results

Every figure and table, each with a reading. Group by claim, not by figure number — a paper's figure
order follows its narrative, and the narrative is what you are re-telling.

State `n` next to every rate. "6 of 10 trials" and "60%" are the same number and not the same claim.

## 7 · The code

The survey. Authorship first, then the correspondence table sorted by verdict, then the divergences
in detail, then the probe output as it printed.

## 8 · What the paper does not tell you

Four kinds, kept apart:

| Kind | Example |
|---|---|
| **Unspecified** | A protocol detail you would need to reproduce it and cannot find |
| **Absent** | An ablation the argument wants and the paper does not run |
| **Does not reconcile** | Two numbers in the paper that do not agree |
| **The authors' own limitations** | Their limitations section, restated |

The last one is theirs and goes last, clearly labelled. Mixing it with yours takes credit for their
honesty.

**Show the interval.** When a stated figure does not follow from a table, do not just assert it —
compute the range the displayed precision allows and show that the claim falls outside it. "The
table shows 93.6 and 79.8, so the difference lies in (13.70, 13.90); the stated 14.0 is outside it
for every pair consistent with what is printed" is checkable. "The arithmetic is wrong" is not.

**Be precise about arithmetic.** Rounded numbers do not reproduce rounded ratios: 79 and 42 shown to
two figures give 88%, and the paper's "87%" is right if the unrounded values are 78.9 and 42.2. Check
whether any pair of unrounded inputs consistent with the display reproduces the claim before calling
it an inconsistency. Crying wolf here costs you the section.

## Reading order inside a block

Three rules, all of which were learned by getting them wrong first.

**The figure comes before the algebra, not after it.** A mechanism block that runs
heading → equation → symbol table → three paragraphs → figure puts the picture 60% of the
way down, so it arrives after everything it was meant to illustrate. Put it straight after
the one-line lede: title, what this is in a sentence, the picture, then the maths. Use
`place: "end"` only for a figure that is a conclusion rather than an orientation.

**The chart shows the shape, the table gives the values.** When a block has both, the chart
goes first. And a table is an *exhibit* — same frame, same caption treatment, same anchor as
a figure. A bare table followed by a floating caption followed by an unrelated figure reads
as though the caption belongs to the figure.

**Cross-references are links.** "Figure 2" and "圖 2" in the prose should jump to the exhibit.
Number every exhibit, derive its id from that number, and resolve references at load time —
skipping captions (self-linking), headings, and code. A reference to a figure you did not
reproduce should stay plain text rather than link somewhere wrong.

## Two text stacks, and CJK gets its own metrics

**A wall of text is a structure problem before it is a leading problem.** Raising line-height
alone bought 6%; splitting the gloss into labelled, ruled items bought the rest. Each gloss
point already opens with a bold lead-in — promote it to its own label so three paragraphs read
as three things.

**Latin and CJK do not want the same metrics.** The document carries `lang`, so set them once:

```css
body{font-size:16px;line-height:1.85}
html[lang^="zh"] body{line-height:2.05;letter-spacing:.028em}
```

CJK needs more leading and a little tracking than Latin to stop reading as a block. Guessing
per-element is how the two versions drift apart.

**Split the font stack by job.** `--sans` is furniture — headings, labels, nav, tags — where a
calligraphic CJK face reads as decoration. `--read` is text you sit with, where an open face
like LXGW WenKai TC is what "breathing room" actually means in Chinese. Check the face is
really rendering before believing it: CJK advance widths are all 1em, so measuring string
width proves nothing — rasterise the same glyphs in each family and compare, with a
deliberately bogus family name as the fallback control.

**Measure the change, do not eyeball it.** Visible characters per 1000px of document height
is a serviceable proxy for density; apply the old values with an injected stylesheet and
re-measure to get a controlled before and after in the same page.

## One measure, not three

**The content column is the reading measure. Set it once, on the column.**

Capping prose at `68ch` inside a wider column is the default instinct and it is wrong here:
paragraphs end at one x, figures and tables at another, captions at a third. The step is
visible on every single figure, and it is what a reader means by "the text doesn't line up
with the images".

Measure it rather than eyeballing it — collect the bounding boxes of a paragraph, a figure
frame, a caption, a table, an equation and a diagram, and assert they share a left and a
right edge:

```js
[...document.querySelectorAll("main p, main figure .frame, main figcaption, main table")]
  .map(n => Math.round(n.getBoundingClientRect().right))   // must be one value
```

## 9 · Sources

Every URL, commit SHA, arXiv version and licence, each with the date fetched. A teardown is a claim
about a moving target; the date is part of the claim.
