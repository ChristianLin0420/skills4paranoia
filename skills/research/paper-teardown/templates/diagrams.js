/* ============================================================================
   Four diagram kinds, reusable across sequence-model papers. Each reads its
   spec from TEARDOWN.diagrams[i], renders into .stage[data-dia], wires
   .ctrl[data-ctrl] and narrates into .say[data-say].
   All copy comes from the spec, so a translated report needs no code change.
   ========================================================================== */
const SVGNS = "http://www.w3.org/2000/svg";
const A = "var(--accent)", AD = "var(--accent-deep)", ASOFT = "var(--accent-soft)",
      AWASH = "var(--wash)", INK = "var(--ink)", INK2 = "var(--body)",
      INK3 = "var(--muted)", RULE = "var(--rule)", SURF = "var(--frame)",
      WARN = "var(--warn)", WSOFT = "var(--warn-soft)", NAME = "var(--name)";

const svg = (w, h) => { const s = document.createElementNS(SVGNS, "svg");
  s.setAttribute("viewBox", "0 0 " + w + " " + h); s.setAttribute("width", w);
  s.setAttribute("height", h); return s; };
function node(tag, attrs, txt) {
  const n = document.createElementNS(SVGNS, tag);
  for (const k in attrs) n.setAttribute(k, attrs[k]);
  if (txt != null) n.textContent = txt;
  return n;
}
function box(g, x, y, w, h, label, o) {
  o = o || {};
  g.appendChild(node("rect", {x, y, width:w, height:h, rx:o.rx || 3,
    fill:o.fill || SURF, stroke:o.stroke || RULE, "stroke-width":o.sw || 1,
    "stroke-dasharray":o.dash || "none", opacity:o.op == null ? 1 : o.op}));
  if (label != null) g.appendChild(node("text", {x:x + w/2, y:y + h/2 + 4,
    "text-anchor":"middle", fill:o.ink || INK, "font-family":"var(--mono)",
    "font-size":o.fs || 12, "font-weight":o.fw || 400, opacity:o.op == null ? 1 : o.op}, label));
}
function arrow(g, x1, y1, x2, y2, o) {
  o = o || {};
  g.appendChild(node("path", {d:o.d || ("M" + x1 + " " + y1 + "L" + x2 + " " + y2),
    fill:"none", stroke:o.stroke || INK3, "stroke-width":o.sw || 1.3,
    "stroke-dasharray":o.dash || "none", opacity:o.op == null ? 1 : o.op,
    "marker-end":"url(#" + (o.head || "ah") + ")"}));
}
function label(g, x, y, t, o) {
  o = o || {};
  g.appendChild(node("text", {x, y, "text-anchor":o.anchor || "middle",
    fill:o.ink || INK3, "font-family":o.mono === false ? "var(--sans)" : "var(--mono)",
    "font-size":o.fs || 10.5, "font-weight":o.fw || 400,
    opacity:o.op == null ? 1 : o.op}, t));
}
function defs(s) {
  const d = node("defs");
  [["ah", INK3], ["ahA", A], ["ahW", WARN], ["ahL", "#C6CCD1"]].forEach(([id, col]) => {
    const m = node("marker", {id, viewBox:"0 0 8 8", refX:7, refY:4, markerWidth:5.5,
      markerHeight:5.5, orient:"auto-start-reverse"});
    m.appendChild(node("path", {d:"M0 0.6 L8 4 L0 7.4 Z", fill:col}));
    d.appendChild(m);
  });
  s.appendChild(d);
}
/* Measure the widest label so the left gutter fits it. A constant here clips the
   moment the report is translated -- CJK labels are wider than their English source. */
function gutter(s, texts, fs) {
  const probe = node("g", {opacity:0}); s.appendChild(probe);
  let w = 0;
  texts.filter(Boolean).forEach(t => {
    const n = node("text", {x:0, y:0, "font-family":"var(--mono)", "font-size":fs || 10.5}, t);
    probe.appendChild(n); w = Math.max(w, n.getBBox().width);
  });
  probe.remove();
  return Math.ceil(w);
}
const stage = id => document.querySelector('.stage[data-dia="' + id + '"]');
const ctrl  = id => document.querySelector('.ctrl[data-ctrl="' + id + '"]');
const say   = id => document.querySelector('.say[data-say="' + id + '"]');
function buttons(id, groupLabel, items, initial, onPick) {
  const c = ctrl(id);
  if (groupLabel) c.appendChild(el("span", "cl", esc(groupLabel)));
  const bs = items.map((it, i) => {
    const b = el("button", i === initial ? "on" : "", esc(it.label));
    b.addEventListener("click", () => {
      bs.forEach(x => x.classList.remove("on")); b.classList.add("on"); onPick(i, it);
    });
    c.appendChild(b); return b;
  });
  return bs;
}

const DIA = {};

/* ---------------------------------------------------------------- 1. recurrence
   A state carried along a timeline: update from (K,V), then apply to Q.
   spec: {steps, stepText:[per-step narration], labels:{k,v,q,o,state,init}}      */
DIA.recurrence = function (d) {
  const T = d.steps || 5, W = 840, H = 208;
  const s = svg(W, H); defs(s);
  stage(d.id).appendChild(s);
  const lw = gutter(s, [d.labels.kv, d.labels.state, d.labels.o]);
  const initW = Math.max(52, gutter(s, [d.labels.init], 12.5) + 16);
  const x0 = lw + 16 + initW + 14, colw = (W - x0 - 12) / T;
  const g = node("g"); s.appendChild(g);

  label(g, 8, 34, d.labels.kv, {anchor:"start", ink:INK2});
  label(g, 8, 116, d.labels.state, {anchor:"start", ink:AD, fw:500});
  label(g, 8, 190, d.labels.o, {anchor:"start", ink:INK2});

  box(g, lw + 16, 92, initW, 34, d.labels.init, {fill:AWASH, stroke:ASOFT, ink:AD, fs:12.5});

  const parts = [];
  const bw = Math.min(88, colw - 22);
  for (let i = 0; i < T; i++) {
    const x = x0 + i * colw, gi = node("g"); g.appendChild(gi);
    box(gi, x, 16, bw, 30, d.labels.k + (i + 1) + "  " + d.labels.v + (i + 1), {fs:11});
    arrow(gi, x + bw / 2, 48, x + bw / 2, 88);
    label(gi, x + bw / 2 + 8, 70, d.labels.update, {anchor:"start", fs:9.5});
    box(gi, x, 92, bw, 34, d.labels.w + (i + 1), {fs:12.5, fw:500});
    if (i < T - 1) arrow(gi, x + bw, 109, x + colw - 2, 109);
    box(gi, x, 140, 40, 26, d.labels.q + (i + 1), {fs:11});
    arrow(gi, x + 20, 138, x + 30, 128);
    arrow(gi, x + bw / 2 + 8, 128, x + bw - 22, 170, {stroke:A, head:"ahA"});
    box(gi, x + bw - 40, 172, 40, 26, d.labels.o + (i + 1), {fs:11, stroke:A, fill:AWASH, ink:AD});
    parts.push(gi);
  }
  arrow(g, lw + 16 + initW, 109, x0 - 2, 109);

  let at = -1, timer = null;
  const paint = () => {
    parts.forEach((p, i) => p.setAttribute("opacity", at < 0 || i <= at ? 1 : 0.16));
    say(d.id).innerHTML = at < 0 ? d.stepText[0] : d.stepText[Math.min(at + 1, d.stepText.length - 1)];
  };
  const c = ctrl(d.id);
  c.appendChild(el("span", "cl", esc(d.labels.ctrl)));
  const mk = (t, fn) => { const b = el("button", "", esc(t)); b.addEventListener("click", fn); c.appendChild(b); return b; };
  mk(d.labels.back, () => { clearInterval(timer); at = Math.max(-1, at - 1); paint(); });
  mk(d.labels.fwd,  () => { clearInterval(timer); at = Math.min(T - 1, at + 1); paint(); });
  const play = mk(d.labels.play, () => {
    clearInterval(timer); at = -1; paint(); play.classList.add("on");
    timer = setInterval(() => { at++; paint();
      if (at >= T - 1) { clearInterval(timer); play.classList.remove("on"); } }, 850);
  });
  mk(d.labels.all, () => { clearInterval(timer); play.classList.remove("on"); at = T - 1; paint(); });
  at = T - 1; paint();
};

/* ------------------------------------------------------------- 2. truncation
   Gradients stop at segment boundaries; the carried state does not.
   spec: {steps, options:[{label, seg}], text(seg, reach)}                        */
DIA.truncation = function (d) {
  const T = d.steps || 12, W = 840, H = 172;
  const s = svg(W, H); defs(s);
  stage(d.id).appendChild(s);
  const pad = gutter(s, [d.labels.state, d.labels.grad]) + 18;
  const cw = (W - pad - 20) / T;
  const g = node("g"); s.appendChild(g);
  const draw = seg => {
    g.innerHTML = "";
    const reach = seg ? Math.min(seg, T) : T;
    label(g, 6, 56, d.labels.state, {anchor:"start", ink:AD, fw:500});
    label(g, 6, 120, d.labels.grad, {anchor:"start", ink:INK2});
    for (let i = 0; i < T; i++) {
      const x = pad + i * cw;
      box(g, x + 2, 40, cw - 6, 26, String(i + 1),
          {fs:10.5, fill:AWASH, stroke:ASOFT, ink:AD});
      if (i < T - 1) arrow(g, x + cw - 4, 53, x + cw + 2, 53, {stroke:A, head:"ahA", sw:1.1});
      const live = i >= T - reach;
      box(g, x + 2, 104, cw - 6, 22, "",
          {fill:live ? WSOFT : "transparent", stroke:live ? WARN : RULE,
           dash:live ? "none" : "3 3", sw:live ? 1.2 : 1});
      if (live && i < T - 1)
        arrow(g, x + cw + 2, 115, x + cw - 4, 115, {stroke:WARN, head:"ahW", sw:1.1});
    }
    if (seg) for (let b = seg; b < T; b += seg) {
      const x = pad + b * cw;
      g.appendChild(node("line", {x1:x, y1:26, x2:x, y2:140, stroke:INK3,
        "stroke-width":1, "stroke-dasharray":"4 4"}));
      label(g, x, 20, d.labels.cut, {ink:INK3, fs:9.5});
    }
    label(g, pad, 152, d.labels.axis, {anchor:"start", ink:INK3, fs:10});
    say(d.id).innerHTML = d.text.replace("{seg}", seg || T).replace("{reach}", reach).replace("{T}", T);
  };
  buttons(d.id, d.labels.ctrl, d.options, d.initial || 0, (i, it) => draw(it.seg));
  draw(d.options[d.initial || 0].seg);
};

/* -------------------------------------------------------------- 3. maskstrip
   Which timesteps update the state, and which contribute to the loss.
   spec: {schemes:[{label, roles:[..], loss:[bool], say}], roleColors, labels}     */
DIA.maskstrip = function (d) {
  const W = 840, H = 152;
  const s = svg(W, H); defs(s);
  stage(d.id).appendChild(s);
  const pad = gutter(s, [d.labels.step, d.labels.updates, d.labels.loss]) + 18;
  const g = node("g"); s.appendChild(g);
  const draw = sc => {
    g.innerHTML = "";
    const T = sc.roles.length, cw = (W - pad - 20) / T;
    label(g, 6, 34, d.labels.step, {anchor:"start", ink:INK2});
    label(g, 6, 80, d.labels.updates, {anchor:"start", ink:AD, fw:500});
    label(g, 6, 124, d.labels.loss, {anchor:"start", ink:INK2});
    for (let i = 0; i < T; i++) {
      const x = pad + i * cw, r = sc.roles[i], col = d.roleColors[r];
      box(g, x + 1.5, 18, cw - 4, 24, d.roleShort[r],
          {fs:10, fill:col.fill, stroke:col.stroke, ink:col.ink});
      box(g, x + 1.5, 64, cw - 4, 22, "", {fill:ASOFT, stroke:A, sw:1.1});
      const on = sc.loss[i];
      box(g, x + 1.5, 108, cw - 4, 22, on ? "" : d.labels.skip,
          {fs:9, fill:on ? WSOFT : "transparent", stroke:on ? WARN : RULE,
           dash:on ? "none" : "3 3", ink:INK3});
    }
    for (let i = 0; i < T - 1; i++)
      arrow(g, pad + (i + 1) * cw - 2.5, 75, pad + (i + 1) * cw + 1.5, 75, {stroke:A, head:"ahA", sw:1.1});
    say(d.id).innerHTML = sc.say;
  };
  buttons(d.id, d.labels.ctrl, d.schemes, d.initial || 0, (i, sc) => draw(sc));
  draw(d.schemes[d.initial || 0]);
};

/* ------------------------------------------------------------------ 4. axes2
   Two operators on two axes of the same grid: one within a column, one along a row.
   spec: {steps, tokens:[{key,label,through}], modes:[{label,axis,say}]}           */
DIA.axes2 = function (d) {
  const T = d.steps || 6, W = 840, y0 = 34;
  const rows = d.tokens.length, rh = 34, H = y0 + rows * rh + 40;
  const s = svg(W, H); defs(s);
  stage(d.id).appendChild(s);
  const x0 = gutter(s, d.tokens.map(t => t.label), 11) + 20;
  const cw = (W - x0 - 26) / T;
  const back = node("g"), front = node("g"); s.appendChild(back); s.appendChild(front);

  d.tokens.forEach((t, r) => label(back, x0 - 12, y0 + r * rh + rh / 2 + 4, t.label,
    {anchor:"end", ink:t.through === false ? INK3 : INK2, fs:11}));
  for (let i = 0; i < T; i++) label(back, x0 + i * cw + cw / 2, y0 - 10, d.labels.t + (i + 1), {fs:10});
  const cells = [];
  for (let r = 0; r < rows; r++) for (let i = 0; i < T; i++) {
    const x = x0 + i * cw + 2, y = y0 + r * rh + 3;
    const rect = node("rect", {x, y, width:cw - 5, height:rh - 7, rx:3,
      fill:SURF, stroke:RULE, "stroke-width":1});
    back.appendChild(rect); cells.push({rect, r, i, t:d.tokens[r]});
  }
  const draw = mode => {
    front.innerHTML = "";
    cells.forEach(c => {
      const inCol = mode.axis === "col" && c.i === (mode.at == null ? 1 : mode.at);
      const inRow = mode.axis === "row" && c.t.through !== false;
      const on = inCol || inRow;
      c.rect.setAttribute("fill", on ? (mode.axis === "col" ? ASOFT : AWASH) : SURF);
      c.rect.setAttribute("stroke", on ? A : (c.t.through === false ? RULE : RULE));
      c.rect.setAttribute("stroke-width", on ? 1.5 : 1);
      c.rect.setAttribute("stroke-dasharray", c.t.through === false ? "3 3" : "none");
      c.rect.setAttribute("opacity", c.t.through === false && mode.axis === "row" ? 0.45 : 1);
    });
    if (mode.axis === "col") {
      const i = mode.at == null ? 1 : mode.at, x = x0 + i * cw + cw / 2;
      arrow(front, x, y0 + 2, x, y0 + rows * rh - 6, {stroke:A, head:"ahA", sw:1.6});
      label(front, x + 8, y0 + rows * rh + 16, mode.note, {anchor:"start", ink:AD, fs:10.5});
    } else {
      d.tokens.forEach((t, r) => { if (t.through === false) return;
        arrow(front, x0 + 4, y0 + r * rh + rh / 2 - 3, W - 22, y0 + r * rh + rh / 2 - 3,
              {stroke:A, head:"ahA", sw:1.6, op:.85}); });
      label(front, x0, y0 + rows * rh + 16, mode.note, {anchor:"start", ink:AD, fs:10.5});
    }
    say(d.id).innerHTML = mode.say;
  };
  buttons(d.id, d.labels.ctrl, d.modes, d.initial || 0, (i, m) => draw(m));
  draw(d.modes[d.initial || 0]);
};
