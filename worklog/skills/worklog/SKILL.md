---
name: worklog
description: Collect what the user did in Claude Code over a day or a month - each session's prompts and last reply, .knowledge/raw entry titles, and the PRs they opened or reviewed - from local session logs, including the Windows desktop app's logs when run under WSL. Use when the user asks what they worked on yesterday, on a given date, or in a month, or when another skill (daily task logging, monthly MM) needs the raw evidence. Read-only; no Notion or model calls.
allowed-tools:
  - Bash(python3 ~/.claude/skills/worklog/scripts/collect.py *)
---

# worklog

로컬 세션 기록에서 그 기간(KST)의 작업 근거를 모은다. 파일은 읽기만 한다.

```bash
python3 ~/.claude/skills/worklog/scripts/collect.py 2026-11-03          # 하루
python3 ~/.claude/skills/worklog/scripts/collect.py 2026-10 -o out.md   # 한 달
python3 ~/.claude/skills/worklog/scripts/collect.py 2026-11-03 --json   # 다른 스크립트가 읽을 때
```

- 세션마다 작업 폴더, 프롬프트, 마지막 응답이 나온다. 마지막 응답은 그 세션이 무엇을 했고 결과가 무엇인지 보여 주는 가장 좋은 근거다. 프롬프트만 보고 서비스나 목적을 추정하지 않는다.
- `gh`가 없거나 로그인돼 있지 않으면 PR 절에 실패 이유가 나온다. 나머지는 그대로 나온다. `--no-prs`로 건너뛸 수 있다.
- 결과를 끝까지 읽고 답한다. 세부가 필요하면 해당 저장소의 `.knowledge/raw/YYYY-MM-DD.md` 본문을 연다.
