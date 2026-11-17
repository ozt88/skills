#!/usr/bin/env bash
# install-claude.sh — install the noclip skill for Claude Code
#
# Usage:
#   bash scripts/install-claude.sh

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SKILLS_DIR="$HOME/.claude/skills"

rm -rf "${SKILLS_DIR:?}/noclip"
mkdir -p "$SKILLS_DIR"
cp -R "$REPO_ROOT/skills/noclip" "$SKILLS_DIR/noclip"
echo "✓ Skill: $SKILLS_DIR/noclip"
