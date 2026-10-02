# Checkpoint graph format

## Contents
- Location and archive
- index.md
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

## Status values and edges

| Status | Meaning | Executable |
|---|---|---|
| Ready | dependencies met | yes |
| In Progress | started; the node has a Progress Snapshot | yes |
| Blocked | waiting on a dependency or event named in Edges | when unblocked |
| Parked | deferred until a `parked_until` condition | when triggered |
| Done | finished; the node has an Output Contract | no |
| Handed off | someone else owns the rest; the node says who and what | no |
| Superseded | replaced; name the replacement | no |
| Dropped | abandoned; say why | no |
| Split, Merged | became other nodes; name them | no |

The cell starts with one of these words. A date or short qualifier may follow in parentheses: `Done (2026-09-10)`, `In Progress (partial)`.

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

- Progress Snapshot exists while the node is not Done. Rewrite it in place; do not append dated logs above it.
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

It reports missing files, unknown status words, missing Output Contract or Progress Snapshot sections, status lines that disagree with `index.md`, unknown or cyclic dependencies, Ready nodes with unfinished dependencies, unlisted node files, and graphs that should be archived.

Then check by reading:
- `index.md` holds routing, not paragraphs of context.
- Each Output Contract is specific enough for the next session to build on.
- The graph's scope matches the current repository and the newest user request.

Severity: High means resuming is unsafe or likely to cause wrong work. Medium means stale but repairable. Low means cleanup.
