---
name: checkpoint
description: Keeps a resumable ledger of multi-session work in .checkpoint/graphs/ so the user can /clear without losing decisions or progress. Use when the user asks to save, checkpoint, resume, continue, plan future work, or audit a checkpoint; at a work boundary (moving to an unrelated task, correcting the same problem more than twice, finishing a task); when the checkpoint hook reports a compaction; or when a fresh session starts in a project with active checkpoint graphs. Subcommands are save, next, plan, review, audit.
---

# Checkpoint

A checkpoint graph keeps what multi-session work produced (results and decisions, not the conversation) as small nodes on disk. A fresh session reads `index.md` and one node instead of the previous chat, so the user can run `/clear` at every work boundary and keep the context small.

## Subcommands

The subcommand is the first word of the arguments (`$ARGUMENTS` in Claude Code) or of the user's request.

| Subcommand | Use it to | Read |
|---|---|---|
| `review` | decide whether a work boundary was reached; answer the compaction reminder | [review.md](review.md) |
| `save` | record work this session performed | [save.md](save.md) |
| `plan` | split unstarted future work into nodes | [plan.md](plan.md) |
| `next` | open the next node in a fresh session | [next.md](next.md) |
| `audit` | check whether a graph can be trusted | [audit.md](audit.md) |

Without a subcommand: in a fresh session where active graphs exist and no work has started, run `next`; otherwise run `review`.

Every subcommand except `review` reads or writes graph files, so read [format.md](format.md) before it.

## Rules for every subcommand

- `review` never writes graph files. `audit` writes only when the user asks for a repair.
- `index.md` is the only source of node status.
- Write graph files and replies in the user's language. Keep the section headings from format.md in English; the checks look for them.
- Treat a saved graph as possibly stale. The newest user message and the current files win; report a conflict before acting on it.
- When a subcommand could have written graph files, end the reply with `Checkpoint state: updated` or `Checkpoint state: unchanged — <reason>`.
