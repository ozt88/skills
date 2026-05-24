# visualize

Codex skill for turning markdown or supplied text into a self-contained HTML view under `.viz/`.

The skill is intended for existing source material: plans, reviews, reports, notes, specs, handoffs, and structured prose. It is not a general charting, image generation, or slide-deck authoring tool.

## Behavior

- `/visualize PLAN.md`: visualize the given file.
- `/visualize`: ask the user to choose from recent markdown candidates.
- `/visualize PLAN.md as kanban`: use the requested treatment if it fits the source.

Every run selects a local reference treatment before writing HTML:

1. `references/INDEX.md`
2. `references/patterns.md`
3. one matching `references/examples/<N>-*.html`

The generated UI should match the user's conversation language and remain faithful to the source content.

## Layout

```text
visualize/
├── SKILL.md
├── README.md
└── references/
    ├── INDEX.md
    ├── patterns.md
    └── examples/
        └── 20 focused HTML reference examples
```

## Preview

Open `.viz/<name>.html` with VS Code Live Preview or a browser. The file is self-contained unless the selected treatment genuinely needs a CDN library such as Mermaid.
