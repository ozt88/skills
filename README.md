# skills

A personal collection of AI agent skills for Claude Code and Codex.

Each skill lives in its own directory with a `README.md` and `SKILL.md`.
See the linked README of each skill for install instructions and detailed usage.

| Skill | Description |
| --- | --- |
| [visualize](./visualize) | Turns plain-text material — markdown notes, plans, reviews, status reports — into a single readable HTML view (tables, timelines, flowcharts, navigable sections). Invoked via `/visualize`. |
| [checkpoint](./checkpoint) | Context-management workflow for long-running AI sessions. Saves work as a DAG of nodes so a new session loads only the slice it needs instead of replaying the whole previous conversation. Six skills (`/checkpoint-review`, `-save`, `-plan`, `-next`, `-audit`, `-viz`) plus optional global hooks that automate the review/save cycle around `compact`. |

## License

MIT.
