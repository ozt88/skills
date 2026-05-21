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

Avoid: literal markdown re-renders, static read-only pages, prose where a table would carry the data, and padding simple content with decorative sections it doesn't earn.

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

### Size discipline

Output HTML should scale with source depth, not max out by default:

| Source markdown | Target HTML size | Typical treatment |
| --- | --- | --- |
| Under ~2 KB | Under ~10 KB | One simple treatment, no extra tabs / diagrams |
| ~2–10 KB | ~10–25 KB | Mix 2–3 treatments |
| Over ~10 KB or multi-section work | Up to ~35 KB | Full toolkit (tabs, search, SVG, etc.) |

If you exceed the band for the source size, briefly note it in the report so the user can ask for a lighter version (e.g. "HTML is 34 KB — try `/visualize ... as outline` for a slimmer one"). **Don't pad with decorative sections if the content doesn't earn them.**

### When you need more depth

1. Read `references/INDEX.md` to find the best-matching example category.
2. Read `references/patterns.md` to identify which `examples/<N>-*.html` file fits the content shape.
3. **Read that example file directly** — it is the canonical source for palette, typography, layout, and component style. Copy the `:root` variables, body, page, nav, h1, h2, and p CSS **verbatim** from the example. Do not approximate or round any values.
4. Only open `references/snippets.md` for a specific micro-component (e.g. a toggle switch or copy button) that the example file doesn't already contain. Never use snippets as a substitute for the example's overall aesthetic.

Don't pre-load anything beyond INDEX.md until needed.

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

1–2 lines in the user's language. Include the output path and the treatment chosen (e.g. "table + timeline", "searchable card grid"). If the HTML exceeded the size band for the source, append a one-line note offering a slimmer rerun.
**First run only** (when the `touch` above just created the marker): add one line — "Right-click the HTML in VS Code and pick **Show Preview** for auto-refresh."

---

## Exceptions

- **Source missing** → stop and ask.
- **Under 5 lines, no headings** → warn that there's little to visualize and confirm.
- **Re-render request** → keep the same source, apply a different treatment.
