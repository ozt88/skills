#!/usr/bin/env python3
"""Mechanical checks for a checkpoint graph directory (see format.md).

Usage: check_graph.py <graph-dir> [<graph-dir> ...]

Prints one finding per line as "[High|Medium|Low] <slug>: <message>", or "<slug>: OK".
Exits 1 if any High finding exists. Judgement checks (is index.md still routing only,
are Output Contracts specific enough) are left to the reader.
"""
import pathlib
import re
import sys

STATUSES = ["in progress", "handed off", "ready", "blocked", "parked", "done",
            "superseded", "dropped", "split", "merged"]
EXECUTABLE = {"ready", "in progress", "blocked", "parked"}
# An index.md past this many lines is usually carrying context that belongs in nodes.
INDEX_LINE_BUDGET = 120

NODE_ID = re.compile(r"\bN\d+\b")
NODE_LINK = re.compile(r"(nodes/[^)\s`|]+\.md)")


def status_of(cell: str) -> str | None:
    s = re.sub(r"[*_`]", "", cell).strip().lower()
    for st in STATUSES:
        if s.startswith(st):
            return st
    return None


def parse_rows(index_text: str):
    """Return rows of the first table under a 'Nodes' heading as dicts of header -> cell."""
    lines = index_text.splitlines()
    try:
        start = next(i for i, l in enumerate(lines) if re.match(r"^#+\s*nodes\b", l.strip(), re.I))
    except StopIteration:
        return None
    table = []
    for l in lines[start + 1:]:
        if l.startswith("#"):
            break
        if l.strip().startswith("|"):
            table.append([c.strip() for c in l.strip().strip("|").split("|")])
        elif table:
            break
    if len(table) < 2:
        return None
    header = [h.lower() for h in table[0]]
    return [dict(zip(header, r)) for r in table[2:]]


def deps_of(row: dict) -> list[str]:
    deps = []
    for key, cell in row.items():
        if "depend" in key:
            deps += NODE_ID.findall(cell)
        elif "edge" in key:
            for part in re.split(r"<br>|;", cell):
                if "depends_on" in part:
                    deps += NODE_ID.findall(part)
    return deps


def has_cycle(graph: dict[str, list[str]]) -> bool:
    state = {}

    def visit(n):
        state[n] = 1
        for d in graph.get(n, []):
            if state.get(d) == 1 or (d not in state and d in graph and visit(d)):
                return True
        state[n] = 2
        return False

    return any(n not in state and visit(n) for n in graph)


def check(gdir: pathlib.Path) -> list[tuple[str, str]]:
    out = []
    index = gdir / "index.md"
    if not index.is_file():
        return [("High", "index.md missing")]
    if not (gdir / "DECISIONS.md").is_file():
        out.append(("Medium", "DECISIONS.md missing"))
    text = index.read_text(encoding="utf-8", errors="replace")
    if len(text.splitlines()) > INDEX_LINE_BUDGET:
        out.append(("Low", f"index.md has {len(text.splitlines())} lines; move context into nodes or DECISIONS.md"))
    rows = parse_rows(text)
    if rows is None:
        return out + [("High", "no node table under a 'Nodes' heading in index.md")]

    nodes = {}  # id -> (status, file, deps)
    listed_files = set()
    for row in rows:
        cells = " | ".join(row.values())
        st_cell = next((v for k, v in row.items() if "status" in k), "")
        st = status_of(st_cell)
        link = NODE_LINK.search(cells)
        rel = link.group(1) if link else None
        first = next(iter(row.values()), "")
        ids = NODE_ID.findall(first) or (NODE_ID.findall(rel) if rel else [])
        nid = ids[0] if ids else (rel or first or "?")
        if rel is None and ids:
            # Rows without a link: fall back to the nodes/<id>-*.md naming convention.
            match = sorted((gdir / "nodes").glob(f"{ids[0]}-*.md"))
            rel = f"nodes/{match[0].name}" if match else None
        f = gdir / rel if rel else None
        if st is None:
            out.append(("Medium", f"{nid}: unknown status '{st_cell}'"))
        if f is not None:
            listed_files.add(f.resolve())
            if not f.is_file():
                out.append(("High", f"{nid}: node file {rel} missing"))
                f = None
        nodes[nid] = (st, f, deps_of(row))

    for nid, (st, f, deps) in nodes.items():
        for d in deps:
            if d not in nodes:
                out.append(("Medium", f"{nid}: depends on unknown node {d}"))
            elif st == "ready" and nodes[d][0] not in ("done", "handed off", "superseded", "merged"):
                out.append(("Medium", f"{nid}: Ready but dependency {d} is {nodes[d][0]}"))
        if f is None:
            continue
        body = f.read_text(encoding="utf-8", errors="replace")
        if st == "done" and not re.search(r"^#+\s*output contract", body, re.I | re.M):
            out.append(("Medium", f"{nid}: Done without an Output Contract section"))
        if st in ("in progress", "blocked") and not re.search(r"^#+\s*progress snapshot", body, re.I | re.M):
            out.append(("Medium", f"{nid}: {st} without a Progress Snapshot section"))
        own = re.search(r"^\**status\**\s*:\s*(.+)$", body, re.I | re.M)
        if own and st and status_of(own.group(1)) != st:
            out.append(("Medium", f"{nid}: node file says '{own.group(1).strip()}' but index.md says {st}"))

    if has_cycle({n: v[2] for n, v in nodes.items()}):
        out.append(("High", "dependency cycle"))
    for f in sorted((gdir / "nodes").glob("*.md")) if (gdir / "nodes").is_dir() else []:
        if f.resolve() not in listed_files:
            out.append(("Low", f"nodes/{f.name} is not listed in index.md"))
    archived = "archive" in gdir.parts
    live = [n for n, v in nodes.items() if v[0] in EXECUTABLE]
    if archived and live:
        out.append(("Low", f"archived graph still has executable nodes: {', '.join(live)}"))
    if not archived and not live:
        out.append(("Low", "no executable node left; archive the graph"))
    return out


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__.strip(), file=sys.stderr)
        return 2
    high = False
    for arg in sys.argv[1:]:
        g = pathlib.Path(arg)
        findings = check(g)
        if not findings:
            print(f"{g.name}: OK")
        for sev, msg in findings:
            high |= sev == "High"
            print(f"[{sev}] {g.name}: {msg}")
    return 1 if high else 0


if __name__ == "__main__":
    sys.exit(main())
