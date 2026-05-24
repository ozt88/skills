---
name: save-checkpoint
description: Save the actual work products of the current or existing session into a resumable checkpoint graph. Use when review-checkpoint recommends closing the session, context is getting too large, the user wants to preserve current work, or a session must hand off without losing changed files, decisions, blockers, rejected directions, and next actions. Inventories artifacts before designing nodes and updates checkpoint state before final response.
---

# Save Checkpoint

Save the current session's actual work into a checkpoint graph.

This skill is for work that already happened. It is not for planning a future task from scratch.

In the checkpoint lifecycle, this is the session-closing step:

```text
active session -> save-checkpoint -> plan-checkpoint when needed -> clear/new session -> next-checkpoint
```

After saving, do not keep expanding the same bloated session unless the user explicitly chooses to continue.

## Core Contract

Do not invent a new graph structure until you have inventoried the session outputs.

Capture:

- changed files
- created files
- deleted or moved files
- durable decisions
- rejected directions
- blockers
- pending work
- validation already run
- next actions
- optional session-local rollups from `.checkpoint/sessions/<session_id>/`

Exclude:

- full transcript summaries
- reasoning traces
- stale brainstorming
- completed details that do not affect future work
- duplicated source-of-truth content

## Workflow

1. Define scope:
   - current session or specified session
   - repo/project or global Codex work
   - checkpoint slug
2. Inventory artifacts before node design:
   - use git status when available
   - list new/modified/deleted files relevant to the session
   - identify reports, TODOs, knowledge updates, generated outputs, and removed artifacts
3. Inventory decisions:
   - durable decisions
   - decisions not to reopen
   - rejected tool/structure directions
   - unresolved assumptions or blockers
   - session-local rollups if present
4. Map source-of-truth:
   - link existing entrypoints instead of copying them
   - preserve canonical sources as links/paths
   - preserve decisions as checkpoint-local ADRs in `DECISIONS.md`
5. Build or update checkpoint graph:
   - repo work: `<repo>/.checkpoint/graphs/<slug>/`
   - global work: `C:\Users\DELL\.codex\.checkpoint\graphs\<slug>\`
6. Write:
   - `index.md` for routing and canonical node state
   - `DECISIONS.md` for checkpoint-local ADRs, entrypoints, rejected directions, and completed-do-not-reopen decisions
   - `nodes/*.md` for resumable work units only
7. State update gate:
   - update `index.md` before final response
   - mark complete, ready, blocked, parked, superseded, or dropped nodes
   - write a progress snapshot when work is not complete
8. Self-audit gate:
   - run the `audit-checkpoint` checklist against the updated graph
   - fix High and Medium issues introduced by this save
   - report remaining Low issues if they are intentionally deferred
9. End-of-session handoff:
   - state whether `plan-checkpoint` is needed before clearing
   - if next executable nodes are already clear, say `plan-checkpoint` may be skipped
   - tell the user the next fresh session should use `next-checkpoint`

## Existing Checkpoint Update

If this session started from an existing checkpoint node, `save-checkpoint` also finalizes that node's state.

1. Identify the checkpoint path and active node.
2. Decide node state:
   - `Done`
   - `In Progress`
   - `Blocked`
   - `Split`
   - `Dropped`
   - `Superseded`
   - `Merged`
3. Update `index.md`; it is the canonical source for node status.
4. Update `DECISIONS.md` if graph-wide decisions, rejected directions, or do-not-reopen rules changed.
5. Write an `Output Contract` when the node is `Done`.
6. Write a `Progress Snapshot` when the node is not `Done`.
7. Unlock newly ready nodes whose dependencies are now done.

### Output Contract

Required when marking a node `Done`:

```md
## Output Contract
- Decisions produced:
- Files changed:
- Validation:
- Unlocks:
- Remaining risks:
```

### Progress Snapshot

Required when a node is not `Done`:

```md
## Progress Snapshot
- Partial work completed:
- Current stopping point:
- Next action:
- Blockers:
- Risks:
```

## Node Design

Nodes must be resume units, not document areas.

Good:

- `setting-index-single-entry`
- `root-context-consolidation`
- `checkpoint-skill-renaming`

Bad:

- `docs`
- `settings`
- `misc followup`

Do not create nodes for completed work unless they are needed as dependencies. Put completed decisions in `DECISIONS.md`.

## DECISIONS.md Format

Use checkpoint-local ADR entries:

```md
## CP-ADR-001: Decision title

Status: Accepted | Superseded | Rejected
Applies to: all nodes | N1,N2
Source: path/to/source.md

### Context
Why this mattered in the captured session.

### Decision
What was decided.

### Consequences
What future sessions must do or avoid.

### Do Not Reopen
What should not be relitigated unless new evidence appears.
```

## State Update Gate

Before final response, state one of:

```text
Checkpoint state: updated
```

or:

```text
Checkpoint state: unchanged — <reason>
```

Do not claim the checkpoint is saved if `index.md`, `DECISIONS.md`, and relevant node files were not written or updated.

## Self-Audit Gate

After writing checkpoint files and before final response, validate the updated graph using the `audit-checkpoint` checks.

`save-checkpoint` owns writes. `audit-checkpoint` owns validation. Do not delegate state writing to audit.

Required checks:

- `index.md` exists and remains routing/status only.
- `DECISIONS.md` exists and remains decision-oriented.
- no `shared.md` exists.
- every node listed in `index.md` exists unless explicitly tiny/parked.
- Ready and Blocked statuses match dependencies.
- Done nodes have an `Output Contract`.
- In Progress nodes have a `Progress Snapshot`.
- High and Medium issues introduced by this save are fixed before final response.
