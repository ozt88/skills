---
name: visualize
description: Render input content or a markdown file into a single self-contained HTML file viewable in VS Code Live Preview. Invoked explicitly by the user via /visualize. If an argument is provided, visualize it directly. If no argument, collect candidates (recent .md files, the last assistant markdown block) and ask the user which one to visualize. Output goes to `.viz/<name>.html`. Do NOT use for CSV/JSON charts, slide decks, image generation, or modifying the source markdown.
---

# visualize

Don't merely convert markdown. Produce HTML that uses density, interactivity, spatial layout, and navigation so the reader grasps the work at a glance.

## Core principles

- **Density**: tables instead of lists, SVG diagrams instead of paragraphs, badges instead of plain text.
- **Interactivity**: collapsibles, filters, sorting, copy buttons, toggles, sliders.
- **Spatial layout**: grids, sidebars, cards — more per screen.
- **Navigation**: TOC, anchors, search for large documents.

Avoid a literal markdown re-render, static read-only pages, and prose where a table would carry the data.

## Output language

UI text (labels, statuses, captions, prompts, buttons) must match the **user's current conversation language**. Detect from the user's recent messages, set `<html lang="...">` to the matching BCP-47 code (e.g. `ko`, `en`, `ja`), and translate every UI string. Keep code blocks, technical terms, file names, and proper nouns in their original form.

---

## Step 1: Resolve the source

**Argument given** → use it. If it's a path, read that file. If it's raw markdown (multi-line with headings/checkboxes), save to `.viz/_input.md` and use that. If the file name is ambiguous (no path, multiple matches), ask which.

**No argument** → never auto-pick. Gather up to 3–5 candidates in this priority order:

1. `.md` files Claude wrote or edited this turn.
2. A long markdown block (>30 lines, or with headings/checkboxes) in the previous assistant message.
3. Recently modified project `.md` files (`find` or `git diff --name-only HEAD`).

Then ask the user to choose, translated to their language. Example shape:

> Choose what to visualize:
> 1. `PLAN.md` — written this turn
> 2. `handoff.md` — modified 5 minutes ago
> 3. Last assistant markdown block (52 lines)
> 4. Specify a different file or content

If zero candidates exist: ask what to visualize.

---

## Step 2: Write the HTML

### Authoring rules

- **Single file**. Inline CSS and JS. External CDN libs (Mermaid, D3) only when a diagram genuinely needs them.
- **Dark mode**. Include `prefers-color-scheme: dark`.
- **Localized UI** per the rule above.
- **Responsive**. Must not break on mobile widths.

### Pick a treatment

| Content shape | Treatment |
| --- | --- |
| Many comparable attributes | Sortable / filterable table |
| Ordered steps or phases | Vertical timeline, progress bar |
| Items grouped by state | Kanban-style columns (visual grouping) |
| Dependencies or connections | SVG diagram or Mermaid |
| Prose-heavy long document | Sidebar TOC + body + search box |
| Checklists | Progress bar + done/todo badges |
| Code or JSON | Syntax highlight + copy button |
| Parameters or options | Sliders / toggles for live tweaking |
| Categorized items | Tabs or accordion |
| Code review | Annotated diff, severity tags, file-by-file tour |

Mix treatments freely. If a better representation comes to mind, use it.

### When you need more depth

Read `references/INDEX.md` (small routing card). It tells you whether to open `references/patterns.md` (category-specific approaches with example URLs), `references/snippets.md` (copy-paste HTML/CSS/JS), or the actual file in `references/examples/<N>-*.html` for full implementations. Don't pre-load anything beyond INDEX.md until needed.

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

1–2 lines in the user's language. Include the output path and the treatment chosen (e.g. "table + timeline", "searchable card grid").
**First run only** (when the `touch` above just created the marker): add one line — "Right-click the HTML in VS Code and pick **Show Preview** for auto-refresh."

---

## Exceptions

- **Source missing** → stop and ask.
- **Under 5 lines, no headings** → warn that there's little to visualize and confirm.
- **Re-render request** → keep the same source, apply a different treatment.
