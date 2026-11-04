#!/usr/bin/env bash
# install-claude.sh — install the worklog skill for Claude Code
#
# Usage:
#   bash scripts/install-claude.sh

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SKILLS_DIR="$HOME/.claude/skills"

if ! command -v python3 &>/dev/null; then
  echo "Error: python3 is required." >&2
  exit 1
fi

rm -rf "${SKILLS_DIR:?}/worklog"
mkdir -p "$SKILLS_DIR"
cp -R "$REPO_ROOT/skills/worklog" "$SKILLS_DIR/worklog"
find "$SKILLS_DIR/worklog" -name __pycache__ -prune -exec rm -rf {} +
chmod +x "$SKILLS_DIR/worklog/scripts/"*
echo "✓ Skill: $SKILLS_DIR/worklog"
