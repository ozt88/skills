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

## Workflow

1. Define the future work objective.
2. Identify canonical entrypoints and files future sessions should read.
3. Identify what must not be read by default.
4. Split the work into minimal resume nodes.
5. Add dependencies and edge meanings.
6. Ask only for decisions that affect node scope, ordering, parked work, or storage.
7. Choose storage:
   - repo work: `<repo>/.checkpoint/graphs/<slug>/`
   - global work: `C:\Users\DELL\.codex\.checkpoint\graphs\<slug>\`
8. Write:
   - `index.md`
   - `DECISIONS.md`
   - `nodes/*.md`
9. Run the state update gate before final response.
10. Run the self-audit gate before final response.
11. Make the next-session entrypoint explicit:
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
- High and Medium issues introduced by this plan are fixed before final response.
