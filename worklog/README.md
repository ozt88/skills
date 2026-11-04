# Worklog

Collects what you did in Claude Code over a day or a month: each session's prompts and last reply, the `.knowledge/raw/` entry titles of every repository under your home, and the PRs you opened or reviewed. It reads local files and `gh` only; it writes nothing and calls no model.

Supported runtime: **Claude Code**. The script itself is plain Python 3 and runs anywhere.

---

## Why

Daily task logging, monthly time reports, and a morning summary all start from the same question: what did I do that day? Each of them used to collect the evidence its own way. One collector means one place to get right which session logs to read.

## What it reads

| Source | Notes |
|---|---|
| `~/.claude/projects/*/*.jsonl` | Prompts in the period, minus slash-command noise, system notices, messages from other sessions, and subagent turns; plus the last assistant reply, which usually says what the session did and what came of it. Sessions are labeled by their working folder. |
| `/mnt/c/Users/*/.claude/projects/*/*.jsonl` | Under WSL, sessions the desktop app opened on a Windows path (`\\wsl.localhost\...` or `C:\...`) are logged only on the Windows side. Remote `ssh-*` folders are skipped because the same session is also logged in WSL, and a session id found on both sides is read once, from WSL. Without `/mnt/c` nothing changes. |
| `~/*/.knowledge/raw/<period>*.md` | Entry titles (`###` lines) from the work log that [knowledge-compile](../knowledge-compile) reads. |
| `gh search prs` | PRs you opened in the period and PRs you reviewed. If `gh` is missing or logged out, the PR section says why and the rest still prints. |

Periods are in KST (`YYYY-MM-DD` or `YYYY-MM`).

## Usage

```bash
python3 ~/.claude/skills/worklog/scripts/collect.py 2026-11-03          # one day, Markdown
python3 ~/.claude/skills/worklog/scripts/collect.py 2026-10 -o out.md   # one month
python3 ~/.claude/skills/worklog/scripts/collect.py 2026-11-03 --json   # for other scripts
```

Other scripts can also import it and call `collect(period)` for the same data as `--json`.

## Install

```bash
bash scripts/install-claude.sh
```

It copies the skill to `~/.claude/skills/worklog`. The desktop app on Windows reads skills from the Windows profile, so copy the folder there too if you want the skill listed in desktop sessions.

## Tests

```bash
python3 -m unittest discover -s worklog/tests
```

The tests build fake session logs; no real logs are read.
