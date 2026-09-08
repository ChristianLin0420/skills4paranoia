#!/usr/bin/env python3
"""Check the claims the README makes about this collection, instead of asserting them.

    python3 tools/lint/check_routing.py

  1. Every skill declares Chinese triggers and carries the **Language.** directive.
  2. No two skills claim the same Chinese trigger PHRASE — a router cannot choose
     between two skills that claim the same sentence.
  3. Report shared multi-character TOPIC terms. Generic verb phrases (幫我把, 有沒有)
     are stopped: they are grammar, not routing signal. A shared topic term is not
     automatically a bug — deck-design-system and research-deck should both answer
     to 投影片 — but each one has to be a decision someone made on purpose.
  4. plugin.json lists exactly the skills on disk.
  5. Every HTML template and example names a CJK face in BOTH font stacks.
     A monospace stack without one renders Chinese as tofu.

Exits non-zero on 1, 2, 4 or 5. 3 is reported and never fails the run.
"""
import glob, itertools, json, os, re, sys

# generic Chinese phrasing: shared by many asks, distinguishes nothing
STOP = {"幫我看", "幫我把", "幫我做", "幫我", "有沒有", "為什麼", "我當初", "做一份",
        "是不是", "這樣想", "這個", "那個", "怎麼", "可以", "什麼", "一份", "沒有",
        "我的", "這些", "要不要", "該怎麼"}

def load():
    out = {}
    for p in sorted(glob.glob("skills/*/*/SKILL.md")):
        s = open(p).read()
        fm, body = s.split("---")[1], s.split("---", 2)[2]
        name = re.search(r"^name:\s*(\S+)", fm, re.M).group(1)
        flat = re.sub(r"\s+", " ", fm.split("description:")[1])   # descriptions wrap mid-phrase
        m = re.search(r"Chinese triggers:(.*)", flat)
        out[name] = dict(dir=os.path.dirname(p), raw=m.group(1).strip() if m else None,
                         lang="**Language.**" in body)
    return out

def phrases(raw):
    return [p.strip(" .").strip() for p in raw.split("/") if p.strip(" .").strip()]

def topic_terms(raw):
    t = set()
    for run in re.findall(r"[一-鿿]+", raw):
        for L in range(3, len(run) + 1):
            for i in range(len(run) - L + 1):
                t.add(run[i:i + L])
    return {x for x in t if x not in STOP and not any(s in x for s in STOP)}

def main():
    fail = []
    sk = load()
    print(f"skills: {len(sk)}")
    # An empty glob satisfies every check below vacuously. Run from the repo root.
    if len(sk) < 2:
        print(f"\nFAILED: found {len(sk)} skills under skills/*/*/SKILL.md — run this from the repo root")
        return 1

    for n, v in sk.items():
        if not v["raw"]: fail.append(f"{n}: no Chinese triggers")
        if not v["lang"]: fail.append(f"{n}: no **Language.** directive")
    print("  triggers + language directive:", "ok" if not fail else "FAIL")

    P = {n: set(phrases(v["raw"])) for n, v in sk.items() if v["raw"]}
    dupes = [(a, b, sorted(P[a] & P[b])) for a, b in itertools.combinations(sorted(P), 2) if P[a] & P[b]]
    print("  duplicate trigger phrases:", len(dupes))
    for a, b, s in dupes:
        fail.append(f"{a} and {b} both claim {s}")

    T = {n: topic_terms(v["raw"]) for n, v in sk.items() if v["raw"]}
    shared = [(a, b, sorted(T[a] & T[b], key=len, reverse=True))
              for a, b in itertools.combinations(sorted(T), 2) if T[a] & T[b]]
    print(f"  shared topic terms (reported, not enforced): {len(shared)}")
    for a, b, s in shared:
        print(f"      {a} <-> {b}: {s[:3]}")

    pj = set(json.load(open(".claude-plugin/plugin.json"))["skills"])
    disk = {"./" + v["dir"] for v in sk.values()}
    if pj != disk:
        fail.append(f"plugin.json vs disk differ: {sorted(pj ^ disk)}")
    print("  plugin.json vs disk:", "in sync" if pj == disk else "FAIL")

    tofu = []
    for h in glob.glob("skills/*/*/templates/*.html") + glob.glob("skills/*/*/examples/**/*.html", recursive=True):
        s = open(h).read()
        for var in ("--sans:", "--mono:"):
            m = re.search(re.escape(var) + r"([^;]+);", s)
            if m and "Noto Sans TC" not in m.group(1):
                tofu.append(f"{h} {var}")
    fail += [f"CJK face missing: {t}" for t in tofu]
    print("  CJK in both font stacks:", "ok" if not tofu else "FAIL")

    if fail:
        print("\nFAILED:")
        for f in fail: print("  -", f)
        return 1
    print("\nall enforced checks pass")
    return 0

if __name__ == "__main__":
    sys.exit(main())
