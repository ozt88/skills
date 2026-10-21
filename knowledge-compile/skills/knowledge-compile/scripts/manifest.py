#!/usr/bin/env python3
"""knowledge-compile의 컴파일 장부(.knowledge/compile-manifest.json)를 다룬다.

pending <project>          마지막 컴파일 뒤 새로 생겼거나 바뀐 raw 파일을 한 줄에 하나씩 출력한다.
mark <project> <file>...   주어진 raw 파일의 현재 mtime을 장부에 적고 last_compiled를 오늘로 바꾼다.

장부가 없는 프로젝트는 knowledge/index.md의 "Last compiled" 날짜를 기준으로 삼는다.
그 날짜 파일부터 다시 보므로 같은 날 뒤에 붙은 기록도 놓치지 않는다.
"""
import json
import re
import sys
from datetime import date
from pathlib import Path


def paths(project):
    kn = Path(project).expanduser().resolve() / ".knowledge"
    return kn / "raw", kn / "compile-manifest.json", kn / "knowledge" / "index.md"


def load(manifest):
    if manifest.exists():
        return json.loads(manifest.read_text())
    return None


def pending(project):
    raw, manifest, index = paths(project)
    if not raw.is_dir():
        return []
    files = sorted(p for p in raw.glob("*.md"))
    m = load(manifest)
    if m is not None:
        seen = m.get("files", {})
        return [p for p in files if seen.get(p.name) != int(p.stat().st_mtime)]
    since = None
    if index.exists():
        hit = re.search(r"Last compiled:\**\s*(\d{4}-\d{2}-\d{2})", index.read_text())
        since = hit and hit.group(1)
    return [p for p in files if since is None or p.stem >= since]


def mark(project, names):
    raw, manifest, _ = paths(project)
    m: dict = load(manifest) or {"files": {}}
    for n in names:
        p = raw / Path(n).name
        if p.exists():
            m["files"][p.name] = int(p.stat().st_mtime)
    m["last_compiled"] = date.today().isoformat()
    manifest.write_text(json.dumps(m, ensure_ascii=False, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    if len(sys.argv) < 3 or sys.argv[1] not in ("pending", "mark"):
        sys.exit(__doc__)
    if sys.argv[1] == "pending":
        for p in pending(sys.argv[2]):
            print(p)
    else:
        mark(sys.argv[2], sys.argv[3:])
