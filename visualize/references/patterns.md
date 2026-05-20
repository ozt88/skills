# Visualization Pattern Catalog

A reference for effective HTML representations by content type.
**Not mandatory templates** — consult only when you need inspiration or a starting point.

Original source: <https://thariqs.github.io/html-effectiveness/>
Local copies: `references/examples/*.html` (20 examples + `_index.html`).
**For specific implementation details, read the actual file** — code is more precise than descriptions.

---

## Common design principles

Five patterns that recur across every effective visualization:

1. **Hierarchical information architecture**: Meta → TL;DR → body → appendix (actions/glossary). Scannable header depth.
2. **Color-coded semantic badges**: Compress state into small chips (Blocking/Nit/Safe, SEV-2, +/− …).
3. **Anchors + inline jump links**: Shorten long documents with TOCs and `file:line` references.
4. **Copy/export calls-to-action**: Put a "Copy markdown/diff/JSON/SVG" button on almost every editor surface.
5. **CSS-variable token palette**: A unified 5-color palette; dark mode switches through the same variables.

---

## Patterns by category

### Exploration & planning (PLAN.md, design docs)

- **Side-by-side comparison** ([code-approaches](https://thariqs.github.io/html-effectiveness/01-exploration-code-approaches.html)): 2–3 approaches stacked vertically + Pro/Con table + inline metric badges (`Bundle impact`).
- **Light/dark design compare** ([visual-designs](https://thariqs.github.io/html-effectiveness/02-exploration-visual-designs.html)): 4 directions × Light/Dark toggles, subtle animations.
- **Milestones → data flow → mockups → code** ([implementation-plan](https://thariqs.github.io/html-effectiveness/16-implementation-plan.html)): Progress badges, risk/mitigation 2-column table, threaded comments.

### Code review (REVIEW.md, PR notes)

- **Annotated PR** ([annotated-pr](https://thariqs.github.io/html-effectiveness/03-code-review-pr.html)): Overview → risk map → file list. Inline line annotations + Blocking/Nit/Safe badges.
- **PR writeup** ([pr-writeup](https://thariqs.github.io/html-effectiveness/17-pr-writeup.html)): TL;DR → Why → File-by-file → Test plan → Rollout. `file:line` references, ±line-count badges, Before/After tables.
- **Module map** ([module-map](https://thariqs.github.io/html-effectiveness/04-code-understanding.html)): Diagram → 5-step call-stack walkthrough. `<details>` toggles fold source.

### Design system

- **Living design system** ([design-system](https://thariqs.github.io/html-effectiveness/05-design-system.html)): Color/type/spacing/shadow/component hierarchy + live buttons, inputs, badges.
- **Component variants sheet** ([component-variants](https://thariqs.github.io/html-effectiveness/06-component-variants.html)): 6-variant grid + padding/border/shadow sliders for live tuning + hover-reveal Props code.

### Prototyping

- **Micro-interaction sandbox** ([animation](https://thariqs.github.io/html-effectiveness/07-prototype-animation.html)): Click checkbox → fill → draw check → strike-through → shrink. Spring easing.
- **Drag-and-drop flow** ([interaction](https://thariqs.github.io/html-effectiveness/08-prototype-interaction.html)): Reorder sidebar list, snap when crossing the midline. ~40 lines of vanilla JS.

### Diagrams

- **SVG sheet** ([svg-illustrations](https://thariqs.github.io/html-effectiveness/10-svg-illustrations.html)): Three 720×320 SVGs + individual Download buttons. 5-color palette, consistent corner radius.
- **Clickable flowchart** ([flowchart](https://thariqs.github.io/html-effectiveness/13-flowchart-diagram.html)): Click a node → panel with runtime/duration/failure modes. Rect = process, diamond = decision.

### Decks, research & reports

- **Arrow-key slide deck** ([deck](https://thariqs.github.io/html-effectiveness/09-slide-deck.html)): Left/right arrow nav, 1/6 counter, big-number metrics.
- **Feature explainer** ([feature-explainer](https://thariqs.github.io/html-effectiveness/14-research-feature-explainer.html)): TOC + 4-stage expand + 3-column code compare + FAQ.
- **Concept simulator** ([concept-explainer](https://thariqs.github.io/html-effectiveness/15-research-concept-explainer.html)): Linear learning flow + interactive simulator (hash-ring add/remove/reset) + comparison table + glossary.
- **Weekly status report** ([status](https://thariqs.github.io/html-effectiveness/11-status-report.html)): Big-number KPI header + Shipped table + daily heatmap.
- **Incident report** ([incident](https://thariqs.github.io/html-effectiveness/12-incident-report.html)): Meta chip row (SEV-2/state/owner) → TL;DR → timeline → root cause → impact → actions.

### Custom editors

- **Triage board** ([triage-board](https://thariqs.github.io/html-effectiveness/18-editor-triage-board.html)): Now/Next/Later/Cut kanban + DnD + tag filter + "Copy as markdown" export.
- **Feature flag editor** ([feature-flags](https://thariqs.github.io/html-effectiveness/19-editor-feature-flags.html)): Toggles + auto-updating dependency warnings + Copy diff / Copy full JSON + "Pending changes (n)" counter.
- **Prompt tuner** ([prompt-tuner](https://thariqs.github.io/html-effectiveness/20-editor-prompt-tuner.html)): Left edit / right live preview + `{{slot}}` syntax + token count + Copy prompt.

---

## Reusable snippets

### Color & type tokens (dark mode aware)

```css
:root {
  --bg: #ffffff; --fg: #1a1a1a; --muted: #6b7280;
  --line: #e5e7eb; --card: #f9fafb; --code: #f3f4f6;
  --accent: #2563eb; --done: #16a34a;
  --warn: #f59e0b; --danger: #dc2626;
  --radius: 8px;
  --shadow: 0 1px 2px rgba(0,0,0,.04), 0 1px 3px rgba(0,0,0,.06);
  --ease-spring: cubic-bezier(.34, 1.56, .64, 1);
}
@media (prefers-color-scheme: dark) {
  :root {
    --bg: #0f172a; --fg: #e5e7eb; --muted: #94a3b8;
    --line: #1e293b; --card: #1e293b; --code: #0b1220;
    --accent: #60a5fa; --done: #4ade80;
    --warn: #fbbf24; --danger: #f87171;
  }
}
body {
  font-family: -apple-system, "Segoe UI", "Pretendard", "Apple SD Gothic Neo", sans-serif;
  background: var(--bg); color: var(--fg);
  line-height: 1.55;
}
```

### Semantic badge system

```html
<span class="badge badge--blocking">Blocking</span>
<span class="badge badge--nit">Nit</span>
<span class="badge badge--safe">Safe</span>
<style>
.badge { font: 600 11px/1 ui-monospace, monospace; padding: 3px 7px;
         border-radius: 4px; letter-spacing: .02em; }
.badge--blocking { background: #fde2e2; color: #a01b1b; }
.badge--nit      { background: #fff1c2; color: #7a5a00; }
.badge--safe     { background: #dff3df; color: #1f6b2a; }
@media (prefers-color-scheme: dark) {
  .badge--blocking { background: #4a1717; color: #fda4a4; }
  .badge--nit      { background: #463a0e; color: #fde68a; }
  .badge--safe     { background: #14361b; color: #86efac; }
}
</style>
```

### KPI header (status reports, postmortems)

```html
<header class="kpi-row">
  <div><b>14</b><span>PRs merged</span></div>
  <div><b>3</b><span>incidents</span></div>
  <div><b>92%</b><span>green builds</span></div>
</header>
<style>
.kpi-row { display: flex; gap: 32px; border-bottom: 1px solid var(--line); padding: 16px 0; flex-wrap: wrap; }
.kpi-row b { font: 600 32px/1 system-ui; display: block; }
.kpi-row span { font-size: 12px; color: var(--muted); text-transform: uppercase; letter-spacing: .05em; }
</style>
```

### "Show source" toggle (via `<details>`)

```html
<details class="source">
  <summary>show source · auth/session.ts</summary>
  <pre><code>export function createSession(...) { ... }</code></pre>
</details>
<style>
.source { background: var(--card); border-radius: var(--radius); margin: 8px 0; }
.source summary { cursor: pointer; font: 500 12px ui-monospace, monospace;
                  color: var(--muted); padding: 8px 12px; }
.source pre { margin: 0; padding: 0 12px 12px; }
</style>
```

### Arrow-key slide deck

```html
<div id="deck">
  <section>Slide 1</section>
  <section hidden>Slide 2</section>
  <section hidden>Slide 3</section>
</div>
<aside id="counter">1 / 3</aside>
<script>
const s = [...document.querySelectorAll('#deck section')]; let i = 0;
const show = n => {
  s.forEach((e, k) => e.hidden = k !== n);
  counter.textContent = `${n+1} / ${s.length}`;
};
addEventListener('keydown', e => {
  if (e.key === 'ArrowRight') show(i = Math.min(i+1, s.length-1));
  if (e.key === 'ArrowLeft')  show(i = Math.max(i-1, 0));
});
</script>
<style>
#deck section { padding: 40px; min-height: 60vh; }
#counter { position: fixed; top: 16px; right: 20px; color: var(--muted); font: 500 12px ui-monospace; }
</style>
```

### Sidebar + content layout (searchable)

```html
<div class="layout">
  <aside class="sidebar">
    <input type="search" placeholder="Search..." oninput="filter(this.value)">
    <nav id="toc"><!-- TOC --></nav>
  </aside>
  <main><!-- Body --></main>
</div>
<style>
.layout { display: grid; grid-template-columns: 240px 1fr; gap: 32px; }
.sidebar { position: sticky; top: 16px; align-self: start; }
@media (max-width: 800px) { .layout { grid-template-columns: 1fr; } }
</style>
```

### Card grid (color by state)

```html
<div class="grid">
  <article class="card done">
    <header><h3>Title</h3><span class="badge done">Done</span></header>
    <p>Body</p>
  </article>
</div>
<style>
.grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 12px; }
.card { background: var(--card); padding: 14px; border-radius: var(--radius);
        border-left: 3px solid var(--muted); }
.card.done   { border-left-color: var(--done); }
.card.warn   { border-left-color: var(--warn); }
.card.danger { border-left-color: var(--danger); }
</style>
```

### Sortable table

```html
<table id="t">
  <thead><tr><th onclick="sort(0)">Name</th><th onclick="sort(1)">Status</th></tr></thead>
  <tbody><!-- ... --></tbody>
</table>
<script>
function sort(col) {
  const tb = document.querySelector('#t tbody');
  const rows = [...tb.rows];
  const asc = tb.dataset.col === String(col) && tb.dataset.dir !== 'asc';
  rows.sort((a, b) => a.cells[col].textContent.localeCompare(b.cells[col].textContent) * (asc ? 1 : -1));
  tb.dataset.col = col; tb.dataset.dir = asc ? 'asc' : 'desc';
  rows.forEach(r => tb.appendChild(r));
}
</script>
```

### Copy button

```html
<pre><code>code content</code></pre>
<button onclick="navigator.clipboard.writeText(this.previousElementSibling.textContent).then(()=>{this.textContent='Copied';setTimeout(()=>this.textContent='Copy',1500)})">Copy</button>
```

### Collapsible (native `<details>`)

```html
<details open>
  <summary>Section title</summary>
  <div>Content</div>
</details>
<style>
details { background: var(--card); border-radius: var(--radius); padding: 8px 14px; margin-bottom: 8px; }
summary { cursor: pointer; font-weight: 600; }
</style>
```

### Vertical timeline

```html
<div class="timeline">
  <div class="stop done"><div class="dot"></div><div class="content"><h4>Step 1</h4></div></div>
  <div class="stop active"><div class="dot"></div><div class="content"><h4>Step 2</h4></div></div>
</div>
<style>
.timeline { position: relative; padding-left: 24px; }
.timeline::before { content: ""; position: absolute; left: 7px; top: 0; bottom: 0;
                    width: 2px; background: var(--line); }
.stop { position: relative; margin-bottom: 16px; }
.stop .dot { position: absolute; left: -22px; top: 6px; width: 14px; height: 14px;
             border-radius: 50%; background: var(--bg); border: 3px solid var(--muted); }
.stop.done   .dot { background: var(--done); border-color: var(--done); }
.stop.active .dot { border-color: var(--warn); }
</style>
```

### Tabs

```html
<div class="tabs">
  <button class="tab active" onclick="showTab(this,0)">Overview</button>
  <button class="tab" onclick="showTab(this,1)">Details</button>
</div>
<div class="panel active">Overview content</div>
<div class="panel">Details content</div>
<script>
function showTab(btn, i) {
  document.querySelectorAll('.tab').forEach((t, idx) => t.classList.toggle('active', idx === i));
  document.querySelectorAll('.panel').forEach((p, idx) => p.classList.toggle('active', idx === i));
}
</script>
<style>
.tabs { display: flex; gap: 4px; border-bottom: 1px solid var(--line); }
.tab { background: none; border: none; padding: 8px 16px; cursor: pointer; color: var(--muted); }
.tab.active { color: var(--fg); border-bottom: 2px solid var(--accent); }
.panel { display: none; padding: 16px 0; }
.panel.active { display: block; }
</style>
```

### Spring-easing check animation

```html
<label class="check" data-done="false" onclick="this.dataset.done = this.dataset.done==='true' ? 'false' : 'true'">
  <svg viewBox="0 0 24 24" width="20" height="20">
    <path d="M5 12l5 5L20 7" fill="none" stroke="currentColor" stroke-width="2.5"
          stroke-linecap="round" stroke-linejoin="round"/>
  </svg>
  <span>Todo item</span>
</label>
<style>
.check { display: inline-flex; align-items: center; gap: 8px; cursor: pointer;
         padding: 6px 12px; border-radius: var(--radius);
         transition: background .25s var(--ease-spring), color .25s var(--ease-spring); }
.check svg path { stroke-dasharray: 24; stroke-dashoffset: 24;
                  transition: stroke-dashoffset .35s var(--ease-spring) .1s; }
.check[data-done="true"] { background: var(--done); color: white; }
.check[data-done="true"] svg path { stroke-dashoffset: 0; }
.check[data-done="true"] span { text-decoration: line-through; opacity: .7; }
</style>
```

### Mermaid diagram (CDN, only when needed)

```html
<script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
<div class="mermaid">
flowchart LR
  A[Start] --> B{Decision}
  B -->|yes| C[Run]
  B -->|no|  D[Stop]
</div>
<script>mermaid.initialize({ startOnLoad: true, theme: 'default' });</script>
```
