# skills

A personal collection of AI agent skills for Claude Code and Codex.

Each skill lives in its own directory with a `README.md`. The `SKILL.md` sits under `skills/<name>/` in that directory, except for adversarial-review, which keeps it at the top, and inbox, which is a mod with no SKILL.md.
See the linked README of each skill for install instructions and detailed usage.

| Skill | SKILL.md | Description |
| --- | --- | --- |
| [checkpoint](./checkpoint) | [checkpoint/skills/checkpoint/SKILL.md](./checkpoint/skills/checkpoint/SKILL.md) | A resumable ledger of multi-session work, so you can `/clear` at every work boundary without losing decisions. Saves results as a DAG of nodes; a new session loads only the node it needs. One skill (`/checkpoint save`, `next`, `plan`, `review`, `audit`) plus an optional compaction hook, for Claude Code and Codex. |
| [digest](./digest) | [digest/skills/digest/SKILL.md](./digest/skills/digest/SKILL.md) | Turns a long Notion page, web article, PDF, or pasted text into a layered Korean digest: one line, TL;DR, key points, a section map marking what to read in full, and what is left for you. Long documents are split and digested in parallel. For Claude Code. |
| [knowledge-compile](./knowledge-compile) | [knowledge-compile/skills/knowledge-compile/SKILL.md](./knowledge-compile/skills/knowledge-compile/SKILL.md) | Compiles the work log an agent appends to `.knowledge/raw/` into curated decisions, guardrails, anti-patterns, troubleshooting, and an index. Reads only logs that changed since the last compile, ships a runner that compiles every project once a night, and loads the index into each new session. For Claude Code. |
| [adversarial-review](./adversarial-review) | [adversarial-review/SKILL.md](./adversarial-review/SKILL.md) | Independent reviewers, a separate Judge, producer responses, and verification. Judges how well a plan, spec, design, or architecture achieves the user's goals, per goal, with reviewers who write their expectations before reading the work. Separates judgment-only calls from tool-using agent work. For Codex and Claude Code. |
| [inbox](./inbox) | none (a mod: [inbox/mod](./inbox/mod)) | One todo list for every session, in a single markdown file. A pane to add and check off items, a band above the prompt for items due soon, `/next` to pick what to do and where, and a weekday morning summary from a scheduled task. For Claude Code. |

## License

MIT.
