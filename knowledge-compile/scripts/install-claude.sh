#!/usr/bin/env bash
# install-claude.sh — install the knowledge-compile skill for Claude Code
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

rm -rf "${SKILLS_DIR:?}/knowledge-compile"
mkdir -p "$SKILLS_DIR"
cp -R "$REPO_ROOT/skills/knowledge-compile" "$SKILLS_DIR/knowledge-compile"
chmod +x "$SKILLS_DIR/knowledge-compile/scripts/"*
echo "✓ Skill: $SKILLS_DIR/knowledge-compile"
echo ""
echo "Nightly runner: $SKILLS_DIR/knowledge-compile/scripts/compile-all.sh"
echo "Schedule it hourly with cron or Windows Task Scheduler (see README)."
