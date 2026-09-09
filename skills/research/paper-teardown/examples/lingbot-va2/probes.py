#!/usr/bin/env python3
"""Audit Robbyant/lingbot-va against the four design principles of arXiv:2607.08639.

    python probes.py /path/to/lingbot-va

This is a STATIC audit of what the repository contains. It executes no model and
makes no claim about model behaviour -- the released checkpoints are Wan-scale and
the paper's own model was never public. What it does establish, reproducibly, is
which of LingBot-VA 2.0's four stated contributions are present in the code.

Each check names what it looked for and what finding it would support either way.
"""
import os, re, sys

ROOT = sys.argv[1] if len(sys.argv) > 1 else "."
SRC = []
for base, dirs, files in os.walk(ROOT):
    dirs[:] = [d for d in dirs if d != ".git"]
    for f in files:
        if f.endswith((".py", ".md", ".toml")):
            p = os.path.join(base, f)
            SRC.append((os.path.relpath(p, ROOT), open(p, errors="ignore").read()))

def find(pattern, label, expect):
    rx = re.compile(pattern, re.I)
    hits = [(p, i + 1, ln.strip()[:72])
            for p, t in SRC for i, ln in enumerate(t.splitlines()) if rx.search(ln)]
    verdict = "PRESENT" if hits else "ABSENT"
    # expect = what this line would look like if the repo held VA 2.0
    mark = "as-VA2  " if verdict == expect else "NOT-VA2 "
    print(f"{mark} {label:44s} {verdict}")
    for p, i, ln in hits[:2]:
        print(f"          {p}:{i}  {ln}")
    return bool(hits)

print(f"repo: {ROOT}   files scanned: {len(SRC)}")
print(f"total python lines: {sum(t.count(chr(10)) for p, t in SRC if p.endswith('.py'))}\n")

print("-- the four design principles of LingBot-VA 2.0 --")
find(r"num_experts|mixture.of.expert|top_?k_?expert|\brouter\b|moe_|SwiGLU",
     "(3) sparse MoE backbone", "PRESENT")
find(r"siglip|dinov2|perception.?encoder|semantic.?align|L_align",
     "(1a) semantic alignment to a teacher", "PRESENT")
find(r"latent.?action|inverse.?dynamics|\bIDM\b|forward.?dynamics|\bFDM\b",
     "(1b) latent action tokenizer", "PRESENT")
find(r"multi.?chunk|\bMCP\b|next.?forcing",
     "(MCP) multi-chunk prediction", "PRESENT")
find(r"foresight|re.?ground|regrounding",
     "(4) Foresight Reasoning / re-grounding", "PRESENT")

print("\n-- what the released model is built on instead --")
find(r"AutoencoderKLWan|WanVAE", "reconstruction VAE from Wan2.2", "ABSENT")
find(r"from_pretrained|Wan2\.2|Wan-AI", "initialised from a pretrained video model", "ABSENT")
find(r"class WanTransformer3DModel", "Wan video transformer as the backbone", "ABSENT")
find(r"from diffusers\.models\.attention import FeedForward", "dense FeedForward, not a routed layer", "ABSENT")

print("\n-- which paper the repository is for --")
ids = sorted({m for p, t in SRC for m in re.findall(r"arxiv[.:/ ]*(?:abs/)?(\d{4}\.\d{4,5})", t, re.I)})
print(f"        arXiv ids referenced anywhere: {ids or 'none'}")
print(f"        2607.08639 (this paper) referenced: {'2607.08639' in ids}")
print(f"        2601.21998 (LingBot-VA 1.0)  referenced: {'2601.21998' in ids}")
pdfs = sorted(f for f in os.listdir(ROOT) if f.lower().endswith(".pdf"))
print(f"        PDFs committed at the repo root: {pdfs}")
