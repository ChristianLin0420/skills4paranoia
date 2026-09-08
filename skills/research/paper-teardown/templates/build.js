#!/usr/bin/env node
/* Assemble a teardown report.

     npm install temml
     node build.js <spec.json> <template.html> <diagrams.js> <out.html> [--inline <assets-dir>]

   --inline embeds every figure as a data URI, producing one portable file instead of
   an HTML plus a sibling assets/ directory. Use it when the reader needs to open the
   report somewhere that will not carry the folder -- a chat, an email, a viewer pane.
   The default stays the folder: base64 costs a third more bytes and git stores a copy
   per language.

   The spec is the TEARDOWN object with one difference: every equation carries
   `tex` instead of `mathml`, and every symbol carries `tex` instead of `sym`.
   This step compiles them once, so the shipped page needs no JS to show maths.

   Macros: put paper-level \newcommand shorthand in spec.macros; temml renders an
   undefined macro as an error string inside the equation, which looks like maths.
*/
const fs = require("fs");
const temml = require("temml");

const [, , specPath, tplPath, diaPath, outPath] = process.argv;
if (!outPath) { console.error("usage: build.js <spec.json> <template.html> <diagrams.js> <out.html> [--inline <assets-dir>]"); process.exit(1); }
const inlineAt = process.argv.indexOf("--inline");
const assetDir = inlineAt > 0 ? process.argv[inlineAt + 1] : null;

const spec = JSON.parse(fs.readFileSync(specPath, "utf8"));
const macros = spec.macros || {};
let count = 0, failed = [];

function render(tex, display) {
  count++;
  try {
    return temml.renderToString(tex, { displayMode: !!display, macros: { ...macros } });
  } catch (e) {
    failed.push(tex.slice(0, 60) + "  ->  " + e.message);
    return '<code>' + tex.replace(/[&<>]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;" }[c])) + '</code>';
  }
}

for (const m of spec.mechanisms || []) {
  for (const e of m.eqs || []) { e.mathml = render(e.tex, true); delete e.tex; }
  for (const s of m.symbols || []) { s.sym = render(s.tex, false); s.key = s.key || s.tex; delete s.tex; }
}
// inline maths anywhere a string contains $...$
const INLINE = /\$([^$]+)\$/g;
const walk = o => {
  if (typeof o === "string") return o.replace(INLINE, (_, t) => render(t, false));
  if (Array.isArray(o)) return o.map(walk);
  if (o && typeof o === "object") { for (const k in o) o[k] = walk(o[k]); return o; }
  return o;
};
for (const k of ["claim", "problem", "mechanisms", "diagrams", "results", "code", "gaps", "methodLede", "diagramsLede"])
  if (spec[k]) spec[k] = walk(spec[k]);

if (failed.length) {
  console.error("LaTeX that did not compile — fix these, they ship as raw source:");
  failed.forEach(f => console.error("  " + f));
  process.exitCode = 1;
}

// --inline: figures become data URIs so the report travels as one file
let inlined = 0;
if (assetDir) {
  const MIME = {".svg":"image/svg+xml", ".webp":"image/webp", ".png":"image/png", ".jpg":"image/jpeg"};
  const seen = new Map();
  const embed = f => {
    if (!f || !f.file || f.link) return;
    if (!seen.has(f.file)) {
      const ext = f.file.slice(f.file.lastIndexOf("."));
      const path = require("path").join(assetDir, f.file);
      if (!fs.existsSync(path)) { console.error("missing asset: " + path); process.exitCode = 1; return; }
      seen.set(f.file, "data:" + (MIME[ext] || "application/octet-stream") +
                       ";base64," + fs.readFileSync(path).toString("base64"));
      inlined++;
    }
    f.dataUri = seen.get(f.file);
  };
  (spec.mechanisms || []).forEach(m => embed(m.fig));
  (spec.results || []).forEach(r => embed(r.fig));
}

const tpl = fs.readFileSync(tplPath, "utf8");
const dia = fs.readFileSync(diaPath, "utf8");
let html = tpl;
for (const [needle, value] of [["__DATA__", JSON.stringify(spec, null, 1)],
                               ["__DIAGRAMS__", dia],
                               ["__TITLE__", spec.meta.title],
                               ["__LANG__", spec.meta.lang || "en"]]) {
  if (!html.includes(needle)) { console.error("template is missing " + needle); process.exit(1); }
  html = html.replace(needle, () => value);
}
fs.writeFileSync(outPath, html);
console.log(`${outPath}  ${(html.length / 1024).toFixed(0)} KB  ${count} formulas  ${(spec.mechanisms || []).length} mechanisms  ${(spec.diagrams || []).length} diagrams` +
            (assetDir ? `  ${inlined} figures inlined` : ""));
