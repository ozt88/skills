# audit

Report whether a graph can be trusted. Report only, unless the user asks for a repair.

1. Run `python3 scripts/check_graph.py <graph-dir>` from this skill's directory.
2. Do the reading checks in format.md.
3. Compare with reality: files and branches named in nodes exist, work marked Done is in git, and the newest user request does not contradict the graph.

```md
# Checkpoint Audit: <slug>

Status: Valid | Stale | Invalid

## Findings
- [High] ...
- [Medium] ...
- [Low] ...

## Recommended Actions
1. ...
```

Use Invalid only when the graph cannot be used until repaired. Otherwise prefer Stale.

## Repair

When asked: fix unknown status words, add missing Output Contract or Progress Snapshot sections from what the node already says, make node status lines match `index.md`, move context out of `index.md` into nodes or DECISIONS.md, and mark obsolete nodes Dropped, Superseded or Merged. Ask before deleting anything the user wrote.
