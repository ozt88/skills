#!/usr/bin/env bash
# install-claude.sh — install the knowledge-compile skill and how sessions load the index for Claude Code
#
# Usage:
#   bash scripts/install-claude.sh          # mod (default): index with the next prompt + 참조 reminder
#   bash scripts/install-claude.sh --hook   # SessionStart hook, for a Claude Code without mods
#
# Either way the other one is removed, so the index is never added twice.

set -euo pipefail

MODE=mod
case "${1:-}" in
  "") ;;
  --hook) MODE=hook ;;
  *) echo "Usage: $0 [--hook]" >&2; exit 1 ;;
esac

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
CLAUDE_DIR="$HOME/.claude"
SKILLS_DIR="$CLAUDE_DIR/skills"
HOOKS_DIR="$CLAUDE_DIR/hooks"
MOD_DIR="$CLAUDE_DIR/mods/knowledge"
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

if [ "$MODE" = mod ]; then
  rm -rf "${MOD_DIR:?}"
  mkdir -p "$MOD_DIR"
  # The engine writes .claude-plugin/types on load; copying an old one would only go stale.
  (cd "$REPO_ROOT/mod" && tar --exclude=.claude-plugin/types -cf - .) | (cd "$MOD_DIR" && tar -xf -)
  rm -f "$HOOKS_DIR/$HOOK_NAME"
  echo "✓ Mod: $MOD_DIR"
else
  mkdir -p "$HOOKS_DIR"
  cp "$REPO_ROOT/hooks/$HOOK_NAME" "$HOOKS_DIR/$HOOK_NAME"
  chmod +x "$HOOKS_DIR/$HOOK_NAME"
  rm -rf "${MOD_DIR:?}"
  echo "✓ Hook script: $HOOKS_DIR/$HOOK_NAME"
fi

# settings.json: register exactly one of the hook or the mod's folder in CLAUDE_CODE_PLUGIN_DIRS.
[ -f "$SETTINGS" ] || echo '{}' > "$SETTINGS"
HOOK_CMD="$(command -v python3) \"$HOOKS_DIR/$HOOK_NAME\""
python3 - "$SETTINGS" "$MODE" "$HOOK_CMD" "$HOOK_NAME" "$MOD_DIR" <<'PYEOF'
import json, os, pathlib, sys

path, mode, cmd, marker, mod_dir = pathlib.Path(sys.argv[1]), *sys.argv[2:]
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
if not hooks:
    del settings["hooks"]

env = settings.setdefault("env", {})
dirs = [d for d in env.get("CLAUDE_CODE_PLUGIN_DIRS", "").split(os.pathsep) if d and d != mod_dir]

if mode == "mod":
    dirs.append(mod_dir)
    print("✓ Mod registered: env.CLAUDE_CODE_PLUGIN_DIRS")
else:
    settings.setdefault("hooks", {}).setdefault("SessionStart", []).append({
        "hooks": [{"type": "command", "command": cmd, "timeout": 10}],
    })
    print("✓ Hook registered: SessionStart")

if dirs:
    env["CLAUDE_CODE_PLUGIN_DIRS"] = os.pathsep.join(dirs)
else:
    env.pop("CLAUDE_CODE_PLUGIN_DIRS", None)
if not env:
    del settings["env"]

path.write_text(json.dumps(settings, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
PYEOF

echo ""
echo "Nightly runner: $SKILLS_DIR/knowledge-compile/scripts/compile-all.sh"
echo "Schedule it hourly with cron or Windows Task Scheduler (see README)."
echo "Restart Claude Code to apply."
