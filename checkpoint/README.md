# Checkpoint

Checkpoint keeps a resumable ledger of multi-session work for AI coding agents, so you can `/clear` at every work boundary without losing decisions or progress.

Supported runtimes: **Claude Code** and **Codex**.

> **Visual intro (Korean):** [docs/intro.html](./docs/intro.html). Open it with VS Code's *Show Preview* or any browser.

---

## Why

Claude Code's [best practices](https://code.claude.com/docs/en/best-practices) start from one constraint: the context window fills up fast, and performance degrades as it fills. The recommended fix is to `/clear` between unrelated tasks, and to `/clear` after correcting the same problem twice instead of piling more corrections into a polluted context. Chroma's [Context Rot](https://github.com/chroma-core/context-rot) experiments show the same degradation.

What makes people hesitate to `/clear` is losing what the session decided. Checkpoint removes that cost. Before clearing, it saves the results (not the conversation) as small nodes on disk; the next session loads one node instead of the previous chat.

## How it differs from built-in features

| Feature | What it keeps | Why it is not enough here |
|---|---|---|
| `/rewind` (officially "Checkpointing") | conversation and file states inside one session | it is undo, not a handoff between sessions |
| `/resume`, `/rename` | the whole session | resuming brings back the failed attempts too |
| Auto memory, `CLAUDE.md` | facts, preferences, rules | no place for in-flight work and its decisions |
| Compaction | a lossy summary | you cannot tell what was dropped |
| **Checkpoint** | per-branch results (Output Contracts) and decisions | the next session loads one node |

Despite the name, this project is unrelated to Claude Code's `/rewind` checkpoints.

---

## Usage

One skill, `checkpoint`, with five subcommands:

| Subcommand | Use it to |
|---|---|
| `/checkpoint review` | decide whether the session hit a work boundary. Claude runs it on its own at boundaries. |
| `/checkpoint save` | record work this session performed as nodes |
| `/checkpoint plan` | split unstarted future work into nodes (proposes first, writes after approval) |
| `/checkpoint next` | in a fresh session, open the next node with minimal context |
| `/checkpoint audit` | check whether a graph can be trusted before resuming it |

In Codex, mention the skill the way Codex does (for example `$checkpoint save`).

### The cycle

```text
work ── boundary? ── /checkpoint review ── continue
                                  └──────── /checkpoint save ── /checkpoint plan (if needed) ── /clear
new session ── /checkpoint next ── work ...
```

A **work boundary** is one of:

- moving to a task unrelated to the work so far
- correcting the same problem more than twice
- finishing a task when the next request is a different slice

Session length and token count alone are not boundaries. Checkpoint does not ask you to stop work early.

### When compaction happens first

If a session reaches compaction without hitting a boundary, a single `SessionStart(compact)` hook asks the agent to run `review` and passes the transcript path. `review` uses `scripts/extract_prompts.py` to read only the user prompts from before the compaction. Nothing else is recorded.

---

## Files

Graphs live in the project being worked on:

```text
<project>/.checkpoint/graphs/<slug>/
  index.md        routing and status only
  DECISIONS.md    graph-wide decisions (checkpoint-local ADRs)
  nodes/          one file per node: goal, Progress Snapshot or Output Contract
<project>/.checkpoint/archive/graphs/<slug>/   graphs with nothing left to do
```

The full format (status values, edges, node template, checks) is in [skills/checkpoint/format.md](./skills/checkpoint/format.md). `scripts/check_graph.py` runs the mechanical checks.

Repository layout:

```text
checkpoint/
├─ skills/checkpoint/
│  ├─ SKILL.md            routing and shared rules
│  ├─ format.md           graph format
│  ├─ save.md  plan.md  next.md  review.md  audit.md
│  ├─ scripts/            check_graph.py, extract_prompts.py
│  └─ agents/openai.yaml  Codex UI metadata
├─ hooks/checkpoint_compact_hook.py
├─ scripts/install-claude.sh, install-codex.sh
└─ docs/intro.html
```

---

## Install

Requirements: bash and `python3` on `PATH`.

```bash
bash scripts/install-claude.sh           # Claude Code, global (~/.claude/)
bash scripts/install-claude.sh --local   # Claude Code, current project (./.claude/)
bash scripts/install-codex.sh            # Codex (~/.codex/)
```

Each installer copies the skill and the hook and registers one hook, `SessionStart` with the `compact` matcher. Re-running is safe. Restart the runtime afterwards; in Codex, approve the hook with `/hooks`.

The skill works without the hook. The hook only covers sessions that reach compaction before a boundary.

### Upgrading from the six-skill version

The installers remove the old `checkpoint-*` skills, the per-prompt logging hook, and its four hook registrations. Existing graphs keep working; the format is unchanged except that status values gained `Handed off`.

Two things the installers leave alone:

- `.checkpoint/sessions/` directories in your projects. They held prompt logs and are no longer read; delete them.
- Hook entries an earlier Codex install wrote to `~/.codex/requirements.toml`. The installer warns if it finds them; remove them by hand.

---

## Design principles

- **Make handoffs unnecessary instead of better.** Resume means reading the graph and loading the next node, not replaying the previous session.
- **Results, not conversation.** Output Contracts carry what was decided and produced; exploration ends with the session.
- **One branch per node.** A finished task with three follow-ups becomes three nodes, so working on one never drags in the other two.
- **Detect boundaries in the conversation; keep the hook as a backstop.** The hook records nothing and only reacts to compaction.
