---
name: visualize
description: Render markdown or supplied text into a self-contained .viz/*.html view when explicitly invoked via /visualize. Use for local markdown/text that should become easier to scan, navigate, compare, or inspect. Do not use for raw CSV/JSON charting, image generation, slide decks, or source editing.
---
# visualize
Create one self-contained HTML view that makes the source easier to inspect than plain markdown.
## Source
Use the provided path/text. If none is provided, ask the user to choose from 3-5 recent markdown candidates. Do not auto-pick.
## Source Shape
Before design, classify the source as one of: instruction/spec/skill docs, comparable items, grouped states, flow/dependencies, long prose/report, checklist, or code/config excerpt.
This controls the treatment. Do not let an attractive reference override the source shape.
## Reference
Before writing HTML, read:
1. `references/INDEX.md`
2. `references/patterns.md`
3. exactly one matching `references/examples/*.html`
Use the example for layout and interaction style, not as permission to discard source detail.
## Compression Contract
Compress for decision usefulness, not shortness.
Preserve behavior-changing details: paths, statuses, schema fields, thresholds, commands, constraints, inputs, outputs, rules, and decision criteria.
Compress first: repetition, rationale, long examples, and decorative prose.
For instruction/spec/skill docs, prefer operational fields: Trigger, Reads, Writes, Decides, Never, Output.
Use expandable `<details>` when important detail would otherwise be lost.
## Treatment
Choose the smallest useful treatment:
| Source | Treatment |
| --- | --- |
| instruction/spec/skill docs | operational cards + source details |
| comparable items | table |
| grouped states | board or grouped panels |
| flows/dependencies | diagram + detail panel |
| long prose/report | TOC + searchable sections |
| checklist | progress summary + checklist |
| code/config excerpt | annotated code + copy action |
For medium/large sources, combine overview + details. Do not make a diagram the only view when rules matter.
## HTML
Write `.viz/<name>.html` with inline CSS/JS.
- Match the user's language.
- Keep source facts faithful.
- Use responsive layout and avoid text overlap.
- Put colors in CSS variables.
- Add search/filter/collapse only when useful.
If `.gitignore` exists, add `.viz/` when missing.
## Check
Before saving, verify:
- the next decision is possible from the view
- behavior-changing rules are visible
- omissions are only repetition, rationale, or examples
- source files/sections are traceable
## Report
Reply with output path, selected reference example, and chosen treatment.