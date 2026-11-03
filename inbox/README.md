# Inbox

One todo list for every Claude Code session, whatever repository it runs in. Add items from a pane beside the chat, see what is due soon above the prompt, ask `/next` what to do now, and get a summary every weekday morning.

Supported runtime: **Claude Code** (desktop app; the pane and band also draw in the terminal).

---

## Why

Todos come from everywhere (meetings, Slack, the middle of other work) and belong to different repositories, or to none yet. Writing each one into its project means first deciding which project, then going there. Inbox keeps a single list in one file, takes items without a project, and decides where to work only when you pick something up.

## How it works

| Part | What it does |
|---|---|
| `~/inbox/todo.md` | The list. One `- [ ]` line per item, with optional `#tag` and `due:YYYY-MM-DD`. Indented lines are sub-steps. Edit it by hand any time. |
| `~/inbox/projects.md` | Which repository each tag means. `/next` fills it in when it meets a tag it does not know. |
| Mod: pane | `/todo` opens it. A field to add an item, open items with dated ones first, a button to check one off, and a button for `/next`. |
| Mod: band | Above the prompt in every session, while an item is past due or due within 3 days. Hidden for the session with one press. |
| Mod: `/todo <text>` | Adds an item without opening the pane. |
| Deadline words | When adding, the first of `11/13`, `~11/13`, `11/13까지`, `오늘`, `내일`, `모레`, `금요일`, `금까지`, `다음주 월요일` in the text becomes `due:YYYY-MM-DD`, so you never type the format. A month/day already past means next year. |
| Mod: `/next` | Asks the model to pick one item (past due, due soon, an open checkpoint, unblocked steps, then age), say why, name the repository, and offer to start a session there. |
| Scheduled task | Weekdays at 9: due items, 1–3 picks for the day, items open over 14 days, items that need a date or tag; moves items done over a week ago to `done.md`. |

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

It copies the mod to `~/.claude/mods/inbox` and adds that folder to `env.CLAUDE_CODE_PLUGIN_DIRS` in `~/.claude/settings.json`. Re-running is safe. Restart Claude Code afterwards. Set `INBOX_DIR` to keep the list somewhere other than `~/inbox`.

The morning task is a desktop scheduled task: ask Claude to create one from [`scheduled/inbox-morning.md`](./scheduled/inbox-morning.md), or add it under Scheduled in the sidebar. It runs while the app is open; a run missed while the app was closed runs at the next launch.

## Tests

```bash
claude plugin validate mod
claude plugin test mod
```
