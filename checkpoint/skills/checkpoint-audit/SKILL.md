---
name: checkpoint-audit
description: Audit a checkpoint artifact for stale state, invalid structure, broken dependencies, missing files, oversized context, status conflicts, and conflicts with current user intent or local filesystem/git state. Use when the user asks to validate, audit, check, repair, refresh, invalidate, or inspect a checkpoint, or when an existing checkpoint may be stale before opening or updating it. Defaults to report-only and recommends fixes unless the user asks to apply safe mechanical updates.
---

# Audit Checkpoint

Use this skill to determine whether an existing checkpoint can be trusted before opening, updating, or continuing from it.

Default to report-only. Apply fixes only when the user asks or the fixes are mechanical and low-risk.

## Audit Checks

Check:

- `index.md` exists and is readable.
- `DECISIONS.md` exists and contains graph-wide checkpoint-local ADRs.
- no `shared.md` exists; this checkpoint format does not use legacy shared context files.
- every node file listed in `index.md` exists, unless the node is a tiny parked item with no file.
- dependency edges reference existing nodes.
- the graph has no dependency cycles.
- Ready and Blocked statuses match dependencies.
- Done nodes have an `Output Contract`.
- In Progress nodes have a `Progress Snapshot`.
- node files do not contain canonical `status` frontmatter that conflicts with `index.md`.
- parked nodes stay tiny or are promoted to node files / new checkpoints.
- `index.md` stays an index, not a context dump.
- `DECISIONS.md` stays decision-oriented, not a full project context dump.
- checkpoint scope matches the current repo, files, and newest user request.
- active resume candidates live under `.checkpoint/graphs/`.
- archived graphs under `.checkpoint/archive/graphs/` are not treated as active unless explicitly requested.

## Severity

Use:

- High: unsafe to open or likely to cause wrong work.
- Medium: stale or inconsistent but repairable.
- Low: cleanup or budget issue.

## Output Format

```md
# Checkpoint Audit

Status: Valid | Stale | Invalid

## Findings
- [High] ...
- [Medium] ...
- [Low] ...

## Recommended Actions
1. ...
2. ...
```

## Invalidation

Mark a checkpoint or node invalid only when it cannot be safely used until repaired.

Prefer `Stale` when the checkpoint is probably usable after verification or minor updates.

## Repair Guidance

When asked to repair:

- make `index.md` the canonical source for status,
- remove stale status from node frontmatter,
- mark obsolete nodes as `Dropped`, `Superseded`, or `Merged`,
- move detailed context out of `index.md` into node files or `DECISIONS.md`,
- preserve user-authored content unless it is clearly stale and the user approves removal.
