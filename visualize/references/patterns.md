# Patterns by category

Effective HTML treatments per content type. Pair with [`snippets.md`](./snippets.md) for ready-to-paste code, or read the actual file in `examples/` for full implementation.

## Contents

- [Exploration & planning](#exploration--planning)
- [Code review](#code-review)
- [Design system](#design-system)
- [Prototyping](#prototyping)
- [Diagrams](#diagrams)
- [Decks, research & reports](#decks-research--reports)
- [Custom editors](#custom-editors)

Source of inspiration: <https://thariqs.github.io/html-effectiveness/>. Local copies in `examples/`. **For implementation details, read the actual file** — code is more precise than descriptions.

---

## Exploration & planning

PLAN.md, design docs, ADRs.

- **Side-by-side comparison** ([01-exploration-code-approaches.html](./examples/01-exploration-code-approaches.html)): 2–3 approaches stacked vertically + Pro/Con table + inline metric badges (`Bundle impact`).
- **Light/dark design compare** ([02-exploration-visual-designs.html](./examples/02-exploration-visual-designs.html)): 4 directions × Light/Dark toggles, subtle bob animations.
- **Milestones → data flow → mockups → code** ([16-implementation-plan.html](./examples/16-implementation-plan.html)): Progress badges, risk/mitigation 2-column table, threaded comments.

## Code review

REVIEW.md, PR descriptions, audit notes.

- **Annotated PR** ([03-code-review-pr.html](./examples/03-code-review-pr.html)): Overview → risk map → file list. Inline line annotations + Blocking / Nit / Safe badges.
- **PR writeup** ([17-pr-writeup.html](./examples/17-pr-writeup.html)): TL;DR → Why → File-by-file → Test plan → Rollout. `file:line` references, ±line-count badges, Before/After tables.
- **Module map** ([04-code-understanding.html](./examples/04-code-understanding.html)): Diagram → 5-step call-stack walkthrough. `<details>` toggles fold source.

## Design system

Token catalogs, component galleries.

- **Living design system** ([05-design-system.html](./examples/05-design-system.html)): Color / type / spacing / shadow / component hierarchy + live buttons, inputs, badges.
- **Component variants sheet** ([06-component-variants.html](./examples/06-component-variants.html)): 6-variant grid + padding/border/shadow sliders for live tuning + hover-reveal Props code.

## Prototyping

Throwaway interaction sketches.

- **Micro-interaction sandbox** ([07-prototype-animation.html](./examples/07-prototype-animation.html)): Click checkbox → fill → draw check → strike-through → shrink. Spring easing.
- **Drag-and-drop flow** ([08-prototype-interaction.html](./examples/08-prototype-interaction.html)): Reorder sidebar list, snap when crossing the midline. ~40 lines of vanilla JS.

## Diagrams

Architecture, flows, illustrations.

- **SVG sheet** ([10-svg-illustrations.html](./examples/10-svg-illustrations.html)): Three 720×320 SVGs + individual Download buttons. 5-color palette, consistent corner radius.
- **Clickable flowchart** ([13-flowchart-diagram.html](./examples/13-flowchart-diagram.html)): Click a node → panel with runtime / duration / failure modes. Rect = process, diamond = decision.

## Decks, research & reports

Status updates, postmortems, learning material.

- **Arrow-key slide deck** ([09-slide-deck.html](./examples/09-slide-deck.html)): Left/right arrow nav, `1 / 6` counter, big-number metrics.
- **Feature explainer** ([14-research-feature-explainer.html](./examples/14-research-feature-explainer.html)): TOC + 4-stage expand + 3-column code compare + FAQ.
- **Concept simulator** ([15-research-concept-explainer.html](./examples/15-research-concept-explainer.html)): Linear learning flow + interactive simulator (hash-ring add/remove/reset) + comparison table + glossary.
- **Weekly status report** ([11-status-report.html](./examples/11-status-report.html)): Big-number KPI header + Shipped table + daily heatmap.
- **Incident report** ([12-incident-report.html](./examples/12-incident-report.html)): Meta chip row (SEV-2 / state / owner) → TL;DR → timeline → root cause → impact → actions.

## Custom editors

Single-purpose UIs with state and export.

- **Triage board** ([18-editor-triage-board.html](./examples/18-editor-triage-board.html)): Now / Next / Later / Cut kanban + DnD + tag filter + "Copy as markdown" export.
- **Feature flag editor** ([19-editor-feature-flags.html](./examples/19-editor-feature-flags.html)): Toggles + auto-updating dependency warnings + Copy diff / Copy full JSON + "Pending changes (n)" counter.
- **Prompt tuner** ([20-editor-prompt-tuner.html](./examples/20-editor-prompt-tuner.html)): Left edit / right live preview + `{{slot}}` syntax + token count + Copy prompt.
