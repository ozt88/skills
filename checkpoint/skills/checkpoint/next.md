# next

Open the next node in a fresh session. The graph replaces the previous conversation; do not load old transcripts or handoff files by default.

When the chosen node lacks the reason for a decision it depends on, or two sources disagree, follow the links the node, its Output Contracts, or DECISIONS.md give (the original request, a design doc, a commit) before asking the user to explain again. If no link leads to the reason, mark it unconfirmed instead of reconstructing it from guesswork.

1. Find active graphs at `<project-root>/.checkpoint/graphs/*/index.md`, excluding the archive unless asked. With several graphs, let the user's request pick one; if it is still ambiguous, ask. If any active graph is stale or has no executable node (`check_graph.py --all <project-root>`), say so in one line and offer to archive or park it. Do not move it unasked.
2. Read `index.md`. Candidates are Ready and In Progress nodes, plus Blocked or Parked nodes whose condition is now met.
3. Pick `Recommended Next` if it is still valid. Otherwise rank by match with the user's request, what the node unlocks, its size, and the risk it removes. If several are plausible, show up to five with a one-line reason each, recommend one, and ask.
4. Read only the chosen node, the CP-ADRs it cites or that apply to all nodes, and the Output Contracts of its direct dependencies.
5. Check for staleness: files the node names exist and git state matches its snapshot. Report conflicts before starting.
6. If the node was Ready, set it to In Progress in `index.md`.
7. Summarize the goal, the stopping point and the next action, then start the work.

## Conductor graphs

When the chosen graph's `index.md` has a `## Conductor` section ([conductor.md](conductor.md)):

- **A fresh session resumes the conductor**, it does not open a node here. Read `## Conductor`, `## Delegations`, DECISIONS.md, and the briefs of rows in Review. Replace the session name in `Mode:` with this session's (a new session took over after `/clear`), summarize the goal, the running delegations and who holds which resource, then continue from `Next action`.
- **The conductor picks a node to start**: follow steps 2 to 5, then ask whether to run it in this session or hand it to a work session. To hand it off:
  - set it to `In Progress (<owner>)` in `index.md` and add a `## Delegations` row;
  - make sure the node file has the brief items conductor.md lists (criteria in Completion condition);
  - start the work session with: begin with `/checkpoint next <graph> <node>`, the graph's absolute path (a chip's worktree has no `.checkpoint/`), what not to do, the conductor's address, and on stopping save only its own node file and report to the conductor (conductor.md, Reporting).
- **A work session opened with `next <graph> <node>`** works that node only, never writes `index.md`, and stops when the Completion condition is met or cannot be met. Either way it saves its own node file (save.md) and reports to the conductor's address in the `Mode:` line.
