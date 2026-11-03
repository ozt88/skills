#!/usr/bin/env bash
# install-claude.sh — install the adversarial-review skill for Claude Code
#
# Usage:
#   bash scripts/install-claude.sh
#
# This folder is also the Codex skill, so only the files the skill reads are copied:
# README, tests, and this script stay behind.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SKILLS_DIR="$HOME/.claude/skills"
TARGET="$SKILLS_DIR/adversarial-review"

if ! command -v python3 &>/dev/null; then
  echo "Error: python3 is required for scripts/check_review.py." >&2
  exit 1
fi

rm -rf "${TARGET:?}"
mkdir -p "$TARGET/scripts"
cp "$REPO_ROOT/SKILL.md" "$TARGET/SKILL.md"
cp -R "$REPO_ROOT/references" "$TARGET/references"
cp "$REPO_ROOT/scripts/check_review.py" "$TARGET/scripts/check_review.py"
echo "✓ Skill: $TARGET"
