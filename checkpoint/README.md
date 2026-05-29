# Checkpoint

Checkpoint is a context-management workflow for long-running AI coding sessions.
It saves work as a small DAG of nodes so that a new session can load only the slice it needs, instead of replaying every previous conversation.

Supported runtimes: **Claude Code** and **Codex**.

---

## The Problem: Context Rot

LLM performance degrades non-linearly as input length grows. Chroma's
[Context Rot](https://github.com/chroma-core/context-rot) experiments show that
the common assumption "the 10,000th token is handled as reliably as the 100th"
does not hold in practice across NIAH variants, LongMemEval, and repeated-word
recall.

When you collaborate with a coding agent across many sessions, this shows up as:

| Symptom | What it looks like |
|---|---|
| Early-context forgetting | Decisions and constraints from the start of the session fade; rejected directions get re-suggested. |
| Retrieval accuracy drop | Finding the right piece of information inside a long input becomes unreliable. |
| Cross-topic interference | Multiple subjects accumulate in one context and bleed into each other. |
| Inconsistency | The model contradicts patterns it established earlier in the same session. |

---

## Existing Approaches and Their Gaps

Several common approaches partially address this. None of them cover the case
where work spans several sessions and branches into multiple follow-ups.

| Approach | What it gives you | Where it falls short |
|---|---|---|
| **Compact** (built-in) | Auto-summarizes when context fills up. | Lossy. You cannot tell what was dropped. Repeated compacts thin out early decisions. State cannot be restored across session boundaries. |
| **HANDOFF.md** | Explicit end-of-session summary. | Overwritten each session, so older history is lost. Reloaded in full at resume → context bloat. No structure for branching follow-up work. |
| **Pre-planned milestones** (e.g. GSD) | Decomposes a large goal into phases up front. | Pre-plan drifts from reality; direction changes force rewriting the whole plan. No built-in handling for context across sessions. |

The common gap: when one finished task spawns *multiple, unrelated follow-ups*,
all of them stay in the same document and pollute every subsequent session.

---

## Checkpoint's Approach

Work is stored as a DAG of nodes on the filesystem. A new session reads
`index.md` and loads only the node it is about to execute plus the Output
Contracts of its direct dependencies.

Three core mechanisms:

1. **Node-level separation.** Completed work is compressed into an Output
   Contract (the result, not the conversation) and stored as a node. Rejected
   options, failed attempts, and intermediate discussion end with the session.
2. **Branching of follow-up work.** `checkpoint-plan` turns "what's left"
   into independent nodes — one per concern — connected by dependencies.
   Whichever branch you pick up next, only its node is loaded.
3. **Hook-recorded evidence + incremental replanning.** `PreCompact` /
   `PostCompact` hooks preserve the pre-compact work flow as a rollup and
   inject a review reminder afterwards. `checkpoint-plan` reads that evidence
   so its node design reflects what actually happened, not what was planned a
   week ago.

### Why it changes the resume cost

Day-by-day comparison for an auth-rollout example (auth-service →
user-service / admin-panel / api-gateway):

| Day | Working on | HANDOFF.md initial context | Checkpoint initial context |
|---|---|---|---|
| Day 1 | auth-service | 0 | 0 |
| Day 2 | user-service | ~5,000 tokens (full prior session) | ~300 tokens (node-b + node-a Output Contract) |
| Day 3 | admin-panel | ~9,500 tokens (Day 1+2 accumulated) | ~500 tokens (node-c + node-a Output Contract) |

Working on admin-panel on Day 3 does not load Day 2's user-service discussion,
because they live in different nodes.

---

## The Six Skills

| Skill | Role |
|---|---|
| `/checkpoint-review` | Diagnose the current session. Decide *continue or save*. Hook-injected after compact; usable manually too. |
| `/checkpoint-save` | Persist completed work as Done nodes with Output Contracts. Conversation noise is discarded. |
| `/checkpoint-plan` | Split remaining work into independent Ready nodes with dependencies. Reads hook evidence so the design reflects reality. |
| `/checkpoint-next` | In a fresh session, pick the next Ready node and load the minimum context. |
| `/checkpoint-audit` | Validate the graph (stale state, broken deps, status conflicts) before resuming after a long pause. |
| `/checkpoint-viz` | Render the graph as an interactive single-file HTML dashboard (DAG, node detail panel, CP-ADR list). |

---

## Hook Automation

Install the hooks and Claude/Codex will tell you when it is time to save —
you don't have to watch token usage yourself.

### How risk is judged

`/checkpoint-review` combines three signals to decide whether the current
session should be closed:

1. **Session length** — accumulated prompt count.
2. **Compact accumulation** — `compact_count` (both auto and manual compacts).
3. **Prompt flow** — the meaningful one.

The prompt-flow signal is what makes the judgment more than a threshold check.
The `UserPromptSubmit` hook appends a small record of each user prompt (hash,
length, lead, tail) to `events.jsonl`. `/checkpoint-review` reads this trail
to detect patterns like:

- **Topic transition** — implementation → debugging → a different feature.
- **Branching** — a side concern was discovered mid-task (e.g. "need to bump
  auth exp to 4h while working on user-service").
- **Repeating loops** — the same area is revisited multiple times.
- **Natural completion** — a task wrapped up cleanly (a good place to cut a
  node).

The decision blends all three signals; raw token usage alone is not the trigger.

### The automation loop

```text
compact happens  →  hooks mark "pending review"  →  next user prompt
              →  Claude/Codex auto-runs /checkpoint-review
              →  if risky, suggests /checkpoint-save
```

Manual `/compact` triggers the same flow — both go through `PreCompact` /
`PostCompact`.

### What hooks write (non-authoritative)

Hooks only record evidence. They do not touch checkpoint graph state.

```text
.checkpoint/sessions/<session_id>/
  session.json
  state.json
  events.jsonl
  rollups/
    001-post-compact.md
```

Graph state under `.checkpoint/graphs/**` is only ever written by
`/checkpoint-save`, `/checkpoint-plan`, `/checkpoint-next`, and
`/checkpoint-audit`.

---

## Lifecycle

```text
active session
  ├─ hooks record events.jsonl / state.json / pre-compact / post-compact
  ├─ on compact: review reminder injected to the next prompt
  │
  └─ /checkpoint-review     decide: continue or save
        │
        ├─ continue
        │
        └─ /checkpoint-save  Done nodes with Output Contracts
              │
              └─ /checkpoint-plan  remaining work split into independent
                    │              Ready nodes (by concern)
                    │
                    └─ /clear

new session
  └─ /checkpoint-next   load: index.md + selected node + deps' Output Contracts
                        (other branches stay unloaded)
```

`/checkpoint-plan` is skippable only when `/checkpoint-save` already produced
clear executable next nodes. If the next session would otherwise need a large
handoff to know what to do, run `/checkpoint-plan` before clearing.

---

## Repository Layout

```text
checkpoint/
├─ README.md                  ← this file
├─ skills/
│  ├─ checkpoint-review/
│  ├─ checkpoint-save/
│  ├─ checkpoint-plan/
│  ├─ checkpoint-next/
│  ├─ checkpoint-audit/
│  └─ checkpoint-viz/
├─ hooks/
│  ├─ checkpoint_session_hook.py
│  └─ requirements.example.toml
├─ scripts/
│  ├─ install-claude.sh
│  └─ install-codex.sh
├─ .claude/                   ← Claude Code integration assets
└─ .codex/                    ← Codex integration assets
```

Graphs and session evidence created during usage:

```text
<project>/.checkpoint/graphs/<slug>/
  index.md
  DECISIONS.md
  nodes/
    N1-...
    N2-...

<project>/.checkpoint/sessions/<session_id>/
  session.json
  state.json
  events.jsonl
  rollups/
    001-post-compact.md
```

---

## File Roles

### `index.md`

Routing and status only. Answers:

- Which nodes exist, and what is their status (`Ready` / `In Progress` /
  `Done` / `Blocked` / `Parked` / `Dropped`).
- Which node should be picked next.
- Which dependencies block what.

Not a context dump.

### `DECISIONS.md`

Checkpoint-local ADRs — durable decisions, rejected directions, do-not-reopen
constraints that span multiple nodes. Does not duplicate project docs.

### `nodes/*.md`

Executable resume units. Each node contains just enough to do that unit of
work, optionally citing relevant entries from `DECISIONS.md`.

---

## Install

Each installer is a single bash script that installs the six skills, the hook
script, and the hook configuration in one step. Re-running is safe — managed
blocks in config files are replaced on each run.

Requirements: bash, `python3` on `PATH`.

**Claude Code:**

```bash
bash scripts/install-claude.sh           # ~/.claude/ (global)
bash scripts/install-claude.sh --local   # ./.claude/ (project-local)
```

**Codex:**

```bash
bash scripts/install-codex.sh            # ~/.codex/
```

After installing, restart the runtime and approve the hook when prompted.

> The skills alone are usable without hooks, but **hooks are strongly
> recommended**. Without them you have to call `/checkpoint-review` yourself
> at the right moment; with them, the runtime auto-runs review after compact
> and proposes `/checkpoint-save` when the session is risky.

### Verifying

After restart:

- `SessionStart` initializes `.checkpoint/sessions/<session_id>/session.json`.
- `UserPromptSubmit` appends to `events.jsonl`.
- `PreCompact` records the compact boundary.
- `PostCompact` records the compact and marks review as pending.
- The next `SessionStart` (`source: "compact"`) or `UserPromptSubmit` injects
  the review reminder via `hookSpecificOutput.additionalContext`.

If `python3` is not on `PATH`, install it first (or use a Python virtualenv
that exposes `python3`). Hook commands are written with `python3` explicitly,
so a `python`-only environment will fail until that name resolves.

---

## Design Principles

- **Don't build better giant handoffs. Make handoffs unnecessary.**
  Resume should mean "read the graph and load the next node," not "load the
  whole previous session."
- **Hooks record. Skills decide.** Hooks write only evidence. Authoritative
  graph state is only ever written by the skills.
- **Result, not conversation.** Output Contracts carry the decision result;
  rejected options and intermediate exploration end with the session.
- **Separate branches, separate nodes.** A finished task with three follow-ups
  becomes three nodes — so working on one never drags in the other two.
