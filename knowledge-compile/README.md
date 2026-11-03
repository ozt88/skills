# Knowledge Compile

Knowledge Compile turns the work log an agent appends during sessions (`.knowledge/raw/YYYY-MM-DD.md`) into a small set of curated files the next session can read first: decisions, guardrails, anti-patterns, troubleshooting, and an index.

Codex 설치와 호출 방법은 [저장소 설치 안내](../README.md#codex)를 참고하세요. 아래는 Claude Code 사용법입니다.

Supported runtime for the instructions below: **Claude Code**.

---

## Why

Logging is cheap, so raw logs pile up. Nobody rereads forty dated files before starting work, and the same mistake gets logged again. Compiling merges the logs into one place per kind of lesson, counts how often each lesson was observed, and flags lessons that contradict earlier ones.

Compiling takes a model and a few minutes per project, so it belongs outside working hours. The bundled runner checks every project for new raw logs and compiles only those, once a night.

## How it works

1. **Logging (your setup).** A `CLAUDE.md` instruction asks the agent to append finished work to `.knowledge/raw/`. An example is below.
2. **Compiling (this skill).** `/knowledge-compile` reads only raw files that are new or changed since the last compile, merges them into `.knowledge/knowledge/`, and records a content hash of what it read in `.knowledge/compile-manifest.json`. Lines appended to a raw file while it is being compiled stay pending for the next compile.
3. **Scheduling (optional).** `scripts/compile-all.sh` runs the skill headlessly in every project that has new raw logs.
4. **Loading (mod or hook).** The nearest `.knowledge/knowledge/index.md` above the working directory goes into the session; only the index, and the agent opens a detail file when the task touches one of its topics. Without this step, compiled knowledge sits unread unless something tells the agent to look. Two ways, reading the same files:
   - **Mod** (`mod/`, the default): reads the index at session start and again after each compaction, and sends it with the next prompt as context, so a nightly compile reaches a running session at its next compaction. It also notes which knowledge files the agent read, and when the agent next writes a raw log, reminds it of them so it can add `참조:` lines. (It does not use a `prompt.compose` system prompt section: on a machine with managed settings, the built-in security plugin skips a user mod's `prompt.compose` hook.)
   - **Hook** (`hooks/knowledge_index_hook.py`): a `SessionStart` hook that adds the index to the session context. For a Claude Code without mods.

When a project has no manifest yet, the skill starts from the `Last compiled` date in `knowledge/index.md`, or from the first raw file if there is no index.

### Merge rules

| File | Holds |
|---|---|
| `decisions.md` | design decisions with what was tried, what happened, and what was chosen; status `active`, `uncertain`, `superseded`, or `rejected` |
| `guardrails.md` | rules with a single right answer, written as actions to take |
| `anti-patterns.md` | traps whose right answer depends on context |
| `troubleshooting.md` | errors mapped to causes and fixes |
| `index.md` | a topic table and keyword index, so one read tells you which file to open |

- A lesson seen again bumps its `Observed: N times (dates)` counter instead of adding a duplicate.
- The logging instruction (below) asks the agent to add `- 참조: <file> › <entry title>` to its raw log whenever an entry changed a decision. Compiling turns those lines into a `Referenced: N times (dates)` counter on the entry and an `(ref N)` mark in the index, so you can see which entries actually get used. `Observed` counts how often a lesson recurs; `Referenced` counts how often it was applied.
- A conclusion that contradicts an existing decision is kept as a dated `New` quote and marks the entry `uncertain`; later evidence settles it.
- When appending to an existing file, the skill keeps that file's field names and heading levels.

## Usage

```bash
/knowledge-compile          # in a project with .knowledge/raw/
```

### Example logging instruction

Add something like this to `~/.claude/CLAUDE.md`:

```md
# Knowledge Compiler

When you finish an implementation, a debugging session, or a design decision worth reusing,
append it to `{primary_working_directory}/.knowledge/raw/YYYY-MM-DD.md`.

### HH:MM — one-line title
- item
- 참조: decisions.md › entry title

Add a `참조:` line for each `.knowledge/knowledge/` entry that changed a decision
or prevented a mistake. Leave out entries you only opened.
```

The `참조:` prefix is what the compiler looks for; keep it even if the rest of your log is in another language.

### Nightly runner

```bash
~/.claude/skills/knowledge-compile/scripts/compile-all.sh          # respects the night window
~/.claude/skills/knowledge-compile/scripts/compile-all.sh --now    # compile now
```

Call it every hour; it exits immediately outside the night window (20:00 to 08:00 by default) or when tonight's compile is done. If the machine was off at night, the next night catches up.

| Variable | Default | Meaning |
|---|---|---|
| `KNOWLEDGE_ROOTS` | `~/.knowledge ~/.claude/.knowledge ~/*/.knowledge` | `.knowledge` directories to scan |
| `KC_NIGHT_START` | `20` | hour the window opens |
| `KC_NIGHT_END` | `8` | hour the window closes |

Each headless run may write only under that project's `.knowledge/knowledge/` and may run only the manifest script; anything else is denied without a prompt. Raw logs are never modified.

Only one runner works at a time; a second one, scheduled or `--now`, exits. A project whose compile or manifest step fails is reported, keeps its raw files pending, and does not count tonight as done, so the next run retries it.

The runner needs Linux or WSL: GNU `date -d`, `flock`, `timeout`, and Bash 4 or later. macOS is not supported as is. `KNOWLEDGE_ROOTS` is split on spaces, so paths containing spaces are not supported.

Cron:

```cron
0 * * * * $HOME/.claude/skills/knowledge-compile/scripts/compile-all.sh >> $HOME/.local/state/knowledge-compile/cron.log 2>&1
```

Windows Task Scheduler with WSL (PowerShell):

```powershell
$action = New-ScheduledTaskAction -Execute "wsl.exe" -Argument "-d Ubuntu -e bash -lc ~/.claude/skills/knowledge-compile/scripts/compile-all.sh"
$hourly = New-ScheduledTaskTrigger -Once -At (Get-Date).Date -RepetitionInterval (New-TimeSpan -Hours 1)
$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -ExecutionTimeLimit (New-TimeSpan -Hours 3) -MultipleInstances IgnoreNew
Register-ScheduledTask -TaskName "knowledge-compile" -Action $action -Trigger $hourly -Settings $settings
```

## Files

```
knowledge-compile/
├─ skills/knowledge-compile/
│  ├─ SKILL.md                 merge rules (Korean)
│  └─ scripts/
│     ├─ manifest.py           pending / mark: which raw files still need compiling
│     └─ compile-all.sh        headless runner for every project
├─ mod/                        Claude Code mod: index on the next prompt + 참조 reminder
│  ├─ hooks/register.ts
│  ├─ hooks/paths.ts
│  └─ tests/knowledge.test.ts  claude plugin test mod
├─ hooks/knowledge_index_hook.py   SessionStart: injects index.md (without mods)
└─ scripts/install-claude.sh
```

## Install

```bash
bash scripts/install-claude.sh
```

It copies the skill to `~/.claude/skills/knowledge-compile` and the mod to `~/.claude/mods/knowledge`, and adds that folder to `env.CLAUDE_CODE_PLUGIN_DIRS` in `~/.claude/settings.json`. With `--hook` it installs the `SessionStart` hook instead. Either way it removes the other, so the index is never added twice. Re-running is safe. Restart Claude Code afterwards.
