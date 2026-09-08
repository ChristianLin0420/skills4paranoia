# Figures

## Vector or raster, decided by the file

Figure PDFs from a paper are of two kinds and they want different treatment. Ask the PDF, do not
guess from the filename.

```python
import pymupdf
page = pymupdf.open(path)[0]
raster = bool(page.get_images(full = True))    # any embedded bitmap at all
```

| Kind | Test | Emit | Why |
|---|---|---|---|
| Plot, chart, line diagram | no embedded images | **SVG** | Crisp at any zoom, text stays text, usually 10–40 KB |
| Photo strip, rendered figure, screenshot | embedded images | **WebP** | SVG would wrap the bitmap and add 5× the bytes |

One guard: a vector figure with gradient meshes can produce an enormous SVG. Set a budget and fall
through to raster when it blows it.

```python
svg = page.get_svg_image(text_as_path = False)
if not raster and len(svg.encode()) < 200 * 1024:
    ...                                        # ship the SVG
```

A 171×97 pt TBPTT diagram producing a 345 KB SVG and a 45 KB WebP is not a hypothetical; it is what
happens when the drawing tool emits shading meshes.

## Size on the long edge, not by a zoom factor

Figure PDFs vary from 171 pt to 5960 pt wide in the same paper. A fixed zoom gives you a 12000 px
photo strip and a 400 px diagram. Target the output width instead:

```python
zoom = min(9.0, max(0.25, 1500 / page.rect.width))
pix  = page.get_pixmap(matrix = pymupdf.Matrix(zoom, zoom), alpha = False)
```

1500 px on the long edge, WebP quality 86, is the point where a 2.1 MB asset set becomes 1.3 MB with
no visible loss at full-page width on a retina display. Check the total; a whole paper's figures
should land near 1–2 MB.

## Where the files go

`index.<lang>.html` plus a sibling `assets/`. Both language versions share one `assets/`.

Inlining as data-URIs makes one portable file, and it also makes a file a third larger per language
that no editor will open and that git stores twice. The folder is the right default.

Inline when the report has to travel somewhere that will not carry the folder — a chat, an email, a
viewer pane, a colleague who will download one thing:

```bash
node build.js spec.json teardown.html diagrams.js out.html --inline ./assets
```

Build both when both are wanted: the folder version is what goes in the repo, the inlined one is what
you hand over. They come from the same spec, so they cannot disagree.

## Attribution

Under every embedded figure, in the caption line: figure number as the paper numbers it, the paper's
short title, and the licence. Once, in the sources section: full citation, URL, licence, and the
date fetched.

If the licence does not permit redistribution, do not embed. Link the figure by number to the
paper's page and write a longer reading — a reading of a figure the reader has open in another tab
is worth more than a thumbnail.

## The reading

**Every figure carries one, and it is not the caption.** The paper's caption says what the figure
is. Your reading says what to do with it.

1. **What to look at.** Name the specific comparison — the two lines, the gap, the one bar out of line. "Compare the blue line's position against the grey one, not its slope."
2. **What it establishes**, and in what units — trials, percent, a rubric score. A rubric score is not a success rate and the difference matters.
3. **What would change your mind.** The condition under which the figure would stop supporting the claim: a missing baseline, an axis that does not start at zero, an n of 10.

Keep the reading and the caption visually distinct. A reader must be able to tell what the authors
said from what you concluded — that is the same tier discipline as everywhere else in this skill.

## Drawing your own

Draw where the paper has no figure and the idea has motion or structure that prose handles badly:
a recurrence, a masking pattern, what is detached from what, a before/after of one design choice.

Three rules:

- **Original diagrams are `inferred` unless the paper states the structure.** They are your reading rendered as a picture, and a picture asserts more confidently than a sentence.
- **Interactive only where interaction is the point.** A slider that changes a segment boundary and redraws which gradients survive teaches something. A slider that changes a colour does not.
- **Same tokens as everything else.** `html-design-system` owns the palette; a diagram in its own colours reads as if it came from somewhere else, which — being yours and not the paper's — is exactly the wrong signal.
