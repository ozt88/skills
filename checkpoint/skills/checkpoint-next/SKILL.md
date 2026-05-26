---
name: checkpoint-next
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

## Storage Home Confirmation Gate

Checkpoint graphs live under the current project root:

```text
<project-root>/.checkpoint/graphs/<slug>/
```

Use the project root that contains the active user work, not a temporary clone or helper repo unless that helper repo is explicitly the project.

Before activating a checkpoint graph, identify the selected graph home. If this is anything other than `<project-root>/.checkpoint/graphs/<slug>/`, ask the user to confirm first.

```text
Graph Home Check
- current project: <path or none>
- selected graph home: <path>
- working repo/context: <path or none>
- existing graph home from index.md: <path or none>
- reason: <why this home was chosen>
- confirmation needed: yes|no
```

If confirmation is not needed, activate the graph and include the chosen graph home in the response.

## Active Graph Set

By default, search only active graphs under:

```text
<project-root>/.checkpoint/graphs/
```

Archived graphs under `.checkpoint/archive/graphs/` are historical. Do not select them unless the user explicitly asks to inspect or restore an archived graph.

## Workflow

1. Locate checkpoint graph.
2. Read `index.md` first.
3. Run the Graph Home Confirmation Gate before activating it.
4. Exclude archived graphs unless explicitly requested.
5. Verify the newest user request against checkpoint status.
6. Exclude:
   - Done nodes
   - Blocked nodes with unmet dependencies
   - Parked nodes whose trigger is not met
   - Superseded or dropped nodes
7. Select next node:
   - use `Recommended Next` if valid and user asked for it
   - otherwise rank ready nodes by request match, unlock value, context cost, risk reduction, and freshness
8. If multiple plausible nodes remain, ask the user to choose.
9. Read only:
   - relevant `index.md` status
   - relevant `DECISIONS.md` CP-ADR entries
   - selected node file
   - direct dependency output contracts if required
10. Surface the selected node context to the active session.
11. Update state if selection/progress changes.

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
- ask for confirmation when the graph home is ambiguous or surprising
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
