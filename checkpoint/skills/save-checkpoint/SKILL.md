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

## Strict Boundary

`save-checkpoint` captures already-performed work. It must not design new future execution nodes just because a next action is visible.

Allowed:

- finalize or update nodes for work that was actually performed
- mark the active node `Done`, `In Progress`, `Blocked`, `Dropped`, `Superseded`, or `Split`
- expose node candidates for work that was started but is not yet ready to become a formal node
- record unresolved future work as `Next action`, `Remaining risks`, `Blockers`, or a `plan-checkpoint needed` note
- unlock existing nodes whose dependencies are now satisfied

Forbidden:

- create new nodes for work that has not started
- convert every remaining risk into a future node
- set `Recommended Next` to a newly invented future node
- treat `save-checkpoint` as a substitute for `plan-checkpoint`

If future work needs node design, write a small handoff note:

```text
plan-checkpoint needed: <future work that requires graph design>
```

Then stop. Do not create that future graph inside `save-checkpoint`.

## Candidate Exposure Inside Existing Nodes

Some work is not future-only. A long session may start several threads before they are complete enough to become clean checkpoint nodes.

`save-checkpoint` must expose these candidates inside an existing node instead of hiding them.

Use `Node Candidates` inside the active node's `Progress Snapshot` or `Output Contract` when work is:

- actually started in the saved session
- mentioned repeatedly or materially changed by the session
- blocked, partial, or ambiguous
- likely to become a node if the user later runs `plan-checkpoint`
- too under-specified to safely mark as `Ready`, `Done`, or `In Progress`

Candidate entries are not canonical node state and must not appear as rows in graph `index.md`. They are a shortlist for future `plan-checkpoint`.

Format:

```md
### Node Candidates
- candidate: <short slug>
  evidence: <what was actually touched or decided>
  why not a node yet: <missing scope, unclear output, user decision needed, or no work performed>
  suggested next step: continue | ask user | plan-checkpoint
```

Do not add candidates for merely imagined future work. If no work was started, use `plan-checkpoint needed` instead.

`plan-checkpoint` may later read these candidates and create new nodes from them. `save-checkpoint` must not create those nodes.

## Storage Home Confirmation Gate

Checkpoint graphs live under the current project root:

```text
<project-root>/.checkpoint/graphs/<slug>/
```

Use the project root that contains the active user work, not a temporary clone or helper repo unless that helper repo is explicitly the project.

Before writing checkpoint graph files, identify the selected graph home. If this is anything other than `<project-root>/.checkpoint/graphs/<slug>/`, ask the user to confirm first.

Print a short check when the location could be confused:

```text
Graph Home Check
- current project: <path or none>
- selected graph home: <path>
- working repo/context: <path or none>
- existing graph home from index.md: <path or none>
- reason: <why this home was chosen>
- confirmation needed: yes|no
```

If confirmation is not needed, continue and include the chosen graph home in the final response.

## Archive Closed Graphs

Active checkpoint graphs live in:

```text
<project-root>/.checkpoint/graphs/<slug>/
```

When `save-checkpoint` determines that a graph has no remaining executable work, move the whole graph folder to:

```text
<project-root>/.checkpoint/archive/graphs/<slug>/
```

Do not require a separate `Completed` status in `index.md`. Archive location is the completion signal.

Archive a graph when:

- no `Ready`, `In Progress`, or meaningfully `Blocked` node remains
- `Recommended Next` is absent or no longer executable
- remaining work was completed, dropped, or superseded by another graph

After archiving, `next-checkpoint` should no longer treat the graph as a normal resume candidate.

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
- node candidates for partial work
- optional session-local rollups from `.checkpoint/sessions/<session_id>/`

Exclude:

- full transcript summaries
- reasoning traces
- stale brainstorming
- completed details that do not affect future work
- duplicated source-of-truth content

`pending work` and `next actions` are captured as handoff facts, not automatically as new checkpoint nodes.

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
   - node candidates created by started-but-unfinished work
   - session-local rollups if present
4. Map source-of-truth:
   - link existing entrypoints instead of copying them
   - preserve canonical sources as links/paths
   - preserve decisions as checkpoint-local ADRs in `DECISIONS.md`
5. Build or update checkpoint graph:
   - default: `<project-root>/.checkpoint/graphs/<slug>/`
   - run the Graph Home Confirmation Gate before writing if choosing any other location
6. Write:
   - `index.md` for routing and canonical node state
   - `DECISIONS.md` for checkpoint-local ADRs, entrypoints, rejected directions, and completed-do-not-reopen decisions
   - `nodes/*.md` for resumable work units only
7. State update gate:
   - update `index.md` before final response
   - mark complete, ready, blocked, parked, superseded, or dropped nodes
   - write a progress snapshot when work is not complete
   - do not add future-only nodes unless they represent work already started in this session
   - if no executable work remains, archive the graph folder under `.checkpoint/archive/graphs/`
8. Self-audit gate:
   - run the `audit-checkpoint` checklist against the updated graph
   - fix High and Medium issues introduced by this save
   - report remaining Low issues if they are intentionally deferred
9. End-of-session handoff:
   - state whether `plan-checkpoint` is needed before clearing
   - if existing next executable nodes are already clear, say `plan-checkpoint` may be skipped
   - if the graph was archived, say `next-checkpoint` will not select it by default
   - if the next work is only a future intention and no existing node represents it, say `plan-checkpoint` is needed instead of creating the node
   - if started-but-unfinished work exists but is not ready to formalize, list it inside the relevant existing node under `Node Candidates`
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

Do not add brand-new future nodes during this update unless the current session already performed partial work for that node and needs a progress snapshot.

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

Do not create nodes for unstarted future work in `save-checkpoint`. Put that future work in:

- `Remaining risks`
- `Next action`
- `Blockers`
- `plan-checkpoint needed`

Use `plan-checkpoint` later if the future work should become a graph.

For started-but-unfinished work, do not hide it. Put it inside an existing node's `Node Candidates` section unless it is already clear enough to become an `In Progress` node with a `Progress Snapshot`.

`Node Candidates` is an input to future `plan-checkpoint`, not a node creation mechanism inside `save-checkpoint`.

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
- Newly added nodes must correspond to work already performed or partially performed in the saved session.
- Future-only work must be recorded as a handoff fact, not as a node.
- Started-but-unfinished work that was not made a node must be visible inside an existing node's `Node Candidates` section or `Progress Snapshot`.
- `Node Candidates` must not create rows in graph `index.md`.
- High and Medium issues introduced by this save are fixed before final response.
