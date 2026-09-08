# Getting the paper

Four sources, in descending order of what they let you do. Take the first one you can get.

| Source | URL | Gives you |
|---|---|---|
| **LaTeX source** | `arxiv.org/e-print/<id>` | Original figure files, the real equation source, section files, the bibliography |
| HTML render | `arxiv.org/html/<id>v1` | Structure and text; figures as PNG; math as MathML |
| PDF | `arxiv.org/pdf/<id>` | Text and embedded images; equations only as glyphs |
| Publisher page | varies | Metadata, licence, sometimes nothing else |

The tarball is not a nicety. Equations retyped from a PDF are equations you have retyped — every
subscript is a chance to be wrong, and the errors are invisible once compiled. Take the source.

```bash
curl -sL -A "<your-email> paper-teardown" -o src.tar.gz "https://arxiv.org/e-print/<id>"
mkdir -p src && tar xzf src.tar.gz -C src
```

Send a real contact in the User-Agent. arXiv asks for it and rate-limits what does not have it.

## Read `00README.json` first

arXiv puts it in the tarball. It names the top-level `.tex` file and the compiler, which saves you
guessing which of 26 files is the entry point:

```bash
python3 -c "import json;print(json.load(open('src/00README.json'))['sources'][0])"
```

Then follow `\input` and `\include` from there. Do not assume `main.tex`, and do not assume the
section files are in reading order in the directory — read the order off the top-level file.

## The licence check is not optional

Before any figure or block quote goes into your output, establish the licence. It is at the bottom
of the arXiv abstract page.

| Licence | Figures | Quotes |
|---|---|---|
| CC BY, CC BY-SA, CC0 | **Embed**, with attribution and a link | Fine, attributed |
| CC BY-NC / -ND | Depends on your use; assume no | Short, attributed |
| arXiv perpetual non-exclusive (the default) | **Link, do not embed** | Short, attributed |
| Publisher copyright | **Link, do not embed** | Short, attributed |

The default arXiv licence grants arXiv the right to distribute. It grants **you** nothing. Most
papers you want to tear down are on it. When you cannot embed, the report still works: link each
figure by number to the paper's own page, and lean harder on the diagrams you draw yourself.

Record the licence in the header of the report and in the sources section. A reader who wants to
reuse your explainer needs to know which parts they inherited a restriction on.

## Metadata worth capturing

Authors **with affiliations** (the abstract page often drops them; the `\author` block in the source
has them), submission date, version, the project page, and any code URL. The version matters: `v1`
and `v3` can differ in the numbers you are about to explain.

## When there is only a PDF

Structure comes from text extraction, figures from `PyMuPDF`, equations from your own retyping.
Retyped equations are **`inferred`**, not `stated` — you are asserting that the glyphs you read map
to the LaTeX you wrote. Mark them so, and say in the report that the source was unavailable.

```python
import pymupdf
doc = pymupdf.open("paper.pdf")
text = "\n".join(p.get_text() for p in doc)          # structure and prose
```

Never OCR a rendered equation into LaTeX and present it as the paper's. Subscript errors from OCR
survive compilation and look authoritative.

## Finding the code

Check, in order: the abstract page, the project page, the paper's footnotes, `paperswithcode`, and
a GitHub search for the paper's short name and for its distinctive method terms.

Record for each candidate: owner, stars, last commit, licence, and **whether the owner is an author
of the paper**. That last field decides how everything downstream is labelled. See
`reference/code-survey.md`.
