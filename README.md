# skills

A personal collection of AI agent skills for Claude Code and Codex.

Each skill lives in its own directory with a `README.md`. The `SKILL.md` sits under `skills/<name>/` in that directory, except for adversarial-review, which keeps it at the top, and inbox, which also ships a Claude Code mod.
See the linked README of each skill for install instructions and detailed usage.

| Skill | SKILL.md | Description |
| --- | --- | --- |
| [checkpoint](./checkpoint) | [checkpoint/skills/checkpoint/SKILL.md](./checkpoint/skills/checkpoint/SKILL.md) | A resumable ledger of multi-session work, so you can `/clear` at every work boundary without losing decisions. Saves results as a DAG of nodes; a new session loads only the node it needs. One skill (`/checkpoint save`, `next`, `plan`, `review`, `audit`) plus an optional compaction hook, for Claude Code and Codex. |
| [digest](./digest) | [digest/skills/digest/SKILL.md](./digest/skills/digest/SKILL.md) | Turns a long Notion page, web article, PDF, or pasted text into a layered Korean digest: one line, TL;DR, key points, a section map marking what to read in full, and what is left for you. Long documents are split and digested in parallel. For Claude Code and Codex (see below). |
| [knowledge-compile](./knowledge-compile) | [knowledge-compile/skills/knowledge-compile/SKILL.md](./knowledge-compile/skills/knowledge-compile/SKILL.md) | Compiles the work log an agent appends to `.knowledge/raw/` into curated decisions, guardrails, anti-patterns, troubleshooting, and an index. Reads only logs that changed since the last compile, ships a runner that compiles every project once a night, and loads the index into each new session. For Claude Code and Codex (see below). |
| [adversarial-review](./adversarial-review) | [adversarial-review/SKILL.md](./adversarial-review/SKILL.md) | Independent reviewers, a separate Judge, producer responses, and verification. Judges how well a plan, spec, design, or architecture achieves the user's goals, per goal, with reviewers who write their expectations before reading the work. Separates judgment-only calls from tool-using agent work. For Codex and Claude Code. |
| [inbox](./inbox) | [inbox/skills/inbox/SKILL.md](./inbox/skills/inbox/SKILL.md) | One todo list for every session, in a single markdown file. A pane to add and check off items, a band above the prompt for items due soon, `/next` to pick what to do and where, and a weekday morning summary from a scheduled task. For Claude Code and Codex (see below). |

## Codex

Run `python -X utf8 scripts/install-codex-ports.py` from this checkout to install digest, knowledge-compile, and inbox. Requires Python 3.11+ and Node 24+. The installer saves previous versions before updating. Restart Codex and review the new SessionStart hooks in `/hooks`.

Use `$digest <document>`, `$knowledge-compile` in a project with raw logs, and `$inbox` for a shared list, deadlines, completion, or a morning review. The index and due reminders load at session start. Inbox uses chat instead of the Claude pane and persistent band. Recurring compiles and morning reviews are opt-in Codex automations. The Claude-specific unattended inbox research guard is not installed.

## License

MIT.
