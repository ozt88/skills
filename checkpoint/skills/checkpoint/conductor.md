# Conductor mode

A graph whose `index.md` has a `## Conductor` section is run by one conductor session. The conductor keeps the context; work sessions do the work. The point is to keep the conductor's context free of files, diffs and logs, so it can hold the user's goals and decisions for a long time.

## What the conductor does

- talks with the user and takes decisions
- keeps `index.md` current: node status, `## Conductor`, `## Delegations`
- writes briefs for work sessions, with the criteria the result is judged by
- reads result summaries, judges them, and decides what comes next

Everything else is delegated, small lookups and edits included: research, comparing files, implementation, tests, builds, deploys, merges, pushes, and writing documents. Doing it here only when the user says to do it in this session.

## Choosing a work session

| Work | Send it to |
|---|---|
| finishes within this session's permissions | a background subagent |
| the user will watch it or approve steps | a chip (spawn_task) |
| belongs to another project folder | a handoff file in the scratchpad, plus the command the user runs in a session there |

A chip starts in its own worktree, where `.checkpoint/` (usually gitignored) does not exist. Give it absolute paths into the main checkout for the graph, the brief and the result file, and treat merging its branch as a shared-resource step.

## Runtimes

Checkpoint runs in Claude Code and Codex, and conductor mode depends on what the runtime offers. Check which one this session runs in before choosing a work session.

| | Claude Code (desktop app) | Codex |
|---|---|---|
| Chips (spawn_task) | yes | no |
| Messages between sessions (`ListAgents`, `SendMessage`) | yes | no |
| Background subagents | yes | only if this Codex version offers them |
| Conductor address | `<name> [<ref>]` from `ListAgents` | a name the user gives |

In Codex, use subagents where available. Otherwise write a brief file and give the user the command to start a new Codex session on it; that session reports through its result file, and the user tells the conductor it finished. Say this once at `init`, so the user knows reports will come through them.

Two subagents writing to the same repository at once conflict; assign the working tree like any other shared resource.

## Brief

Each delegation gets a row in `## Delegations` and a brief: the node file for a node, otherwise `artifacts/D<n>-brief.md`. A brief has:

- **Goal**: one or two lines.
- **Known facts**: what the conductor has confirmed, with where (`file:line`, command, link), so the work session does not search again.
- **Do not**: out-of-scope work, and shared resources it must not touch.
- **Criteria**: two to five checkable statements derived from the user's goals and DECISIONS.md, each with the evidence that proves it (command output, `file:line`, screenshot). Write them before seeing any result.
- **Stop when**: the criteria are met, or one of them cannot be met (blocked, out of scope, the criterion itself looks wrong). Either way the work session stops and reports; it does not widen the scope to get there.
- **Result**: the absolute path of the result file (`artifacts/D<n>-result.md`, or the node file for a node) and the reply items: "Report: (1)… (2)…".
- **Report to**: the conductor's address from the `Mode:` line, and how to reach it (below).
- **Shared resources**: the ones this delegation holds. For any other, report "ready for <resource>" and wait.

When the user changes a requirement, update the criteria of the delegations it touches and tell their work sessions.

## Shared resources

A shared resource (a branch, an environment, a document, a push, a working tree) is held by at most one work session at a time, recorded in the `Holds` column. The conductor does not use the resource itself; it assigns it. When a holder finishes, the conductor checks the result, frees the resource, and assigns it to the next session waiting.

## Reporting: the work session's duty

The conductor sets the criteria and the stop condition; the work session owns telling the conductor when it reaches either. It reports on:

- **done**: every criterion met, each with its evidence;
- **cannot finish**: which criterion, why, and what would unblock it;
- **ready for a resource** it does not hold.

The report is the result file plus a short message: the state above, the path, and the reply items. How it reaches the conductor:

- a subagent: its final reply, which arrives as a completion notification;
- a chip or a session in another project: `SendMessage` to the conductor's address (`ListAgents` shows the sessions it can reach); not available in Codex;
- if the message cannot be sent: the result file, and a line asking the user to tell the conductor.

The conductor does not poll for reports.

## Receiving results: the conductor's duty

A report that only lives in this conversation is lost at the next `/clear`. Before replying to the user or starting anything else, write it into the graph.

1. Read the result file's evidence lines against the criteria.
2. Judge, scaled to the risk:

   | Work | Check |
   |---|---|
   | small: lookups, plain edits | the conductor reads the evidence lines and judges |
   | medium: implementation, deploys | a separate verifier subagent gets the brief and the result file and rules on each criterion: met, partial, unmet, unknown. The work session never verifies its own result. |
   | large: designs, plans, anything the user will ship | the `adversarial-review` skill |

   Code-level quality (dead code, style, contract changes) is not something the conductor can phrase as a criterion; put a procedural criterion instead, such as "ran `/review` before pushing".
3. Decide: accept, send back with only the unmet criteria, or take it to the user.
4. Record it in the graph, every time, whatever the decision:
   - accepted: the node becomes Done with its Output Contract; a delegation that was not a node goes into DECISIONS.md or the related node's Output Contract, and its row is deleted; free its resources;
   - sent back or cannot finish: set the row to Rework or Waiting and write the reason into the brief;
   - update `## Conductor` Next action if the plan changed.
5. Tell the user in a few lines in their language.

## Context cycle

The conductor's context still grows with conversation, briefs and summaries. At a work boundary or after a compaction, run `save` (which keeps `## Conductor` and `## Delegations` current), then `/clear`, then `/checkpoint next`: next sees the `## Conductor` section and resumes the conductor role instead of opening a node here.
