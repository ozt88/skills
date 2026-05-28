---
name: checkpoint-viz
description: Visualize the current checkpoint graph as an interactive HTML dashboard. Shows node DAG, status kanban, and details panel. Output goes to .viz/checkpoint-<slug>.html. Use when the user wants to see the checkpoint graph visually, inspect progress at a glance, or share the graph state.
---

# Checkpoint Visualizer

Produce an interactive, single-file HTML dashboard from a checkpoint graph.
Follow the same visual conventions as the `visualize` skill (CSS variables, dark mode).
UI labels (tab names, buttons, status text) must match the user's current conversation language.

---

## Step 1: Locate the graph

**Argument given** → treat it as a graph slug. Look for:

```text
<project-root>/.checkpoint/graphs/<slug>/index.md
```

**No argument** → find all active graphs:

```bash
find . -path '*/.checkpoint/graphs/*/index.md' ! -path '*/archive/*' | sort
```

- If exactly one graph: use it.
- If multiple: list them and ask the user to choose. Show slug + first `Recommended Next` line from each `index.md`.
- If none: report "No active checkpoint graphs found." and stop.

---

## Step 2: Parse the graph

Read in this order:

1. **`index.md`** — canonical node status and routing. Extract:
   - Graph title / slug
   - For each node: ID (e.g. `N1`), slug name, status, dependencies, blocked-by notes
   - `Recommended Next` if present
   - Node statuses: `Ready` | `In Progress` | `Done` | `Blocked` | `Parked` | `Dropped` | `Superseded` | `Split` | `Merged`

2. **`DECISIONS.md`** — extract CP-ADR titles, status (Accepted/Rejected/Superseded), and one-line context summaries.

3. **Node files** (`nodes/*.md`) — for each node: read up to the first `## Output Contract` or `## Progress Snapshot` section. Extract:
   - Goal (first paragraph after `## Goal` or `# Node: …`)
   - Progress Snapshot bullet points if present
   - Output Contract bullet points if Done

### Index.md parsing patterns

`index.md` may use either a table or heading-based layout. Handle both:

**Table format:**

```md
| Node | Status | Dependencies | Notes |
|------|--------|-------------|-------|
| N1 — setting-index | Ready | — | — |
| N2 — root-consolidation | Blocked | N1 | Waiting for N1 |
```

**Heading format:**

```md
### N1 — setting-index
Status: Ready
Dependencies: none
```

Use regex to capture `N\d+` IDs, status values, and dependency lists. Treat `—`, `-`, `none`, `(none)` as "no dependencies".

---

## Step 3: Build the HTML

### Data embedding

Embed all parsed graph data as a JS constant at the top of the `<script>` block:

```js
const GRAPH = {
  slug: "my-graph",
  title: "My Graph Title",
  recommendedNext: "N2",
  nodes: [
    {
      id: "N1",
      name: "setting-index",
      status: "Done",
      deps: [],
      goal: "Ensure index.md has exactly one entry per node.",
      snapshot: null,
      contract: { decisions: ["Use table format"], files: ["index.md"], unlocks: ["N2"] }
    },
    {
      id: "N2",
      name: "root-consolidation",
      status: "Blocked",
      deps: ["N1"],
      blockedBy: "N1 not done",
      goal: "Consolidate root context files into a single source.",
      snapshot: { partial: ["Drafted outline"], stopping: "Blocked on N1", next: "Resume after N1 Done" }
    }
  ],
  decisions: [
    { id: "CP-ADR-001", title: "Use table format for index.md", status: "Accepted", summary: "Easier to parse and scan than heading format." }
  ]
};
```

### CSS palette (required — copy verbatim)

```css
:root {
  --bg:       #FAF9F5;
  --surface:  #ffffff;
  --text:     #3D3D3A;
  --heading:  #141413;
  --border:   #D1CFC5;
  --muted:    #87867F;
  --accent:   #D97757;
  --serif:    ui-serif, Georgia, "Times New Roman", serif;
  --sans:     system-ui, -apple-system, "Segoe UI", Roboto, sans-serif;
  --mono:     ui-monospace, "SF Mono", Menlo, Consolas, monospace;

  /* status tokens */
  --s-done-bg:     #F0F7EC; --s-done-bd: #788C5D; --s-done-tx: #4A6A30;
  --s-prog-bg:     #FEF6EE; --s-prog-bd: #D97757; --s-prog-tx: #A84E2A;
  --s-ready-bg:    #EEF3FA; --s-ready-bd: #2471A3; --s-ready-tx: #1A5A8A;
  --s-block-bg:    #FEF0EF; --s-block-bd: #C0392B; --s-block-tx: #9B2219;
  --s-parked-bg:   #F0EEE6; --s-parked-bd: #87867F; --s-parked-tx: #5A5955;
  --s-dropped-bg:  #F5F4F2; --s-dropped-bd: #C0BEB4; --s-dropped-tx: #87867F;
}
@media (prefers-color-scheme: dark) {
  :root {
    --bg:       #1A1A17;
    --surface:  #272724;
    --text:     #C0BEB4;
    --heading:  #F0EEE6;
    --border:   #3A3A36;
    --muted:    #87867F;
    --accent:   #D97757;

    --s-done-bg:     #162016; --s-done-bd: #4A6A3A; --s-done-tx: #8ABF6A;
    --s-prog-bg:     #281C10; --s-prog-bd: #A05828; --s-prog-tx: #D4915A;
    --s-ready-bg:    #101828; --s-ready-bd: #2A5080; --s-ready-tx: #7AABDB;
    --s-block-bg:    #281010; --s-block-bd: #8A2A2A; --s-block-tx: #E07070;
    --s-parked-bg:   #201E18; --s-parked-bd: #4A4840; --s-parked-tx: #87867F;
    --s-dropped-bg:  #1C1C1A; --s-dropped-bd: #3A3A36; --s-dropped-tx: #5A5955;
  }
  body { background: var(--bg); }
}
```

### HTML structure

```html
<body>
  <div class="wrap">
    <header>     <!-- graph title, eyebrow, progress bar, Recommended Next chip -->
    <div class="main-layout">   <!-- two-column: left=tabs+view, right=detail-panel -->
      <div class="view-area">
        <div class="tabs">      <!-- [DAG] [Kanban] [Decisions] -->
        <div id="tab-dag">      <!-- SVG DAG -->
        <div id="tab-kanban" hidden>    <!-- kanban columns -->
        <div id="tab-decisions" hidden> <!-- ADR table -->
      </div>
      <aside id="detail-panel"> <!-- node detail side panel -->
    </div>
  </div>
</body>
```

### Progress bar

```html
<div class="progress-bar">
  <div class="progress-fill" style="width: calc(3 / 7 * 100%)"></div>
</div>
<span class="progress-label">3 / 7 done</span>
```

### DAG view (SVG-based, no CDN dependency)

Use a pure JS topological layout:

1. Compute node levels via BFS from root nodes (nodes with no deps).
2. Within each level, sort nodes by ID.
3. Layout: each level is a horizontal row, spaced 140px vertically. Nodes within a level are spaced 200px horizontally, centered.
4. Draw edges as SVG `<path>` with cubic bezier curves. Arrowhead via `<marker>`.
5. Node boxes: 180×52px rounded rectangles colored by status token.
6. "Recommended Next" node gets a `★` prefix and a clay-colored double-border.
7. On click: call `showDetail(nodeId)` to update the side panel.

Use `viewBox` sized to fit the graph with 40px padding. Add `overflow-x: auto` wrapper.

Nodes use `g.node[data-id="N1"]` elements. Highlight on hover with a lighter stroke.

### Kanban view

Five columns (hide empty columns):

| In Progress | Ready | Blocked | Done | Other |
|-------------|-------|---------|------|-------|
| `--s-prog-*` | `--s-ready-*` | `--s-block-*` | `--s-done-*` | `--s-parked-*` |

"Other" covers: Parked, Dropped, Superseded, Split, Merged.

Each card shows: node ID badge, name, dependency chips (if Blocked).

### Decision tab

Simple table: ADR ID | Title | Status badge | Summary

### Detail panel (right side)

Default state: placeholder text telling the user to click a node.

When a node is selected, show:

```text
[N2] root-consolidation   [Blocked]
───────────────────────────────────
Goal:
  Consolidate root context files into a single source.

Progress Snapshot:       (shown when In Progress or Blocked)
  - Partial work: Drafted outline
  - Stopping point: Blocked on N1
  - Next action: Resume after N1 Done

Output Contract:         (shown when Done)
  - Decisions: Use table format
  - Files changed: index.md
  - Unlocks: N2

Dependencies: N1 ✓, N3 ⏳

[Copy to clipboard]
```

---

## Step 4: Save and report

```bash
mkdir -p .viz
grep -q '\.viz' .gitignore 2>/dev/null || ([ -d .git ] && echo '.viz/' >> .gitignore)
[ -f .viz/.first-run-done ] || touch .viz/.first-run-done
```

Write to `.viz/checkpoint-<slug>.html`.

Report 1–2 lines in the user's language: output path, view modes included, node count summary.
First run only: add a one-line hint about VS Code **Show Preview**.

---

## Exceptions

- **`index.md` missing or unreadable** → stop and report path.
- **No nodes found** → warn and offer to audit the checkpoint.
- **Graph is archived** → note it's archived, offer to visualize anyway.
- **Circular dependency detected** → note in the header and skip the cycle edge.

---

## Size guidance

Checkpoint graphs are typically small (< 15 nodes). Target HTML under 20 KB.
If node detail text is very long, truncate to 300 chars with `…` in the panel JS.
