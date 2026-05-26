#!/usr/bin/env bash
# install-claude.sh — Claude Code global hook installer
# Counterpart to install-global-hooks.ps1 for Linux/macOS
#
# Usage:
#   bash scripts/install-claude.sh          # global install (~/.claude/)
#   bash scripts/install-claude.sh --local  # project-local install (.claude/)

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
GLOBAL=true

for arg in "$@"; do
  case $arg in
    --local) GLOBAL=false ;;
  esac
done

if $GLOBAL; then
  CLAUDE_DIR="$HOME/.claude"
  echo "Global install: $CLAUDE_DIR"
else
  CLAUDE_DIR="$REPO_ROOT/.claude"
  echo "Local install: $CLAUDE_DIR"
fi

HOOKS_DIR="$CLAUDE_DIR/hooks"
SETTINGS="$CLAUDE_DIR/settings.json"
SRC_HOOK="$REPO_ROOT/hooks/checkpoint_session_hook.py"

if ! command -v python3 &>/dev/null; then
  echo "Error: python3 is required." >&2
  exit 1
fi

# Install hook script
mkdir -p "$HOOKS_DIR"
cp "$SRC_HOOK" "$HOOKS_DIR/checkpoint_session_hook.py"
chmod +x "$HOOKS_DIR/checkpoint_session_hook.py"
echo "✓ Hook script: $HOOKS_DIR/checkpoint_session_hook.py"

# Install skills
SKILLS_DIR="$CLAUDE_DIR/skills"
for skill in checkpoint-save checkpoint-review checkpoint-plan checkpoint-next checkpoint-audit; do
  mkdir -p "$SKILLS_DIR/$skill"
  cp "$REPO_ROOT/skills/$skill/SKILL.md" "$SKILLS_DIR/$skill/SKILL.md"
  echo "✓ Skill: $skill"
done

# Merge hooks into settings.json
mkdir -p "$CLAUDE_DIR"
[ -f "$SETTINGS" ] || echo '{}' > "$SETTINGS"

PYTHON3=$(command -v python3)

if $GLOBAL; then
  HOOK_CMD="$PYTHON3 \"$HOOKS_DIR/checkpoint_session_hook.py\""
else
  HOOK_CMD='python3 "$(git rev-parse --show-toplevel)/.claude/hooks/checkpoint_session_hook.py"'
fi

MERGE_PY=$(mktemp /tmp/checkpoint_merge_XXXXXX.py)
cat > "$MERGE_PY" << 'PYEOF'
import json, sys, pathlib

settings_path = pathlib.Path(sys.argv[1])
hook_cmd = sys.argv[2]
settings = json.loads(settings_path.read_text(encoding="utf-8")) if settings_path.stat().st_size > 0 else {}

hooks = settings.setdefault("hooks", {})
MARKER = "checkpoint_session_hook.py"

entries = [
    ("SessionStart",     "startup|resume|clear|compact", 10,  "Initializing checkpoint session log"),
    ("UserPromptSubmit", None,                           30,  "Recording checkpoint session prompt"),
    ("PreCompact",       "manual|auto",                  10,  "Recording pre-compact boundary"),
    ("PostCompact",      "manual|auto",                  10,  "Recording compact boundary"),
]

for event, matcher, timeout, status_msg in entries:
    existing = hooks.setdefault(event, [])
    already = any(
        MARKER in h.get("command", "")
        for entry in existing
        for h in entry.get("hooks", [])
    )
    if already:
        print(f"  ~ {event}: already registered")
        continue
    hook_obj = {"type": "command", "command": hook_cmd, "timeout": timeout, "statusMessage": status_msg}
    entry = {"hooks": [hook_obj]}
    if matcher:
        entry["matcher"] = matcher
    existing.append(entry)
    print(f"  ✓ {event}")

settings_path.write_text(json.dumps(settings, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
PYEOF

python3 "$MERGE_PY" "$SETTINGS" "$HOOK_CMD"
rm -f "$MERGE_PY"

echo ""
echo "Done. Restart Claude Code to apply."
