#!/usr/bin/env python3
"""knowledge-compile의 컴파일 장부(.knowledge/compile-manifest.json)를 다룬다.

pending <project>          마지막 컴파일 뒤 새로 생겼거나 바뀐 raw 파일을 한 줄에 하나씩 출력한다.
mark <project> <file>...   주어진 raw 파일을 처리한 것으로 장부에 적고 last_compiled를 오늘로 바꾼다.

장부는 파일 내용의 sha256을 적는다. pending은 출력한 파일의 해시를 .knowledge/compile-pending.json에 남기고,
mark는 그 해시를 적는다. 컴파일 도중 raw에 기록이 붙어도 붙은 부분은 다음 pending에 다시 나온다.
예전 장부가 적은 정수 mtime은 파일이 그대로인 동안 처리한 것으로 본다.

장부가 없는 프로젝트는 knowledge/index.md의 "Last compiled" 날짜를 기준으로 삼는다.
그 날짜 파일부터 다시 보므로 같은 날 뒤에 붙은 기록도 놓치지 않는다.
"""
import hashlib
import json
import os
import re
import sys
from datetime import date
from pathlib import Path


def paths(project):
    kn = Path(project).expanduser().resolve() / ".knowledge"
    return kn / "raw", kn / "compile-manifest.json", kn / "knowledge" / "index.md", kn / "compile-pending.json"


def load(path):
    if path.exists():
        return json.loads(path.read_text())
    return None


def save(path, data):
    # 쓰다 끊겨도 장부가 반쯤 쓰인 채 남지 않게 임시 파일에 쓰고 바꿔 끼운다.
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n")
    os.replace(tmp, path)


def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def processed(p, seen):
    if isinstance(seen, int):
        return seen == int(p.stat().st_mtime)
    return seen == digest(p)


def pending(project):
    raw, manifest, index, snapshot = paths(project)
    if not raw.is_dir():
        return []
    files = sorted(p for p in raw.glob("*.md"))
    m = load(manifest)
    if m is not None:
        seen = m.get("files", {})
        out = [p for p in files if not processed(p, seen.get(p.name))]
    else:
        since = None
        if index.exists():
            hit = re.search(r"Last compiled:\**\s*(\d{4}-\d{2}-\d{2})", index.read_text())
            since = hit and hit.group(1)
        out = [p for p in files if since is None or p.stem >= since]
    save(snapshot, {p.name: digest(p) for p in out})
    return out


def mark(project, names):
    raw, manifest, _, snapshot = paths(project)
    m: dict = load(manifest) or {"files": {}}
    read = load(snapshot) or {}
    for n in names:
        p = raw / Path(n).name
        if p.exists():
            m["files"][p.name] = read.get(p.name) or digest(p)
    m["last_compiled"] = date.today().isoformat()
    save(manifest, m)


if __name__ == "__main__":
    if len(sys.argv) < 3 or sys.argv[1] not in ("pending", "mark"):
        sys.exit(__doc__)
    if sys.argv[1] == "pending":
        for p in pending(sys.argv[2]):
            print(p)
    else:
        mark(sys.argv[2], sys.argv[3:])
