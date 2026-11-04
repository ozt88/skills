#!/usr/bin/env python3
"""하루 또는 한 달 동안의 Claude Code 작업 근거를 모은다. Notion과 LLM은 쓰지 않는다.

- 세션: ~/.claude/projects/*/*.jsonl 의 사용자 프롬프트와 마지막 어시스턴트 응답.
  WSL에서 돌면 Windows 데스크톱 앱 기록(/mnt/c/Users/*/.claude/projects)도 읽는다.
- .knowledge/raw: 홈 아래 저장소의 그 기간 항목 제목(### 줄)
- PR: gh CLI로 그 기간에 만든 PR과 리뷰한 PR

사용:
  collect.py 2026-11-03                 # 하루 (KST)
  collect.py 2026-10 -o out.md          # 한 달
  collect.py 2026-11-03 --json          # 스크립트용
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import re
import subprocess
from datetime import datetime, timedelta, timezone

KST = timezone(timedelta(hours=9))
HOME = os.path.expanduser("~")
WIN_PROJECTS = "/mnt/c/Users/*/.claude/projects"
WSL_UNC = re.compile(r"^\\\\wsl(?:\.localhost|\$)\\[^\\]+", re.I)
NOISE_COMMANDS = {"clear", "model", "compact", "mcp", "statusline"}
REPLY_CHARS = 600


def period_range(period: str):
    """기간(YYYY-MM 또는 YYYY-MM-DD, KST)을 [시작, 끝) KST datetime으로 바꾼다."""
    if len(period) == 10:
        start = datetime.strptime(period, "%Y-%m-%d").replace(tzinfo=KST)
        return start, start + timedelta(days=1)
    start = datetime.strptime(period, "%Y-%m").replace(tzinfo=KST)
    return start, (start + timedelta(days=32)).replace(day=1)


def period_range_utc(period: str):
    """jsonl timestamp와 문자열로 비교할 수 있는 UTC 'YYYY-MM-DDTHH:MM' 범위."""
    fmt = "%Y-%m-%dT%H:%M"
    return tuple(t.astimezone(timezone.utc).strftime(fmt) for t in period_range(period))


def prompt_text(msg):
    c = msg.get("message", {}).get("content")
    if isinstance(c, list):
        c = " ".join(x.get("text", "") for x in c if isinstance(x, dict) and x.get("type") == "text")
    if not isinstance(c, str):
        return None
    c = " ".join(c.split())
    if not c or c.startswith("[Request interrupted"):
        return None
    m = re.search(r"<command-name>/?([^<]+)</command-name>", c)
    if m:
        name = m.group(1)
        return None if name in NOISE_COMMANDS else f"/{name}"
    if c.startswith("<"):  # 시스템 알림, 다른 세션 메시지 같은 사람 입력이 아닌 것
        return None
    return c


def reply_text(msg):
    c = msg.get("message", {}).get("content")
    if isinstance(c, str):
        texts = [c]
    elif isinstance(c, list):
        texts = [x.get("text", "") for x in c if isinstance(x, dict) and x.get("type") == "text"]
    else:
        return None
    t = " ".join(" ".join(texts).split())
    return t or None


def label_from_cwd(cwd, home=HOME):
    if WSL_UNC.match(cwd):
        cwd = WSL_UNC.sub("", cwd).replace("\\", "/")
    if cwd == home or cwd.startswith(home + "/"):
        cwd = "~" + cwd[len(home):]
    return cwd


def session_files(home=HOME, win_projects=WIN_PROJECTS):
    """세션 파일 목록. 같은 세션 id(파일 이름)가 양쪽에 있으면 WSL 쪽을 쓴다.

    Windows 쪽 원격(ssh-<id>) 폴더는 WSL 쪽에도 같은 세션이 남으므로 읽지 않는다.
    """
    files = {}
    for f in sorted(glob.glob(os.path.join(home, ".claude/projects/*/*.jsonl"))):
        files.setdefault(os.path.basename(f), f)
    for f in sorted(glob.glob(os.path.join(win_projects, "*/*.jsonl"))):
        if not os.path.basename(os.path.dirname(f)).startswith("ssh-"):
            files.setdefault(os.path.basename(f), f)
    return sorted(files.values())


def read_session(f, lo, hi, home=HOME):
    """기간 안의 프롬프트와 마지막 어시스턴트 응답. 기간 안에 프롬프트가 없으면 None."""
    cwd, prompts, reply = None, [], None
    with open(f, errors="ignore") as fh:
        for line in fh:
            try:
                d = json.loads(line)
            except json.JSONDecodeError:
                continue
            if not isinstance(d, dict):
                continue
            cwd = cwd or d.get("cwd")
            ts = d.get("timestamp", "")
            if not (lo <= ts < hi) or d.get("isMeta") or d.get("isSidechain"):
                continue
            if d.get("type") == "user":
                t = prompt_text(d)
                if t:
                    prompts.append((ts, t))
            elif d.get("type") == "assistant":
                reply = reply_text(d) or reply
    if not prompts:
        return None
    return {
        "id": os.path.basename(f)[:-6],
        "label": label_from_cwd(cwd, home) if cwd else os.path.basename(os.path.dirname(f)),
        "first": prompts[0][0],
        "last": prompts[-1][0],
        "prompts": prompts,
        "reply": reply[:REPLY_CHARS] if reply else None,
    }


def collect_sessions(period, home=HOME, win_projects=WIN_PROJECTS):
    lo, hi = period_range_utc(period)
    out = []
    for f in session_files(home, win_projects):
        s = read_session(f, lo, hi, home)
        if s:
            out.append(s)
    return sorted(out, key=lambda s: (s["label"], s["first"]))


def collect_knowledge(period, home=HOME):
    pats = [
        os.path.join(home, "*", ".knowledge/raw", f"{period}*.md"),
        os.path.join(home, ".claude/projects/*/.knowledge/raw", f"{period}*.md"),
    ]
    out = []
    for f in sorted({p for pat in pats for p in glob.glob(pat)}):
        with open(f, errors="ignore") as fh:
            heads = [l.strip()[4:] for l in fh if l.startswith("### ")]
        if heads:
            out.append({"file": f.replace(home, "~", 1), "heads": heads})
    return out


def gh(args):
    try:
        r = subprocess.run(["gh", *args], capture_output=True, text=True, timeout=60)
    except (OSError, subprocess.TimeoutExpired) as e:
        return {"error": str(e)}
    if r.returncode != 0:
        return {"error": r.stderr.strip()[:200]}
    return json.loads(r.stdout or "[]")


def collect_prs(period):
    start, end = period_range(period)
    first, last = start.date().isoformat(), (end - timedelta(days=1)).date().isoformat()
    created = first if first == last else f"{first}..{last}"
    return {
        "authored": gh(["search", "prs", "--author=@me", f"--created={created}", "--limit", "100",
                        "--json", "repository,number,title,state,url"]),
        "reviewed": gh(["search", "prs", "--reviewed-by=@me", f"--updated={first}..{end.date().isoformat()}",
                        "--limit", "100", "--json", "repository,number,title,author,url"]),
    }


def collect(period, prs=True, home=HOME, win_projects=WIN_PROJECTS):
    return {
        "period": period,
        "sessions": collect_sessions(period, home, win_projects),
        "knowledge": collect_knowledge(period, home),
        "prs": collect_prs(period) if prs else None,
    }


def kst(ts):
    return datetime.fromisoformat(ts.replace("Z", "+00:00")).astimezone(KST)


def pr_lines(rows):
    if isinstance(rows, dict):
        return [f"(gh 실패: {rows['error']})"]
    return [f"- {r['repository']['nameWithOwner']}#{r['number']} {r['title']}"
            + (f" ({r['state']})" if r.get("state") else "")
            + (f" by {r['author']['login']}" if r.get("author") else "")
            for r in rows] or ["(없음)"]


def render(data, max_prompts=40):
    lines = [f"# Claude 작업 기록 {data['period']} (KST)", "", "# 세션", ""]
    for s in data["sessions"]:
        lines.append(f"## {s['label']} {s['id'][:8]} {kst(s['first']):%m-%d}~{kst(s['last']):%m-%d} "
                     f"({len(s['prompts'])} prompts)")
        lines += [f"- {kst(ts):%m-%d %H:%M} {t[:300]}" for ts, t in s["prompts"][:max_prompts]]
        if s["reply"]:
            lines.append(f"- 마지막 응답: {s['reply']}")
        lines.append("")
    lines += ["# .knowledge/raw 항목", ""]
    for k in data["knowledge"]:
        lines += [f"## {k['file']}", *[f"- {h}" for h in k["heads"]], ""]
    if data["prs"] is not None:
        lines += ["# PR", "", "## 내가 만든 PR", *pr_lines(data["prs"]["authored"]), "",
                  "## 내가 리뷰한 PR", *pr_lines(data["prs"]["reviewed"]), ""]
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser(description="Claude Code 작업 근거 수집")
    ap.add_argument("period", help="YYYY-MM 또는 YYYY-MM-DD (KST)")
    ap.add_argument("-o", "--out")
    ap.add_argument("--json", action="store_true", help="마크다운 대신 JSON으로 낸다")
    ap.add_argument("--max-prompts", type=int, default=40, help="마크다운에서 세션마다 보일 프롬프트 수")
    ap.add_argument("--no-prs", action="store_true", help="gh 조회를 건너뛴다")
    a = ap.parse_args()
    data = collect(a.period, prs=not a.no_prs)
    text = json.dumps(data, ensure_ascii=False, indent=1) if a.json else render(data, a.max_prompts)
    if a.out:
        with open(a.out, "w") as fh:
            fh.write(text)
        print(f"{a.out}: {len(text)} chars")
    else:
        print(text)


if __name__ == "__main__":
    main()
