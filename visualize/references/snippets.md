# Reusable snippets

Copy-paste HTML / CSS / JS. Replace text and tokens to fit your context.

## Contents

- [Color & type tokens (dark-mode aware)](#color--type-tokens-dark-mode-aware)
- [Semantic badge system](#semantic-badge-system)
- [KPI header](#kpi-header)
- ["Show source" toggle](#show-source-toggle)
- [Arrow-key slide deck](#arrow-key-slide-deck)
- [Sidebar + content layout (searchable)](#sidebar--content-layout-searchable)
- [Card grid (color by state)](#card-grid-color-by-state)
- [Sortable table](#sortable-table)
- [Copy button](#copy-button)
- [Native collapsible](#native-collapsible)
- [Vertical timeline](#vertical-timeline)
- [Tabs](#tabs)
- [Spring-easing check animation](#spring-easing-check-animation)
- [Mermaid diagram (CDN, only when needed)](#mermaid-diagram-cdn-only-when-needed)

---

## Color & type tokens (dark-mode aware)

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

## Semantic badge system

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

## KPI header

Status reports, postmortems, dashboards.

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

## "Show source" toggle

Native `<details>`, no JS.

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

## Arrow-key slide deck

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

## Sidebar + content layout (searchable)

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

## Card grid (color by state)

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

## Sortable table

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

## Copy button

```html
<pre><code>code content</code></pre>
<button onclick="navigator.clipboard.writeText(this.previousElementSibling.textContent).then(()=>{this.textContent='Copied';setTimeout(()=>this.textContent='Copy',1500)})">Copy</button>
```

## Native collapsible

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

## Vertical timeline

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

## Tabs

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

## Spring-easing check animation

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

## Mermaid diagram (CDN, only when needed)

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
