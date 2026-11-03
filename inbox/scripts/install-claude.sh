#!/usr/bin/env bash
# install-claude.sh — install the inbox mod for Claude Code
#
# Usage:
#   bash scripts/install-claude.sh
#
# Copies the mod to ~/.claude/mods/inbox and adds that folder to env.CLAUDE_CODE_PLUGIN_DIRS in
# ~/.claude/settings.json. The morning task is set up from the app; see README.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
CLAUDE_DIR="$HOME/.claude"
MOD_DIR="$CLAUDE_DIR/mods/inbox"
SETTINGS="$CLAUDE_DIR/settings.json"

PY="$(command -v python3 || command -v python || true)"
if [ -z "$PY" ]; then
  echo "Error: python3 is required." >&2
  exit 1
fi

rm -rf "${MOD_DIR:?}"
mkdir -p "$MOD_DIR"
# The engine writes .claude-plugin/types on load; copying an old one would only go stale.
(cd "$REPO_ROOT/mod" && tar --exclude=.claude-plugin/types -cf - .) | (cd "$MOD_DIR" && tar -xf -)
echo "✓ Mod: $MOD_DIR"

[ -f "$SETTINGS" ] || echo '{}' > "$SETTINGS"
"$PY" - "$SETTINGS" "$MOD_DIR" <<'PYEOF'
import json, os, pathlib, sys

path, mod_dir = pathlib.Path(sys.argv[1]), sys.argv[2]
text = path.read_text(encoding="utf-8")
settings = json.loads(text) if text.strip() else {}

env = settings.setdefault("env", {})
# Drop an earlier registration so re-running does not add a second one.
dirs = [d for d in env.get("CLAUDE_CODE_PLUGIN_DIRS", "").split(os.pathsep) if d and d != mod_dir]
dirs.append(mod_dir)
env["CLAUDE_CODE_PLUGIN_DIRS"] = os.pathsep.join(dirs)

path.write_text(json.dumps(settings, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("✓ Mod registered: env.CLAUDE_CODE_PLUGIN_DIRS")
PYEOF

echo ""
echo "Todo list: ~/inbox/todo.md (set INBOX_DIR to use another folder)."
echo "Restart Claude Code to apply."
