---
name: visualize
description: Render input content or a markdown file into a single self-contained HTML file viewable in VS Code Live Preview. Invoked explicitly by the user via /visualize. If an argument is provided, visualize it directly. If no argument, collect candidates (recent .md files, the last assistant markdown block) and ask the user which one to visualize. Output goes to `.viz/<name>.html`. Do NOT use for CSV/JSON charts, slide decks, image generation, or modifying the source markdown.
---

# visualize

Don't merely convert markdown — produce HTML that uses what HTML can do (density, interactivity, spatial layout, navigation) so the reader grasps the work at a glance.

## Core principles

- **Information density**: tables instead of lists, SVG diagrams instead of paragraphs, visual badges instead of plain text
- **Interactivity**: collapsibles, filters, sorting, copy buttons, toggles
- **Spatial layout**: grids, sidebars, cards — more content per screen
- **Navigation**: table of contents, anchors, search box for large documents

## Output language

UI text in the HTML output (labels, statuses, captions, prompts, buttons) must be translated into the **user's current language** — match whatever language the user is using in this conversation. Do not hardcode any single language; detect from the user's messages and translate accordingly. Set `<html lang="...">` to the matching BCP 47 code (e.g. `ko`, `en`, `ja`). Keep code blocks, technical terms, file names, and proper nouns in their original form.

---

## Step 1: Resolve the source

### A. Argument provided — proceed without asking

- **File path or name** (e.g. `PLAN.md`, `.planning/handoff.md`, `~/notes/spec.md`) → use that file
- **Raw markdown text** (multi-line content with headings/checkboxes passed as the argument) → save to `.viz/_input.md` then use

If the file name is ambiguous (no path, multiple matches), ask which one and proceed.

### B. No argument — always ask the user

Do NOT auto-pick. Collect 3–5 candidates and let the user choose.

Candidate sources, in priority order:

1. **`.md` files written or edited by Claude this turn** (highest priority if present)
2. **A long markdown block in the previous assistant message** (>30 lines, or containing headings/checkboxes) — label as "last assistant markdown"
3. **Recently modified `.md` files in the project** (e.g. `PLAN.md`, `handoff.md`, `.planning/**/*.md`) — use `find` or `git diff --name-only HEAD`

Ask using this shape (translated to the user's language):

> Choose what to visualize:
> 1. `PLAN.md` — written this turn
> 2. `handoff.md` — modified 5 minutes ago
> 3. Last assistant markdown block (52 lines)
> 4. Specify a different file or content

If there are zero candidates, ask: "What file or content should I visualize? (e.g. `PLAN.md`, or pass raw markdown)"

---

## Step 2: Write the HTML

### Authoring rules

- **Single file**: inline CSS and JS, no external dependencies (CDN libraries such as Mermaid or D3 are allowed only when a diagram genuinely needs them)
- **Dark mode**: include a `prefers-color-scheme: dark` media query
- **Localized UI**: set `<html lang>` to the user's language and translate all UI text accordingly
- **Responsive**: must not break on mobile widths

### Technique table (mix freely)

| Content shape | Treatment |
| --- | --- |
| Many comparable attributes | Sortable / filterable table |
| Ordered steps or phases | Vertical timeline, progress bar |
| Items grouped by state | Kanban-style columns (visual grouping; no drag needed) |
| Dependencies or connections | SVG diagram or Mermaid |
| Prose-heavy long document | Sidebar TOC + body + search box |
| Checklists | Progress bar + done/todo badges |
| Code or JSON snippets | Syntax highlight + copy button |
| Parameters or options | Sliders / toggles for live tweaking |
| Categorized items | Tabs or accordion |
| Code review | Annotated diff, severity tags, file-by-file tour |

### References

- `references/patterns.md` — common principles, category-specific patterns, reusable snippets
- `references/examples/*.html` — 20 working examples. **If a specific implementation detail is unclear, read the actual file.**

These are not mandatory templates — if a better representation comes to mind, use it.

### Anti-patterns

- HTML that's just a literal markdown rendering (only headings, lists, paragraphs)
- Static pages with no interactivity (single read-only view)
- Presenting key data as prose when a table would convey it better

---

## Step 3: Save the file

```bash
mkdir -p .viz
grep -q '\.viz' .gitignore 2>/dev/null || ([ -d .git ] && echo '.viz/' >> .gitignore)
[ -f .viz/.first-run-done ] || touch .viz/.first-run-done
```

Write to `.viz/<basename>.html` (e.g. `PLAN.md` → `.viz/PLAN.html`; inline input → `.viz/_input.html`).

---

## Step 4: Report

1–2 lines, in the user's language. Include the output path and the chosen treatment (e.g. "table + timeline", "searchable card grid").
**First run only** (when the `touch` above just created the marker file): append one line telling the user to right-click the HTML and choose "Show Preview" in VS Code for auto-refresh.

---

## Exceptions

- **Source file missing**: stop and ask.
- **Source under 5 lines with no headings**: warn that there isn't much to visualize and confirm before proceeding.
- **Re-render request**: keep the same source, apply a different treatment without re-resolving.
