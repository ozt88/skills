# plan

Design nodes for future work that has not started. Propose first, write after approval.

## Before proposing

Read local files first. Ask the user only what files cannot answer and what would change the graph's shape (node scope, order, approval gates, location), one question at a time.

Settle:
- What concrete output ends this work, and what is out of scope.
- Granularity: one node is about one focused session. Merge steps of the same session; split on different goals, dependencies, approval gates or blockers.
- Operations that change what later nodes may read or trust (a migration, a rename, a deletion). Record each as a CP-ADR.
- The first node must be executable from graph files alone.

If an existing node has Node Candidates, decide for each one: promote, merge, park, drop, or leave as a candidate.

## Proposal

Show the graph path, each node (id, goal, completion condition), edges, the recommended first node, the candidate decisions, and remaining assumptions.

Write nothing until the user approves the structure or gives subset or ordering instructions. Invoking `plan` is not approval. If the user asked for no interaction (for example `auto`), write directly and say so in the reply.

## After approval

Write the nodes from the format.md template (Goal, Required context, Do not read by default, Completion condition), then DECISIONS.md, then `index.md`. Run the checks. Reply with the first node and tell the user that a fresh session should run `/checkpoint next`.
