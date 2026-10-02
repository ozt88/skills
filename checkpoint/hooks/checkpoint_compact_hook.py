#!/usr/bin/env python3
"""SessionStart(compact) hook for Claude Code and Codex.

After a compaction, adds a reminder to the model's context to run `checkpoint review`,
with the transcript path so the review can see what was asked before the compaction.
Records nothing on disk.
"""
import json
import sys


def main() -> int:
    raw = sys.stdin.buffer.read().decode("utf-8", errors="replace")
    try:
        hook_input = json.loads(raw) if raw.strip() else {}
    except json.JSONDecodeError:
        hook_input = {}

    if hook_input.get("hook_event_name") != "SessionStart" or hook_input.get("source") != "compact":
        print(json.dumps({"continue": True, "suppressOutput": True}))
        return 0

    transcript = hook_input.get("transcript_path") or "not provided"
    context = (
        "The conversation was just compacted. Before handling the next request, run the "
        "`checkpoint` skill with the `review` subcommand to decide whether this is a work "
        f"boundary worth saving. transcript_path: {transcript}"
    )
    print(json.dumps({
        "continue": True,
        "suppressOutput": True,
        "hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": context},
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
