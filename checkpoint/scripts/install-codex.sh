#!/usr/bin/env bash
# install-codex.sh — Codex global hook installer (bash)
#
# Usage:
#   bash scripts/install-codex.sh

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
CODEX_DIR="$HOME/.codex"
HOOKS_DIR="$CODEX_DIR/hooks"
SKILLS_DIR="$CODEX_DIR/skills"
REQUIREMENTS_TOML="$CODEX_DIR/requirements.toml"
CONFIG_TOML="$CODEX_DIR/config.toml"
SRC_HOOK="$REPO_ROOT/hooks/checkpoint_session_hook.py"
TARGET_HOOK="$HOOKS_DIR/checkpoint_session_hook.py"
SRC_REQUIREMENTS="$REPO_ROOT/hooks/requirements.example.toml"

if ! command -v python3 &>/dev/null; then
  echo "Error: python3 is required." >&2
  exit 1
fi

echo "Codex install: $CODEX_DIR"

# 1. Install hook script
mkdir -p "$HOOKS_DIR"
cp "$SRC_HOOK" "$TARGET_HOOK"
chmod +x "$TARGET_HOOK"
echo "✓ Hook script: $TARGET_HOOK"

# 2. Install skills
for skill in checkpoint-save checkpoint-review checkpoint-plan checkpoint-next checkpoint-audit checkpoint-viz; do
  mkdir -p "$SKILLS_DIR/$skill"
  cp "$REPO_ROOT/skills/$skill/SKILL.md" "$SKILLS_DIR/$skill/SKILL.md"
  echo "✓ Skill: $skill"
done

# 3. Write requirements.toml from the example, replacing the Windows placeholder path
sed "s|C:\\\\Users\\\\YOUR_USER\\\\.codex\\\\hooks|$HOOKS_DIR|g" \
    "$SRC_REQUIREMENTS" > "$REQUIREMENTS_TOML"
echo "✓ Requirements: $REQUIREMENTS_TOML"

# 4. Merge managed hooks block into config.toml
mkdir -p "$CODEX_DIR"
[ -f "$CONFIG_TOML" ] || : > "$CONFIG_TOML"

MARKER_BEGIN="# BEGIN checkpoint managed hooks"
MARKER_END="# END checkpoint managed hooks"

# Remove any existing managed block (idempotent reinstall)
if grep -qF "$MARKER_BEGIN" "$CONFIG_TOML"; then
  python3 - "$CONFIG_TOML" "$MARKER_BEGIN" "$MARKER_END" <<'PYEOF'
import re, sys, pathlib
p = pathlib.Path(sys.argv[1])
begin = re.escape(sys.argv[2])
end = re.escape(sys.argv[3])
text = p.read_text(encoding="utf-8")
text = re.sub(rf"\n?{begin}.*?{end}\n?", "\n", text, flags=re.DOTALL)
p.write_text(text, encoding="utf-8")
PYEOF
fi

# Append fresh managed block
cat >> "$CONFIG_TOML" <<EOF

$MARKER_BEGIN
[hooks]
managed_dir = "~/.codex/hooks"

[[hooks.SessionStart]]
matcher = "startup|resume|clear|compact"

[[hooks.SessionStart.hooks]]
type = "command"
command = 'python3 "$TARGET_HOOK"'
timeout = 10
statusMessage = "Initializing checkpoint session log"

[[hooks.UserPromptSubmit]]

[[hooks.UserPromptSubmit.hooks]]
type = "command"
command = 'python3 "$TARGET_HOOK"'
timeout = 10
statusMessage = "Recording checkpoint session prompt"

[[hooks.PreCompact]]
matcher = "manual|auto"

[[hooks.PreCompact.hooks]]
type = "command"
command = 'python3 "$TARGET_HOOK"'
timeout = 10
statusMessage = "Recording pre-compact boundary"

[[hooks.PostCompact]]
matcher = "manual|auto"

[[hooks.PostCompact.hooks]]
type = "command"
command = 'python3 "$TARGET_HOOK"'
timeout = 10
statusMessage = "Recording compact boundary"
$MARKER_END
EOF
echo "✓ Config: $CONFIG_TOML"

# 5. Ensure [features] hooks = true
if ! grep -qE "^\s*hooks\s*=\s*true" "$CONFIG_TOML"; then
  if grep -qE "^\[features\]" "$CONFIG_TOML"; then
    # [features] exists but no hooks line — insert hooks = true under it
    python3 - "$CONFIG_TOML" <<'PYEOF'
import re, sys, pathlib
p = pathlib.Path(sys.argv[1])
text = p.read_text(encoding="utf-8")
text = re.sub(r"(\[features\]\s*\n)", r"\1hooks = true\n", text, count=1)
p.write_text(text, encoding="utf-8")
PYEOF
  else
    printf '\n[features]\nhooks = true\n' >> "$CONFIG_TOML"
  fi
  echo "✓ Enabled [features] hooks = true"
else
  echo "  ~ [features] hooks already enabled"
fi

echo ""
echo "Done. Restart Codex to apply."
