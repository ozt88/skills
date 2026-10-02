#!/usr/bin/env bash
# install-codex.sh — install the checkpoint skill and its compaction hook for Codex
#
# Usage:
#   bash scripts/install-codex.sh

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
CODEX_DIR="$HOME/.codex"
HOOKS_DIR="$CODEX_DIR/hooks"
SKILLS_DIR="$CODEX_DIR/skills"
CONFIG_TOML="$CODEX_DIR/config.toml"
HOOK_NAME="checkpoint_compact_hook.py"

if ! command -v python3 &>/dev/null; then
  echo "Error: python3 is required." >&2
  exit 1
fi

echo "Codex install: $CODEX_DIR"

# 1. Hook script; the old per-prompt logger is replaced
mkdir -p "$HOOKS_DIR"
cp "$REPO_ROOT/hooks/$HOOK_NAME" "$HOOKS_DIR/$HOOK_NAME"
chmod +x "$HOOKS_DIR/$HOOK_NAME"
rm -f "$HOOKS_DIR/checkpoint_session_hook.py"
echo "✓ Hook script: $HOOKS_DIR/$HOOK_NAME"

# 2. Skill; the checkpoint-* skills of earlier versions are removed
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

# 3. Replace the managed hook block in config.toml
mkdir -p "$CODEX_DIR"
[ -f "$CONFIG_TOML" ] || : > "$CONFIG_TOML"
MARKER_BEGIN="# BEGIN checkpoint managed hooks"
MARKER_END="# END checkpoint managed hooks"

python3 - "$CONFIG_TOML" "$MARKER_BEGIN" "$MARKER_END" <<'PYEOF'
import pathlib, re, sys
p = pathlib.Path(sys.argv[1])
begin, end = re.escape(sys.argv[2]), re.escape(sys.argv[3])
text = p.read_text(encoding="utf-8")
text = re.sub(rf"\n?{begin}.*?{end}\n?", "\n", text, flags=re.DOTALL).rstrip()
p.write_text(text + "\n" if text else "", encoding="utf-8")
PYEOF

cat >> "$CONFIG_TOML" <<EOF

$MARKER_BEGIN
[[hooks.SessionStart]]
matcher = "compact"

[[hooks.SessionStart.hooks]]
type = "command"
command = 'python3 "$HOOKS_DIR/$HOOK_NAME"'
timeout = 10
$MARKER_END
EOF
echo "✓ Hook registered in $CONFIG_TOML: SessionStart(compact)"

# Earlier versions also wrote hooks into requirements.toml. Leave that file to its owner.
if grep -qs "checkpoint_session_hook.py" "$CODEX_DIR/requirements.toml"; then
  echo ""
  echo "! $CODEX_DIR/requirements.toml still registers checkpoint_session_hook.py from an"
  echo "  earlier install. Remove those [[hooks.*]] entries by hand."
fi

echo ""
echo "Done. Restart Codex and approve the hook with /hooks."
