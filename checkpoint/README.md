# Checkpoint

Checkpoint is a context management workflow for long-running AI work sessions.

It has two jobs:

1. Review context rot inside an active session and suggest `save-checkpoint` before the session becomes unsafe.
2. Replace oversized handoff documents with a checkpoint graph that can split work, track blockers, and return to the real problem when blockers are resolved.
3. Keep a lightweight session-local evidence trail so compacted sessions can be reviewed without turning logs into another giant handoff.

## Primary Lifecycle

Checkpoint is designed around a session boundary.

The default lifecycle is:

```text
active session
  -> hooks record lightweight session evidence
  -> PostCompact automatically invokes review-checkpoint
  -> review-checkpoint reviews context rot or task drift
  -> save-checkpoint captures the current session and closes the active work state
  -> plan-checkpoint prepares the next-session graph when future work is not already explicit
  -> clear the current chat or start a new session
  -> next-checkpoint loads the next executable node with minimal context
```

In other words:

- hooks record evidence; they do not write checkpoint graphs.
- `PostCompact` is the automatic review boundary.
- `review-checkpoint` summarizes the compacted segment and asks whether to continue or save.
- `save-checkpoint` is how a full or risky session is safely ended.
- `plan-checkpoint` is how unresolved future work is shaped before the next session starts.
- `next-checkpoint` is what a fresh session uses after clear/resume to choose what to execute.

`plan-checkpoint` can be skipped only when `save-checkpoint` already produced clear executable next nodes. If the next session would otherwise need a large handoff to know what to do, run `plan-checkpoint` before clearing.

## Install

Checkpoint has two install surfaces:

1. Skills: copied into the Codex skills root.
2. Hooks: copied into the target repository so Codex can discover `.codex/hooks.json`.

### Install Skills

Copy each skill directory into your Codex skills root:

```text
~/.codex/skills/review-checkpoint/
~/.codex/skills/save-checkpoint/
~/.codex/skills/plan-checkpoint/
~/.codex/skills/next-checkpoint/
~/.codex/skills/audit-checkpoint/
```

Example from a cloned `checkpoint` repo:

```bash
mkdir -p ~/.codex/skills
cp -R skills/review-checkpoint ~/.codex/skills/
cp -R skills/save-checkpoint ~/.codex/skills/
cp -R skills/plan-checkpoint ~/.codex/skills/
cp -R skills/next-checkpoint ~/.codex/skills/
cp -R skills/audit-checkpoint ~/.codex/skills/
```

### Install Hooks

Hooks are repo-local. Copy `.codex/` into each repository where you want checkpoint session logging:

```bash
cp -R .codex /path/to/target-repo/
```

Then open that target repository in Codex and run:

```text
/hooks
```

Review and trust the hook definitions before expecting them to run. Codex discovers repo-local hooks from `<repo>/.codex/hooks.json`.

### Windows Notes

The included hook config has `commandWindows` entries that run the Python hook through the target repo root. Python must be available as `python`.

If your environment uses `py -3` instead, edit `.codex/hooks.json` in the target repo and replace the `commandWindows` launcher accordingly.

### Verify Hook Installation

After trust is granted:

- `SessionStart` should initialize `.checkpoint/sessions/<session_id>/session.json`.
- `UserPromptSubmit` should append prompt evidence to `.checkpoint/sessions/<session_id>/events.jsonl`.
- `PostCompact` should append a compact event and return a review signal for `review-checkpoint`.

The hook never writes `.checkpoint/graphs/**` and never runs `save-checkpoint` automatically.

## The First Problem: Context Rot Inside A Session

Long AI sessions fail in two common ways:

- too much context accumulates inside one session
- the user suddenly switches to a different problem before the current state is safely captured

Checkpoint treats both as context-rot signals.

The `review-checkpoint` skill reviews context usage, unresolved decisions, stale branches, task switching, and state that exists only in chat. It can run manually when the user suspects context drift, or automatically after compact. When the session is getting unsafe, it should point out the problem and ask whether to save the current work:

```text
Continue in this session, or save the current work with save-checkpoint first?
```

The review is not meant to interrupt every long conversation. It is meant to catch the moment when continuing would make future resume depend on an oversized or polluted memory of the session.

## Session-Local Evidence Layer

Checkpoint can use hooks as a recording layer, not as an automation engine.

Hooks should write only lightweight session-local evidence:

```text
.checkpoint/sessions/<session_id>/
  session.json
  events.jsonl
  rollups/
    001-post-compact.md
```

This layer is non-authoritative. It is allowed to help `review-checkpoint` and `save-checkpoint`, but it must not update checkpoint graph state.

Recommended hook behavior:

```text
SessionStart
  -> initialize session.json
  -> append session_start source: startup/resume/clear/compact

UserPromptSubmit
  -> append hash, length, lead, tail, timestamp

PostCompact
  -> record compact trigger/count
  -> invoke review-checkpoint automatically

review-checkpoint
  -> summarize the just-compacted request flow
  -> write a session-local rollup when possible
  -> explain possible drift or handoff risk
  -> ask whether to continue or run save-checkpoint
```

Do not store full prompts, full transcripts, full tool outputs, or full diffs. Do not classify topic drift inside hooks. `review-checkpoint` may interpret the flow; hooks should only record evidence.

## The Second Problem: Handoff Becomes The New Context Rot

The core problem is not that handoff notes are too weak. The problem is that handoff notes become too large, while still missing important context.

As work continues across many sessions, a handoff tends to accumulate everything:

- current decisions
- old decisions
- rejected directions
- pending work
- blockers
- modified files
- validation notes
- user preferences
- warnings for the next session

At first this prevents context loss. Later it becomes a new source of context pollution. Each resume loads the whole handoff again, including stale decisions, completed work, rejected paths, and background that is no longer active. The next session starts with too much context, not too little, and the model has to infer which parts still matter.

Checkpoint replaces the growing handoff document with a small executable graph. Work can be split into nodes, blockers can be represented explicitly, and once blockers are resolved the next session can return to the real problem without loading every previous side path.

## Goal

Resume should not mean "load the whole previous session."

Resume should mean:

1. Read the graph status.
2. Select the next executable node.
3. Load only the decisions relevant to that node.
4. Execute or update that node.

The goal is to preserve continuity without re-injecting all old context into every future session.

## Repository Shape

```text
.checkpoint/graphs/<slug>/
  index.md
  DECISIONS.md
  nodes/
    N1-...
    N2-...

.checkpoint/sessions/<session_id>/
  session.json
  events.jsonl
  rollups/
    001-post-compact.md
```

This repository also includes the Codex skills that implement the workflow:

```text
skills/
  review-checkpoint/
  save-checkpoint/
  plan-checkpoint/
  next-checkpoint/
  audit-checkpoint/
```

The repository also includes repo-local Codex hooks:

```text
.codex/hooks.json
.codex/hooks/checkpoint_session_hook.py
```

Codex discovers repo-local hooks from `<repo>/.codex/hooks.json`. Review and trust the hook definition with `/hooks` before expecting it to run. The hook writes session-local evidence and emits a `PostCompact` review signal; it does not execute `save-checkpoint` or write graph state.

Current Codex command hooks cannot directly call a skill as an API. The `PostCompact` hook records the compact event and returns a `systemMessage` instructing the active agent to invoke `review-checkpoint` before continuing.

## File Roles

### `index.md`

Routing and status only.

It answers:

- Which nodes exist?
- Which nodes are `Ready`, `In Progress`, `Done`, `Blocked`, `Parked`, or `Dropped`?
- Which node should be considered next?
- Which dependencies block execution?

It should not become a context dump.

### `DECISIONS.md`

Checkpoint-local ADRs.

It records durable decisions, rejected directions, and do-not-reopen constraints that affect more than one node.

It should not copy project documentation. It exists so a future session can load only the decisions relevant to the selected node.

### `nodes/*.md`

Executable resume units.

Each node should contain enough context to execute that unit, but not the entire graph. A node can cite relevant decisions from `DECISIONS.md`.

## Skills

### `review-checkpoint`

Session boundary review.

It is automatically invoked after `PostCompact` and can also be called manually. It reviews compacted, long, or drifting sessions and explains whether continuing may cause context loss or context pollution. It should only offer:

- continue in the current session
- save current work with `save-checkpoint`

It may write session-local rollups under `.checkpoint/sessions/<session_id>/`, but it should not automatically route to planning, opening, auditing, or authoritative graph writes.

### `save-checkpoint`

Captures actual current-session work.

It records changed artifacts, decisions, blockers, rejected directions, validation state, and next actions. It may consult session-local evidence and rollups, but it writes the authoritative graph state. It also updates node status after work has been performed.

### `plan-checkpoint`

Creates a checkpoint graph for future work that has not been executed yet.

It must not pretend to capture current-session artifacts.

### `next-checkpoint`

Selects the next executable node from an existing graph.

It reads `index.md` first, then only the relevant `DECISIONS.md` entries and the selected node.

### `audit-checkpoint`

Validates checkpoint structure and freshness.

It checks stale state, missing files, invalid dependencies, status conflicts, oversized context, and conflict with current user intent or local filesystem state.

## Why Graph, Not Handoff?

A handoff is a narrative summary.

A checkpoint graph is a state model.

Handoff answers:

```text
What happened before?
```

Checkpoint answers:

```text
What is executable now?
What is done?
What is blocked?
What should not be loaded unless needed?
```

This matters because long-running work does not only need memory. It needs selective loading.

## Review Trigger Philosophy

The review should not trigger because "a lot happened."

It should trigger when failing to checkpoint would force a future session to reconstruct state from a large, polluted handoff.

Good trigger candidates:

- session usage is near a high-water mark such as 80%
- auto-compact, resume, or context loss risk is explicit
- the user switches tasks before the current state is file-backed
- global behavior rules, skills, or setting structure changed
- important decisions, rejected directions, or next actions exist only in chat
- a future session would struggle to reconstruct what is current, stale, done, or blocked

Poor trigger candidates by themselves:

- raw file count
- a TODO line was added
- a report was created and already saved
- the user merely said "context" or "checkpoint"
- the user asked a natural follow-up in the same active problem

## Design Principle

Do not make better giant handoffs.

Make handoffs unnecessary for normal resume.

Use a graph so future sessions can load the smallest correct context.
