#!/usr/bin/env bash
# install-claude.sh — install the knowledge-compile skill and its index hook for Claude Code
#
# Usage:
#   bash scripts/install-claude.sh

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
CLAUDE_DIR="$HOME/.claude"
SKILLS_DIR="$CLAUDE_DIR/skills"
HOOKS_DIR="$CLAUDE_DIR/hooks"
SETTINGS="$CLAUDE_DIR/settings.json"
HOOK_NAME="knowledge_index_hook.py"

if ! command -v python3 &>/dev/null; then
  echo "Error: python3 is required." >&2
  exit 1
fi

rm -rf "${SKILLS_DIR:?}/knowledge-compile"
mkdir -p "$SKILLS_DIR"
cp -R "$REPO_ROOT/skills/knowledge-compile" "$SKILLS_DIR/knowledge-compile"
chmod +x "$SKILLS_DIR/knowledge-compile/scripts/"*
echo "✓ Skill: $SKILLS_DIR/knowledge-compile"

mkdir -p "$HOOKS_DIR"
cp "$REPO_ROOT/hooks/$HOOK_NAME" "$HOOKS_DIR/$HOOK_NAME"
chmod +x "$HOOKS_DIR/$HOOK_NAME"
echo "✓ Hook script: $HOOKS_DIR/$HOOK_NAME"

# Register the hook in settings.json (SessionStart, every source)
[ -f "$SETTINGS" ] || echo '{}' > "$SETTINGS"
HOOK_CMD="$(command -v python3) \"$HOOKS_DIR/$HOOK_NAME\""
python3 - "$SETTINGS" "$HOOK_CMD" "$HOOK_NAME" <<'PYEOF'
import json, pathlib, sys

path, cmd, marker = pathlib.Path(sys.argv[1]), sys.argv[2], sys.argv[3]
text = path.read_text(encoding="utf-8")
settings = json.loads(text) if text.strip() else {}
hooks = settings.setdefault("hooks", {})

# Drop an earlier registration so re-running does not add a second one.
for event in list(hooks):
    kept = []
    for entry in hooks[event]:
        entry["hooks"] = [h for h in entry.get("hooks", []) if marker not in h.get("command", "")]
        if entry["hooks"]:
            kept.append(entry)
    if kept:
        hooks[event] = kept
    else:
        del hooks[event]

hooks.setdefault("SessionStart", []).append({
    "hooks": [{"type": "command", "command": cmd, "timeout": 10}],
})
path.write_text(json.dumps(settings, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("✓ Hook registered: SessionStart")
PYEOF

echo ""
echo "Nightly runner: $SKILLS_DIR/knowledge-compile/scripts/compile-all.sh"
echo "Schedule it hourly with cron or Windows Task Scheduler (see README)."
echo "Restart Claude Code to apply the hook."
