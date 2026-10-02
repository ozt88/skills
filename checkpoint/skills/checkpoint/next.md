# next

Open the next node in a fresh session. The graph replaces the previous conversation; do not load old transcripts or handoff files.

1. Find active graphs at `<project-root>/.checkpoint/graphs/*/index.md`, excluding the archive unless asked. With several graphs, let the user's request pick one; if it is still ambiguous, ask.
2. Read `index.md`. Candidates are Ready and In Progress nodes, plus Blocked or Parked nodes whose condition is now met.
3. Pick `Recommended Next` if it is still valid. Otherwise rank by match with the user's request, what the node unlocks, its size, and the risk it removes. If several are plausible, show up to five with a one-line reason each, recommend one, and ask.
4. Read only the chosen node, the CP-ADRs it cites or that apply to all nodes, and the Output Contracts of its direct dependencies.
5. Check for staleness: files the node names exist and git state matches its snapshot. Report conflicts before starting.
6. If the node was Ready, set it to In Progress in `index.md`.
7. Summarize the goal, the stopping point and the next action, then start the work.
