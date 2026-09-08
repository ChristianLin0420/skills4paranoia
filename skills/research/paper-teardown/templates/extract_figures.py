#!/usr/bin/env python3
"""Figure PDFs from a paper's source -> web assets, one per figure.

    python3 extract_figures.py <src-dir> <out-dir>

Vector figures (no embedded bitmap, SVG under budget) become SVG; everything
else becomes WebP sized to a fixed long edge. Writes out-dir/index.json listing
what it produced, so the build step can look figures up by name.

    pip install pymupdf pillow
"""
import glob, io, json, os, re, sys
import pymupdf
from PIL import Image

LONG_EDGE   = 1500          # target device px on the long edge
SVG_BUDGET  = 200 * 1024    # a vector figure above this is a shading mesh; rasterise it
WEBP_Q      = 86

def convert(path, out):
    page = pymupdf.open(path)[0]
    # strip the -fig / _2 suffixes LaTeX authors add, so names match \label-ish keys
    stem = os.path.splitext(os.path.basename(path))[0]
    name = re.sub(r"(?:[-_]fig)?(?:_\d+)?$", "", stem)      # foo-fig.pdf, foo_2.pdf -> foo
    raster = bool(page.get_images(full=True))

    if not raster:
        s = page.get_svg_image(text_as_path=False)
        if len(s.encode()) < SVG_BUDGET:
            open(os.path.join(out, name + ".svg"), "w").write(s)
            return dict(name=name, kind="svg", file=name + ".svg",
                        bytes=len(s.encode()), w=page.rect.width, h=page.rect.height)

    zoom = min(9.0, max(0.25, LONG_EDGE / page.rect.width))
    pm = page.get_pixmap(matrix=pymupdf.Matrix(zoom, zoom), alpha=False)
    im = Image.open(io.BytesIO(pm.tobytes("png")))
    buf = io.BytesIO(); im.save(buf, "WEBP", quality=WEBP_Q, method=6)
    open(os.path.join(out, name + ".webp"), "wb").write(buf.getvalue())
    return dict(name=name, kind="webp", file=name + ".webp",
                bytes=len(buf.getvalue()), w=im.width, h=im.height)

def main(src, out):
    os.makedirs(out, exist_ok=True)
    pdfs = sorted(glob.glob(os.path.join(src, "**", "*.pdf"), recursive=True))
    rows, total = [], 0
    for p in pdfs:
        try:
            r = convert(p, out)
        except Exception as e:                       # a broken figure must not kill the run
            print(f"  SKIP {os.path.basename(p)}: {e}", file=sys.stderr); continue
        rows.append(r); total += r["bytes"]
        print(f"{r['name']:34s} {r['kind']:4s} {r['bytes']/1024:8.0f}KB  {r['w']:.0f}x{r['h']:.0f}")
    print(f"{'TOTAL':34s}      {total/1024:8.0f}KB in {len(rows)} figures")
    if total > 3 * 1024 * 1024:
        print("  warning: over 3 MB — lower LONG_EDGE or WEBP_Q", file=sys.stderr)
    json.dump(rows, open(os.path.join(out, "index.json"), "w"), indent=1)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2])
