---
name: next-checkpoint
description: Find and activate the next executable checkpoint node from an existing checkpoint graph. Use when the user asks what checkpoint is next, continue from checkpoint, open checkpoint, resume checkpoint work, choose a ready node, or load checkpoint context. Reads index.md first, then DECISIONS.md and one selected node by default. Updates checkpoint state when node selection or progress changes.
---

# Next Checkpoint

Find the next executable checkpoint node and pass the minimal context needed to continue.

This skill opens existing checkpoint graphs. It does not create future plans from scratch; use `plan-checkpoint` for that. It does not package a full session's work products; use `save-checkpoint` for that.

In the checkpoint lifecycle, this is the fresh-session entrypoint after the previous chat was cleared or a new session was started:

```text
save-checkpoint -> plan-checkpoint when needed -> clear/new session -> next-checkpoint
```

Do not load the old handoff or full prior conversation by default. The graph is the resume surface.

## Storage Home Guard

Do not activate checkpoint graphs from transient storage as authoritative state.

Transient storage includes:

- `.tmp/`
- `tmp/`
- throwaway clones
- downloaded archives
- temporary worktrees created only to publish or inspect another repository

If a matching graph is found under a transient path:

1. report that the graph home is not durable
2. look for a durable copy under `C:\Users\DELL\.codex\.checkpoint\graphs\` or a durable repo-local `.checkpoint/graphs/`
3. activate the durable copy if one exists
4. if no durable copy exists, stop and ask whether to migrate it before continuing

Use transient clone paths only as working repo context inside a selected node, not as the graph home.

## Workflow

1. Locate checkpoint graph.
2. Read `index.md` first.
3. Verify the graph home is durable before activating it.
4. Verify the newest user request against checkpoint status.
5. Exclude:
   - Done nodes
   - Blocked nodes with unmet dependencies
   - Parked nodes whose trigger is not met
   - Superseded or dropped nodes
6. Select next node:
   - use `Recommended Next` if valid and user asked for it
   - otherwise rank ready nodes by request match, unlock value, context cost, risk reduction, and freshness
7. If multiple plausible nodes remain, ask the user to choose.
8. Read only:
   - relevant `index.md` status
   - relevant `DECISIONS.md` CP-ADR entries
   - selected node file
   - direct dependency output contracts if required
9. Surface the selected node context to the active session.
10. Update state if selection/progress changes.

## Candidate Display

Show at most five ready candidates:

```text
진행 가능한 checkpoint node가 여러 개 있습니다.

1. N1 - setting-index-single-entry (Small, unlocks N3)
2. N2 - root-context-consolidation (Medium, reduces stale-context risk)

추천: N1. 가장 작고 후속 작업을 unlock합니다.
```

## Staleness Guard

Treat checkpoints as possibly stale.

Before acting:

- prefer the newest user message over saved state
- verify relevant files and artifacts exist
- reject transient graph homes unless the user explicitly asks to inspect that stale copy
- stop and explain conflicts between checkpoint state and local state

## State Update Gate

Before final response, state one of:

```text
Checkpoint state: updated
```

or:

```text
Checkpoint state: unchanged — <reason>
```
