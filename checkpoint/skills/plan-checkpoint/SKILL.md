---
name: plan-checkpoint
description: Create a future-work checkpoint graph for an unresolved task before the work is performed. Use when the user wants to split a large future problem into resumable nodes, create a Context DAG for later execution, park future work, or plan a multi-session continuation. Does not capture current-session artifacts; use save-checkpoint for actual session work.
---

# Plan Checkpoint

Plan a checkpoint graph for future work.

This skill is for work that has not happened yet. If the user wants to preserve actual work from the current or another session, use `save-checkpoint`.

In the checkpoint lifecycle, this prepares the next session after current work has been saved:

```text
save-checkpoint -> plan-checkpoint -> clear/new session -> next-checkpoint
```

Use it when unresolved future work would otherwise require a large handoff or an ambiguous restart prompt.

## Core Contract

Create the smallest graph that makes future execution safe.

Do not summarize a whole project. Do not duplicate existing source-of-truth documents.

## Storage Home Confirmation Gate

Checkpoint graphs live under the current project root:

```text
<project-root>/.checkpoint/graphs/<slug>/
```

Use the project root that contains the active user work, not a temporary clone or helper repo unless that helper repo is explicitly the project.

Before proposing or writing checkpoint graph files, identify the selected graph home. If this is anything other than `<project-root>/.checkpoint/graphs/<slug>/`, ask the user to confirm first.

```text
Graph Home Check
- current project: <path or none>
- selected graph home: <path>
- working repo/context: <path or none>
- existing graph home from index.md: <path or none>
- reason: <why this home was chosen>
- confirmation needed: yes|no
```

If confirmation is not needed, include the chosen graph home in the plan proposal and continue through the normal Interactive Planning Gate.

## Interactive Planning Gate

`plan-checkpoint` is interactive by default.

Before writing or updating checkpoint graph files, present a plan proposal and get user approval.

When reading `Node Candidates` from an existing checkpoint node:

1. list the candidates with their evidence
2. explain whether each candidate should be promoted, merged, parked, dropped, or left inside the source node
3. recommend the smallest graph that makes future execution safe
4. wait for explicit user approval before writing graph files

Do not write or update:

- `index.md`
- `DECISIONS.md`
- `nodes/*.md`

until the user approves the proposed structure.

Explicit approval means the user confirms the proposed structure or gives clear subset/order instructions, such as:

- `승인`
- `이 구조로 진행`
- `N3만 만들고 N4는 보류`
- `두 후보를 하나로 합쳐`

Calling `plan-checkpoint` by itself is not approval to write.

If the user explicitly requests auto mode, such as `auto`, `비대화형`, or `추천안대로 바로 작성`, graph writes are allowed without an approval turn. In that case, state in the final response that auto mode was used.

## Workflow

1. Define the future work objective.
2. Identify canonical entrypoints and files future sessions should read.
3. Identify what must not be read by default.
4. If existing `Node Candidates` are present, prepare a candidate review:
   - promote
   - merge
   - park
   - drop
   - leave as candidate
5. Propose the minimal node split, dependencies, edge meanings, and storage target.
6. Stop for user approval unless auto mode was explicitly requested.
7. After approval, split the work into minimal resume nodes.
8. Add dependencies and edge meanings.
9. Ask only for decisions that affect node scope, ordering, parked work, or storage.
10. Choose storage:
   - default: `<project-root>/.checkpoint/graphs/<slug>/`
   - run the Graph Home Confirmation Gate before writing if choosing any other location
11. Write:
   - `index.md`
   - `DECISIONS.md`
   - `nodes/*.md`
12. Run the state update gate before final response.
13. Run the self-audit gate before final response.
14. Make the next-session entrypoint explicit:
   - identify the recommended first node
   - state what a fresh session should load through `next-checkpoint`
   - keep restart instructions small enough that the graph, not the chat, carries the context

## Edge Meanings

Use explicit edge meanings:

- `depends_on`
- `blocks`
- `verifies`
- `supersedes`
- `parked_until`
- `resumes_after`

## Node Fields

Each node should include:

- Goal
- Why this node exists
- Required context
- Do not read by default
- Inputs/dependencies
- Output contract
- Completion condition
- Risks/blockers

## DECISIONS.md

Use `DECISIONS.md` for graph-wide assumptions and checkpoint-local ADRs.

Include:

- canonical entrypoints
- project/user constraints all nodes share
- chosen graph split rationale
- rejected structures
- parked conditions
- decisions not to reopen

Do not create `shared.md`.

## State Update Gate

Before final response, state one of:

```text
Checkpoint state: updated
```

or:

```text
Checkpoint state: unchanged — <reason>
```

## Self-Audit Gate

After creating the checkpoint graph and before final response, validate it using the `audit-checkpoint` checks.

`plan-checkpoint` owns graph creation. `audit-checkpoint` owns validation. Do not delegate graph writing to audit.

Required checks:

- `index.md` exists and remains routing/status only.
- `DECISIONS.md` exists and contains graph-wide checkpoint-local ADRs.
- no `shared.md` exists.
- every listed node file exists.
- dependency edges reference existing nodes.
- no dependency cycles exist.
- Ready and Blocked statuses match dependencies.
- node output contracts are clear enough for future execution.
- if nodes were created from `Node Candidates`, the graph records explicit user approval or auto mode.
- High and Medium issues introduced by this plan are fixed before final response.
