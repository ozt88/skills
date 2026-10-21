# skills

A personal collection of AI agent skills for Claude Code and Codex.

Each skill lives in its own directory with a `README.md` and `SKILL.md`.
See the linked README of each skill for install instructions and detailed usage.

| Skill | Description |
| --- | --- |
| [checkpoint](./checkpoint) | A resumable ledger of multi-session work, so you can `/clear` at every work boundary without losing decisions. Saves results as a DAG of nodes; a new session loads only the node it needs. One skill (`/checkpoint save`, `next`, `plan`, `review`, `audit`) plus an optional compaction hook, for Claude Code and Codex. |
| [knowledge-compile](./knowledge-compile) | Compiles the work log an agent appends to `.knowledge/raw/` into curated decisions, guardrails, anti-patterns, troubleshooting, and an index. Reads only logs that changed since the last compile, and ships a runner that compiles every project once a night. For Claude Code. |

## License

MIT.
