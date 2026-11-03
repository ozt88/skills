#!/usr/bin/env python3
"""Mechanical checks for a checkpoint graph directory (see format.md).

Usage: check_graph.py <graph-dir> [<graph-dir> ...]
       check_graph.py --all <project-root>

Prints one finding per line as "[High|Medium|Low] <slug>: <message>", or "<slug>: OK".
With --all, checks every active graph under <project-root>/.checkpoint/graphs/ and ends
with the graphs to archive and to park. Exits 1 if any High finding exists. Judgement
checks (is index.md still routing only, are Output Contracts specific enough) are left
to the reader.
"""
import datetime
import pathlib
import re
import sys

STATUSES = ["in progress", "handed off", "ready", "blocked", "parked", "done",
            "superseded", "dropped", "split", "merged"]
EXECUTABLE = {"ready", "in progress", "blocked", "parked"}
# A dependency in one of these became other nodes; the edge should point at them instead.
REPLACED = {"superseded", "split", "merged"}
# An index.md past this many lines is usually carrying context that belongs in nodes.
INDEX_LINE_BUDGET = 120
# A Progress Snapshot holds the current state only (format.md); past this it is usually a log.
SNAPSHOT_LINE_BUDGET = 12
# Lines that read as rounds kept in a snapshot: a bullet that opens with a date, "2차" or "round 2",
# or a round with what was done in it ("1차 확인"). A bare "2차 UT" is a name, not a round.
ROUND_LINE = re.compile(
    r"^\s*[-*]\s*\**(\d{4}-\d{2}-\d{2}|\d+\s*차\b|round\s*\d+\b)"
    r"|\d+\s*차\s*(확인|시도|검토|리뷰|수정|반영)|\bround\s*\d+\b",
    re.I,
)
# index.md unchanged this long while nodes are still open, in progress or not: offer Parked or the archive.
STALE_DAYS = 30
# Findings --all collects into its closing lists.
TO_ARCHIVE = "no executable node left; archive the graph"
STALE_PREFIX = "stale since "

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


def section_filled(body: str, title: str) -> bool | None:
    """None if the section is absent, else whether it has content beyond empty `- Label:` template lines."""
    m = re.search(rf"^#+\s*{title}\b.*$", body, re.I | re.M)
    if not m:
        return None
    rest = body[m.end():]
    nxt = re.search(r"^#+\s", rest, re.M)
    lines = rest[:nxt.start() if nxt else len(rest)].splitlines()
    return any(l.strip() and not re.match(r"^\s*[-*]\s*[^:]+:\s*$", l) for l in lines)


def snapshot_of(body: str) -> list[str]:
    """Non-blank lines of the Progress Snapshot section, up to its next heading (Node Candidates included)."""
    lines = body.splitlines()
    start = next((i for i, l in enumerate(lines) if re.match(r"^#+\s*progress snapshot", l, re.I)), None)
    if start is None:
        return []
    out = []
    for l in lines[start + 1:]:
        if re.match(r"^#{1,2}\s", l):
            break
        if l.strip() and not l.startswith("#"):
            out.append(l)
    return out


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
        if nid in nodes:
            out.append(("High", f"{nid}: listed more than once in index.md"))
        if st is None:
            out.append(("Medium", f"{nid}: unknown status '{st_cell}'"))
        if f is None:
            sev = "High" if st in EXECUTABLE else "Medium"
            out.append((sev, f"{nid}: no node file linked or found as nodes/{nid}-*.md"))
        else:
            listed_files.add(f.resolve())
            if not f.is_file():
                out.append(("High", f"{nid}: node file {rel} missing"))
                f = None
        nodes[nid] = (st, f, deps_of(row))

    for nid, (st, f, deps) in nodes.items():
        for d in deps:
            if d not in nodes:
                out.append(("Medium", f"{nid}: depends on unknown node {d}"))
            elif st == "ready" and nodes[d][0] != "done":
                # Handed off means someone else still owns the rest, so its output is not ready either.
                hint = "; point the edge at what replaced it" if nodes[d][0] in REPLACED else ""
                out.append(("Medium", f"{nid}: Ready but dependency {d} is {nodes[d][0]}{hint}"))
        if f is None:
            continue
        body = f.read_text(encoding="utf-8", errors="replace")
        for need, title, label in (("done", "output contract", "an Output Contract"),
                                   ("in progress", "progress snapshot", "a Progress Snapshot"),
                                   ("blocked", "progress snapshot", "a Progress Snapshot")):
            if st != need:
                continue
            filled = section_filled(body, title)
            if filled is None:
                out.append(("Medium", f"{nid}: {st} without {label} section"))
            elif not filled:
                out.append(("Medium", f"{nid}: {st} with {label} section left empty"))
        if st not in ("done", "handed off", "superseded", "dropped", "split", "merged"):
            snap = snapshot_of(body)
            if len(snap) > SNAPSHOT_LINE_BUDGET:
                out.append(("Medium", f"{nid}: Progress Snapshot has {len(snap)} lines; rewrite it to the current state"))
            rounds = [l.strip() for l in snap if ROUND_LINE.search(l)]
            if rounds:
                out.append(("Medium", f"{nid}: Progress Snapshot keeps rounds ('{rounds[0][:40]}'); replace it whole on save"))
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
        out.append(("Low", TO_ARCHIVE))
    # Stale: open nodes not all parked already, and nothing touched for a while; a node left
    # In Progress for that long counts too, since abandoned work is the common case.
    waiting = [n for n in live if nodes[n][0] != "parked"]
    if not archived and waiting:
        edited = datetime.date.fromtimestamp(index.stat().st_mtime)
        if (datetime.date.today() - edited).days >= STALE_DAYS:
            busy = [n for n in waiting if nodes[n][0] == "in progress"]
            why = f"{', '.join(busy)} in progress" if busy else "no node in progress"
            out.append(("Low", f"{STALE_PREFIX}{edited.isoformat()} ({why}); park or archive"))
    return out


def report(g: pathlib.Path) -> tuple[bool, list[str]]:
    """Prints a graph's findings; returns whether any was High, and its findings' messages."""
    findings = check(g)
    if not findings:
        print(f"{g.name}: OK")
    for sev, msg in findings:
        print(f"[{sev}] {g.name}: {msg}")
    return any(sev == "High" for sev, _ in findings), [msg for _, msg in findings]


def main() -> int:
    if len(sys.argv) < 2 or (sys.argv[1] == "--all" and len(sys.argv) != 3):
        print(__doc__.strip(), file=sys.stderr)
        return 2
    if sys.argv[1] == "--all":
        root = pathlib.Path(sys.argv[2]) / ".checkpoint" / "graphs"
        graphs = sorted(p for p in root.iterdir() if p.is_dir()) if root.is_dir() else []
        if not graphs:
            print(f"no active graph under {root}")
            return 0
        high, to_archive, to_park = False, [], []
        for g in graphs:
            h, msgs = report(g)
            high |= h
            if TO_ARCHIVE in msgs:
                to_archive.append(g.name)
            if any(m.startswith(STALE_PREFIX) for m in msgs):
                to_park.append(g.name)
        print(f"archive: {', '.join(to_archive) or '-'}")
        print(f"park or archive (stale): {', '.join(to_park) or '-'}")
        return 1 if high else 0
    high = False
    for arg in sys.argv[1:]:
        high |= report(pathlib.Path(arg))[0]
    return 1 if high else 0


if __name__ == "__main__":
    sys.exit(main())
