# Checkpoint graph format

## Contents
- Location and archive
- index.md (Conductor and Delegations)
- Status values and edges
- Node files
- DECISIONS.md
- Checks

## Location and archive

```text
<project-root>/.checkpoint/graphs/<slug>/
  index.md        routing and status
  DECISIONS.md    graph-wide decisions
  nodes/          one file per node
  artifacts/      optional supporting files
```

`<project-root>` is the repository or directory that holds the user's work, not a helper clone or a temporary directory. Before writing anywhere else, or when an existing `index.md` names a different home, ask the user.

A graph with no executable node left moves as a whole to `<project-root>/.checkpoint/archive/graphs/<slug>/`. The location is the completion signal. `next` skips archived graphs unless the user asks for one.

An active graph is stale when it still has open nodes and index.md has not changed for 30 days, whether or not a node is In Progress (a node left In Progress that long is usually abandoned). Stale graphs are offered for Parked (with a `parked_until` condition) or for the archive; nothing moves without the user's yes.

If the project is a git repository and `.checkpoint/` is not ignored, mention it once. Do not edit `.gitignore` without asking.

## index.md

Routing and status only. Context belongs in nodes and DECISIONS.md.

```md
# <graph title>

## Nodes
| Node | Status | Edges | Summary |
|---|---|---|---|
| [N1-player-ban-bitset](nodes/N1-player-ban-bitset.md) | Done | — | one line |
| [N2-console-integration](nodes/N2-console-integration.md) | Ready | depends_on N1 | one line |

## Recommended Next
N2 — one line on why.
```

Graphs made with other column layouts (an `ID` column, a `Depends on` column) stay valid. Keep a graph's existing layout when editing it.

### Conductor and Delegations

A graph in conductor mode ([conductor.md](conductor.md)) has two more sections after `## Nodes`:

```md
## Conductor
Mode: conductor (session: UT prep [4f2a1c], since 2026-11-12)
Goal: one line
Next action: one line

## Delegations
| ID | Owner | Task | Brief | Holds | State |
|---|---|---|---|---|---|
| D1 | agent: log-scan | find why matching fails | artifacts/D1-brief.md | — | Running |
| N3 | chip: deploy-dev | deploy the fix to dev | nodes/N3-deploy-dev.md | dev env | Review |
```

- State is one of Running, Waiting (ready, waiting for a resource), Review, Rework. A resolved row is deleted.
- Owner is `agent: <name>`, `chip: <title>` or `handoff: <project>`. A node handed to a work session also carries its owner in the status cell: `In Progress (chip: deploy-dev)`.
- In conductor mode only the conductor writes `index.md`. Work sessions write their own node or result file and report; when two sessions write `index.md`, the later write silently drops the other's change.
- A graph with a `## Conductor` section is not archived for having no executable node, since delegations may still be running.

## Status values and edges

| Status | Meaning | Executable |
|---|---|---|
| Ready | every `depends_on` node is Done | yes |
| In Progress | started; the node has a Progress Snapshot | yes |
| Blocked | waiting on a dependency or event named in Edges | when unblocked |
| Parked | deferred until a `parked_until` condition | when triggered |
| Done | finished; the node has an Output Contract | no |
| Handed off | someone else owns the rest; the node says who and what | no |
| Superseded | replaced; name the replacement | no |
| Dropped | abandoned; say why | no |
| Split, Merged | became other nodes; name them | no |

The cell starts with one of these words. A date or short qualifier may follow in parentheses: `Done (2026-09-10)`, `In Progress (partial)`.

A Handed off dependency does not make a node Ready: its output is not there yet. When a dependency is Superseded, Split, or Merged, point the edge at the node that replaced it.

Edges: `depends_on`, `blocks`, `verifies`, `supersedes`, `parked_until <condition>`, `resumes_after`.

## Node files

A node is one focused session of work with a checkable result. Name it by the work (`player-ban-bitset`), never by an area (`docs`, `misc`). File name: `nodes/<id>-<slug>.md`.

```md
# N2 · <title>

## Goal
## Required context
Files and CP-ADRs to read before starting.
## Do not read by default
## Completion condition

## Progress Snapshot
- Done so far:
- Stopping point:
- Next action:
- Blockers and risks:

## Output Contract
- Decisions:
- Files changed:
- Validation:
- Unlocks:
- Remaining risks:
```

- Progress Snapshot exists while the node is not Done. It holds the current state only. Replace it whole on every save; never append rounds ("1차, 2차", dated entries). A decision a round produced moves to the Output Contract or DECISIONS.md; the rest is dropped. Stopping point and Next action are one line each — they are read at a glance (the band and pane show them on one line).
- Output Contract is required when the node is Done. Write the result the next session builds on, not the story of how it was reached.
- A `Status:` line in a node file is optional and must match `index.md`.

Work started in a session but not shaped enough to be a node goes into the active node as candidates. Candidates never become `index.md` rows until `plan` promotes them.

```md
### Node Candidates
- candidate: <slug>
  evidence: <what was actually touched or decided>
  why not a node: <missing scope | needs a user decision | ...>
```

## DECISIONS.md

Decisions that apply beyond one node, as checkpoint-local ADRs. Canonical entrypoints (files, docs) may be listed at the top. Link to existing documents instead of copying them.

```md
## CP-ADR-001: <title>
Status: Accepted | Superseded | Rejected
Applies to: all | N1, N2
Decision: ...
Why: ...
Do not reopen: ... unless new evidence appears.
```

## Checks

Run from this skill's directory:

```bash
python3 scripts/check_graph.py <graph-dir>
```

It reports missing files, rows listed twice, unknown status words, missing or empty Output Contract or Progress Snapshot sections, status lines that disagree with `index.md`, unknown or cyclic dependencies, Ready nodes whose dependencies are not Done, unlisted node files, Progress Snapshots that grew past the current state (too long, or kept as rounds), stale graphs, and graphs that should be archived (conductor graphs excepted).

`python3 scripts/check_graph.py --all <project-root>` checks every active graph of a project and ends with the graphs to archive and to park.

Then check by reading:
- `index.md` holds routing, not paragraphs of context.
- Each Output Contract is specific enough for the next session to build on.
- The graph's scope matches the current repository and the newest user request.

Severity: High means resuming is unsafe or likely to cause wrong work. Medium means stale but repairable. Low means cleanup.
