#!/usr/bin/env bash
# install-claude.sh — install the checkpoint skill and its compaction hook for Claude Code
#
# Usage:
#   bash scripts/install-claude.sh          # global install (~/.claude/)
#   bash scripts/install-claude.sh --local  # current project only (./.claude/)

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
  CLAUDE_DIR="$PWD/.claude"
  echo "Project install: $CLAUDE_DIR"
fi

if ! command -v python3 &>/dev/null; then
  echo "Error: python3 is required." >&2
  exit 1
fi

HOOKS_DIR="$CLAUDE_DIR/hooks"
SKILLS_DIR="$CLAUDE_DIR/skills"
SETTINGS="$CLAUDE_DIR/settings.json"
HOOK_NAME="checkpoint_compact_hook.py"

# Hook script; the old per-prompt logger is replaced
mkdir -p "$HOOKS_DIR"
cp "$REPO_ROOT/hooks/$HOOK_NAME" "$HOOKS_DIR/$HOOK_NAME"
chmod +x "$HOOKS_DIR/$HOOK_NAME"
rm -f "$HOOKS_DIR/checkpoint_session_hook.py"
echo "✓ Hook script: $HOOKS_DIR/$HOOK_NAME"

# Skill; the six checkpoint-* skills of earlier versions are removed
for old in checkpoint-save checkpoint-review checkpoint-plan checkpoint-next checkpoint-audit checkpoint-viz; do
  if [ -d "$SKILLS_DIR/$old" ]; then
    rm -rf "${SKILLS_DIR:?}/$old"
    echo "  - removed old skill: $old"
  fi
done
rm -rf "${SKILLS_DIR:?}/checkpoint"
mkdir -p "$SKILLS_DIR"
cp -R "$REPO_ROOT/skills/checkpoint" "$SKILLS_DIR/checkpoint"
echo "✓ Skill: $SKILLS_DIR/checkpoint"

# Register the hook in settings.json
[ -f "$SETTINGS" ] || echo '{}' > "$SETTINGS"
if $GLOBAL; then
  HOOK_CMD="$(command -v python3) \"$HOOKS_DIR/$HOOK_NAME\""
else
  HOOK_CMD="python3 \"\$CLAUDE_PROJECT_DIR/.claude/hooks/$HOOK_NAME\""
fi

python3 - "$SETTINGS" "$HOOK_CMD" <<'PYEOF'
import json, pathlib, sys

path = pathlib.Path(sys.argv[1])
cmd = sys.argv[2]
text = path.read_text(encoding="utf-8")
settings = json.loads(text) if text.strip() else {}
hooks = settings.setdefault("hooks", {})
markers = ("checkpoint_session_hook.py", "checkpoint_compact_hook.py")

# Drop every checkpoint entry, including the four events earlier versions registered.
for event in list(hooks):
    kept = []
    for entry in hooks[event]:
        entry["hooks"] = [h for h in entry.get("hooks", []) if not any(m in h.get("command", "") for m in markers)]
        if entry["hooks"]:
            kept.append(entry)
    if kept:
        hooks[event] = kept
    else:
        del hooks[event]

hooks.setdefault("SessionStart", []).append({
    "matcher": "compact",
    "hooks": [{"type": "command", "command": cmd, "timeout": 10}],
})
path.write_text(json.dumps(settings, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("✓ Hook registered: SessionStart(compact)")
PYEOF

echo ""
echo "Done. Restart Claude Code to apply."
