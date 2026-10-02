# save

Record what this session actually did. Future work that has not started is not a node here; that is `plan`.

## Steps

1. Inventory before designing anything:
   - changed, new and deleted files (`git status`, `git diff --stat`)
   - decisions made, directions rejected, validation run, blockers
   - the node this session opened through `next`, if any
2. Choose the graph: the opened node's graph, an existing graph this work belongs to, or a new `<slug>`. Apply the location rule in format.md.
3. Update nodes:
   - finished → `Done` with an Output Contract
   - unfinished → `In Progress` or `Blocked` with a rewritten Progress Snapshot
   - started but not shaped enough → Node Candidates in the active node
   - a new node only for work this session performed; finished side work that nothing depends on goes into DECISIONS.md or an Output Contract instead
   - unlock nodes whose dependencies are now Done
4. Add decisions that apply beyond one node to DECISIONS.md.
5. Update `index.md` last. If no executable node remains, archive the graph.
6. Run the checks in format.md and fix High and Medium findings this save introduced.

## Leave out

Transcript summaries, reasoning traces, exploration that led nowhere (keep only the conclusion, as a rejected direction), and anything already in source files or docs (link to it).

## Future work

Next work that is visible but not started goes into the Progress Snapshot's next action, the Output Contract's remaining risks, or a line `plan needed: <work>`. Do not create a node for it and do not point Recommended Next at it.

## Reply

- graph path and each node's status change
- whether `plan` is needed before clearing, or which node `next` will open
- suggest `/clear` (or a new session) followed by `/checkpoint next`
