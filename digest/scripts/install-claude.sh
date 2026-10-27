#!/usr/bin/env bash
# install-claude.sh — install the digest skill for Claude Code
#
# Usage:
#   bash scripts/install-claude.sh

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SKILLS_DIR="$HOME/.claude/skills"

rm -rf "${SKILLS_DIR:?}/digest"
mkdir -p "$SKILLS_DIR"
cp -R "$REPO_ROOT/skills/digest" "$SKILLS_DIR/digest"
echo "✓ Skill: $SKILLS_DIR/digest"
