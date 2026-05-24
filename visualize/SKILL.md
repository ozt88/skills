---
name: visualize
description: Render markdown or supplied text into a single self-contained HTML file viewable in VS Code Live Preview. Invoked explicitly via /visualize. If an argument is provided, visualize it. If no argument is provided, collect candidates and ask the user to choose. Output goes to `.viz/<name>.html`. Do not use as a general CSV/JSON charting tool, slide-deck generator, image generator, or source markdown editor.
---

# visualize

Create an HTML view that helps the reader understand the source faster than a plain markdown render. Prefer dense, navigable, interactive structure over decorative sections.

## Core Principles

- **Reference first**: choose and read a local reference example before authoring HTML.
- **Density**: use tables, badges, diagrams, grouped panels, and compact summaries where they carry information better than prose.
- **Interactivity**: use search, filters, collapsibles, copy buttons, toggles, or small simulations when they clarify the source.
- **Navigation**: include anchors, TOC, jump links, or section tabs for multi-section documents.
- **Restraint**: do not pad small sources with unused tabs, fake dashboards, decorative diagrams, or oversized layouts.

## Output Language

UI text must match the user's current conversation language. Set `<html lang="...">` to the matching BCP-47 code, such as `ko`, `en`, or `ja`. Keep code blocks, paths, commands, technical identifiers, and proper nouns in their original form.

## Step 1: Resolve The Source

**Argument given**: use it. If it is a path, read that file. If it is raw markdown or multi-line structured text, save a temporary source as `.viz/_input.md` and visualize that. If the path/name is ambiguous, ask which source to use.

**No argument**: never auto-pick. Gather up to 3-5 candidates in this order:

1. `.md` files the assistant wrote or edited this turn.
2. A long markdown block in the previous assistant message.
3. Recently modified project `.md` files from `git diff --name-only HEAD` or filesystem timestamps.

Ask the user to choose. If no candidates exist, ask what to visualize.

Exception: if the source is under 5 lines and has no headings or structure, warn that there is little to visualize and ask for confirmation.

## Step 2: Select A Reference Treatment

Before writing HTML, always read local references in this order:

1. `references/INDEX.md`
2. `references/patterns.md`
3. Exactly one best-matching `references/examples/<N>-*.html`

Do not skip this for small documents. If the source is small, choose the closest lightweight example and simplify from it.

The selected example is the primary visual source for palette, typography, spacing, page shell, navigation, component style, and interaction style. Adapt the content and layout to the source, but do not invent an unrelated aesthetic.

When using example CSS, preserve its design intent while normalizing hardcoded colors into CSS variables where needed. Current skill rules override example implementation details when they conflict.

## Step 3: Choose The Treatment

Choose treatments from the source shape and the selected reference:

| Source shape | Typical treatment |
| --- | --- |
| Comparable attributes | Sortable/filterable table |
| Ordered phases or chronology | Timeline + progress badges |
| Items grouped by state | Kanban columns or grouped panels |
| Dependencies or flows | SVG or Mermaid diagram |
| Long prose document | Sidebar TOC + searchable body |
| Checklist | Progress summary + done/todo badges |
| Code, config, or JSON excerpt | Syntax block + copy button |
| Options or parameters | Toggles, sliders, or live preview |
| Code review or PR writeup | Severity tags + file-by-file tour |

Use one clear treatment for small sources, 2-3 treatments for medium sources, and a richer navigable view only for large or multi-section sources.

Slide-like navigation is allowed only as a treatment for an existing source document; do not create a standalone presentation deck from scratch.

## Step 4: Author The HTML

- Produce one self-contained `.html` file with inline CSS and JS.
- Use external CDN libraries only when a diagram genuinely needs them.
- Define all colors as CSS variables in `:root`; redefine the same variables in `@media (prefers-color-scheme: dark) { :root { ... } }`.
- Outside `:root`, use `var(...)` or `currentColor` for colors. Avoid hardcoded hex colors in CSS rules, SVG attributes, and JavaScript style assignments.
- Make the view responsive. Text and controls must not overlap on mobile widths.
- Localize all UI labels, buttons, captions, statuses, and prompts.
- Keep source content faithful. Do not invent facts, statuses, metrics, file references, or conclusions.

## Step 5: Save The File

Create `.viz/` if needed using the native filesystem tools available in the current environment. Write to `.viz/<basename>.html`, for example `PLAN.md` -> `.viz/PLAN.html`; inline input -> `.viz/_input.html`.

If the project has a `.gitignore`, add `.viz/` only when it is missing. Do not otherwise modify the source markdown.

## Step 6: Report

Reply in 1-2 lines in the user's language. Include:

- output path
- selected reference example
- chosen treatment

If the HTML is intentionally large for the source size, mention that a slimmer rerun is possible. On first use only, add: `Right-click the HTML in VS Code and pick Show Preview for auto-refresh.`

## Exceptions

- **Source missing**: stop and ask.
- **Re-render request**: keep the same source and choose a different treatment/reference.
- **Unsupported request**: if the user wants charts from raw CSV/JSON, image generation, or a standalone slide deck, explain that this skill is not the right tool unless they are visualizing an existing markdown/text source.
