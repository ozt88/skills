# Inbox

One todo list for every Claude Code session, whatever repository it runs in. Add items from a pane beside the chat, see what is due soon above the prompt, ask `/next` what to do now, and get a summary every weekday morning.

Codex 설치와 호출 방법은 [저장소 설치 안내](../README.md#codex)를 참고하세요. 아래는 Claude Code 사용법입니다.

Supported runtime for the instructions below: **Claude Code** (desktop app; the pane and band also draw in the terminal).

---

## Why

Todos come from everywhere (meetings, Slack, the middle of other work) and belong to different repositories, or to none yet. Writing each one into its project means first deciding which project, then going there. Inbox keeps a single list in one file, takes items without a project, and decides where to work only when you pick something up.

## How it works

| Part | What it does |
|---|---|
| `~/inbox/todo.md` | The list. One `- [ ]` line per item, with optional `#tag` and `due:YYYY-MM-DD`. Indented lines are sub-steps. Edit it by hand any time. |
| `~/inbox/projects.md` | Which repository each tag means. `/next` fills it in when it meets a tag it does not know. |
| Mod: pane | `/inbox` opens it. A field to add an item, open items with dated ones first, a button to check one off, and a button for `/next`. |
| Mod: band | Above the prompt in every session, while an item is past due or due within 3 days. Hidden for the session with one press. |
| Mod: `/todo <text>` | Adds an item or idea without opening the pane. Bare `/todo` only shows how to use it. |
| Deadline words | When adding, the first of `11/13`, `~11/13`, `11/13까지`, `오늘`, `내일`, `모레`, `금요일`, `금까지`, `다음주 월요일` in the text becomes `due:YYYY-MM-DD`, so you never type the format. A month/day already past means next year. |
| Mod: `/next` | Asks the model to pick one item (past due, due soon, an open checkpoint, unblocked steps, then age), say why, name the repository, and offer to start a session there. |
| Scheduled task | Weekdays at 9: yesterday's tasks and open questions from a daily-task run when one left a report (`~/.local/state/daily-task/runs/`), with a dated progress line added under the open item each task clearly belongs to (never checked off), due items, 1–3 picks for the day, items open over 14 days, items that need a date or tag; moves items done over a week ago to `done.md`. |

### The worker: research done before you open it

A second scheduled task ([`scheduled/inbox-worker.md`](./scheduled/inbox-worker.md), weekdays at 12:10) picks one or two open items and does what can be done unattended: research in Notion, Slack, the repository and web search, a breakdown of the work, a draft for document work, and for code a standalone prototype under `~/inbox/work/<name>/`, written but not run. It writes a note to `~/inbox/work/<name>.md` (what to decide, what it found, what it made, what blocked it, next steps) and tags the item `work:<name>`; the pane then shows a button that walks you through the note. Items tagged `#직접` are left alone.

The worker only writes inside the inbox folder, and the mod enforces it rather than trusting the prompt. A session whose prompt opens with `[inbox-worker]` is fenced from then on (`hooks/guard.ts`): reads pass; Write and Edit outside the inbox folder are refused; Bash runs only read commands and read-only `git` and `gh`, with the options that write or run a program refused (`find -exec`, `sort -o`, `rg --pre`, `git -c`, `git --output` and the like), no redirect outside the inbox folder, no background `&` and no command substitution; MCP tools pass only when their name reads as a read. Nothing runs a program, not even a script under the inbox folder, since the worker can write there. Agent, WebFetch and PowerShell are refused: a subagent's calls may not pass through the fence, and a fetched URL can carry what the worker read in Slack or Notion to anyone. The mod adds `inbox 가드 켜짐` to that first prompt, and the worker stops at once when the line is missing, so a session without the mod does nothing.

The fence is best effort, not a sandbox: it reads commands as text and refuses what it cannot read with confidence. For a hard boundary, run the worker with Claude Code's sandbox limiting writes to the inbox folder and network to the services it reads.

The mod rereads the file every minute, so edits from an editor, the morning task, or another session show up on their own. A check-off rereads the file first and finds the line by its text, so it does not clobber an edit made meanwhile.

### todo.md

```md
# Inbox

- [ ] 주간 보고서 작성 #업무 due:2026-11-14 added:2026-11-03
- [ ] 릴리스 절차 리마인드 #프로젝트A added:2026-11-03
  - [ ] 절차에 맞춰 테스트 시나리오 재작성
  - [ ] 시나리오 테스트
- [x] API 스키마 확정 #프로젝트B added:2026-11-01 done:2026-11-03
```

A large item can point to a checkpoint graph instead of growing sub-steps here; `/next` and the morning task read open checkpoints.

## Install

```bash
bash scripts/install-claude.sh
```

It copies the mod to `~/.claude/mods/inbox` and adds that folder to `env.CLAUDE_CODE_PLUGIN_DIRS` in `~/.claude/settings.json`. Re-running is safe. Restart Claude Code afterwards. Set `INBOX_DIR` to keep the list somewhere other than `~/inbox`. Run under WSL, the script sets `INBOX_DIR` to the Windows profile's `inbox` folder (for example `/mnt/c/Users/<you>/inbox`) unless it is already set, so WSL sessions, Windows sessions and the scheduled tasks share one list.

The morning task is a desktop scheduled task: ask Claude to create one from [`scheduled/inbox-morning.md`](./scheduled/inbox-morning.md), or add it under Scheduled in the sidebar. It runs while the app is open; a run missed while the app was closed runs at the next launch.

## Tests

```bash
claude plugin validate mod
claude plugin test mod
```
