# init

Make this session the conductor of a graph: from now on it keeps the context and hands the work to work sessions. The user runs `init` by hand, usually when a long session is expected; never start it on your own.

`/checkpoint init [goal in one line]`

## Steps

1. **Get a graph.**
   - No active graph: create one now, without the `plan` proposal. Write `.checkpoint/graphs/<slug>/index.md` and an empty `DECISIONS.md`, with the slug taken from the goal. Apply the location rule in format.md. Ask for the goal only if the request and the conversation give none.
   - Active graphs exist: join the one that matches the goal. If it is ambiguous, ask once whether to join one or create a new graph.
   - Nodes may start empty. Add them with `plan` when work worth a session of its own appears.
2. **Mark the conductor.** Add the `## Conductor` section to `index.md` (format.md). The session name is the address other sessions message this one by: in Claude Code, the `This session is <name> [<ref>]` line `ListAgents` prints. Where there is none (Codex), use the name the user gives, otherwise `<date>-<slug>`. If the section already names another session, ask whether this session takes over; on yes, replace the name.
3. **Take stock.**
   - If work already happened in this session, record it with the `save` steps first.
   - List the subagents, chips and other-project handoffs already running under `## Delegations`.
   - Show the user the shared resources in play (branches, environments, documents, pushes) and who holds each.
4. Check the runtime (conductor.md, Runtimes). In Codex, tell the user there are no chips and no messages between sessions, so work goes to subagents or to new sessions they start, and reports come through them.
5. Read [conductor.md](conductor.md) and work by it until the graph is archived or the user ends conductor mode.

## Ending

When the user ends conductor mode, delete the `## Conductor` and `## Delegations` sections after every delegation is resolved or written into a node. Archiving the graph ends it too.

## Reply

The graph path, the session name, the delegations and resource holders found, and one line on how the session will work from here: it decides and delegates, and work sessions do the work.
