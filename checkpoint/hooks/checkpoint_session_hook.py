#!/usr/bin/env python3
"""Lightweight session evidence hook for checkpoint.

This script records minimal session-local evidence. It never writes
authoritative checkpoint graph state.
"""

from __future__ import annotations

import hashlib
import json
import os
import pathlib
import secrets
import sys
from datetime import datetime, timezone


SCHEMA_VERSION = 1


def now_iso() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def safe_session_id(raw: str | None) -> str:
    if raw:
        keep = []
        for ch in raw:
            keep.append(ch if ch.isalnum() or ch in "-_" else "-")
        value = "".join(keep).strip("-")
        if value:
            return value[:96]
    return datetime.now().strftime("%Y%m%d-%H%M%S") + "-" + secrets.token_hex(2)


def read_input() -> dict:
    raw = sys.stdin.buffer.read().decode("utf-8", errors="replace")
    if not raw.strip():
        return {}
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {"_invalid_json": True}


def find_repo_root(cwd: str | None) -> pathlib.Path:
    start = pathlib.Path(cwd or os.getcwd()).resolve()
    cur = start
    while True:
        if (cur / ".git").exists():
            return cur
        if cur.parent == cur:
            return start
        cur = cur.parent


def write_json(path: pathlib.Path, payload: dict) -> None:
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def append_jsonl(path: pathlib.Path, payload: dict) -> None:
    with path.open("a", encoding="utf-8", newline="\n") as fh:
        fh.write(json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + "\n")


def load_state(path: pathlib.Path) -> dict:
    if not path.exists():
        return {"schema_version": SCHEMA_VERSION, "prompt_count": 0, "compact_count": 0}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {"schema_version": SCHEMA_VERSION, "prompt_count": 0, "compact_count": 0}


def rollup_count(session_dir: pathlib.Path) -> int:
    rollups_dir = session_dir / "rollups"
    if not rollups_dir.exists():
        return 0
    return len([path for path in rollups_dir.glob("*.md") if path.is_file()])


def pending_compact_review(session_dir: pathlib.Path, state: dict) -> dict | None:
    compact_count = int(state.get("compact_count", 0))
    if compact_count <= 0:
        return None
    reviewed_count = max(
        int(state.get("reviewed_compact_count", 0)),
        rollup_count(session_dir),
    )
    if reviewed_count >= compact_count:
        return None
    return {
        "compact_count": compact_count,
        "reviewed_compact_count": reviewed_count,
        "trigger": state.get("last_compact_trigger"),
        "turn_id": state.get("last_compact_turn_id"),
    }


def compact_review_context(pending: dict) -> str:
    trigger = pending.get("trigger") or "unknown"
    turn_id = pending.get("turn_id") or "unknown"
    compact_count = pending.get("compact_count")
    reviewed_count = pending.get("reviewed_compact_count")
    return (
        "Checkpoint PostCompact review is pending. "
        f"compact_count={compact_count}, reviewed_compact_count={reviewed_count}, "
        f"trigger={trigger}, turn_id={turn_id}. "
        "Before handling the user's new request, invoke the `review-checkpoint` skill, "
        "review the compacted session flow, and write a session-local rollup under "
        "`.checkpoint/sessions/<session_id>/rollups/` when possible. "
        "After that, ask whether to continue or close the session with `save-checkpoint`."
    )


def prompt_excerpt(prompt: str, n: int = 180) -> tuple[str, str]:
    prompt = prompt.encode("utf-8", errors="replace").decode("utf-8")
    text = " ".join(prompt.split())
    if len(text) <= n * 2:
        return text, text
    return text[:n], text[-n:]


def ensure_session_dir(repo_root: pathlib.Path, hook_input: dict) -> tuple[pathlib.Path, str]:
    session_id = safe_session_id(hook_input.get("session_id"))
    session_dir = repo_root / ".checkpoint" / "sessions" / session_id
    session_dir.mkdir(parents=True, exist_ok=True)
    session_json = session_dir / "session.json"
    if not session_json.exists():
        write_json(
            session_json,
            {
                "session_id": session_id,
                "created_at": now_iso(),
                "status": "active",
                "started_from_checkpoint": False,
                "source_checkpoint_ref": None,
                "source_graph_ref": None,
                "produced_checkpoint_refs": [],
                "schema_version": SCHEMA_VERSION,
            },
        )
    return session_dir, session_id


def handle_session_start(session_dir: pathlib.Path, hook_input: dict) -> dict:
    source = str(hook_input.get("source") or "unknown")
    state_path = session_dir / "state.json"
    state = load_state(state_path)
    state["last_start_source"] = source
    state["updated_at"] = now_iso()
    write_json(state_path, state)

    append_jsonl(
        session_dir / "events.jsonl",
        {
            "e": "session_start",
            "ts": now_iso(),
            "source": source,
            "model": hook_input.get("model"),
        },
    )
    if source == "compact":
        pending = pending_compact_review(session_dir, state)
        if pending:
            append_jsonl(
                session_dir / "events.jsonl",
                {
                    "e": "post_compact_review_reminder",
                    "ts": now_iso(),
                    "source": "session_start",
                    "compact_count": pending.get("compact_count"),
                    "reviewed_compact_count": pending.get("reviewed_compact_count"),
                },
            )
            return {
                "continue": True,
                "suppressOutput": True,
                "hookSpecificOutput": {
                    "hookEventName": "SessionStart",
                    "additionalContext": compact_review_context(pending),
                },
            }
    return {"continue": True, "suppressOutput": True}


def handle_user_prompt(session_dir: pathlib.Path, hook_input: dict) -> dict:
    prompt = str(hook_input.get("prompt") or "")
    prompt = prompt.encode("utf-8", errors="replace").decode("utf-8")
    lead, tail = prompt_excerpt(prompt)
    digest = hashlib.sha256(prompt.encode("utf-8", errors="replace")).hexdigest()[:16]

    state_path = session_dir / "state.json"
    state = load_state(state_path)
    state["prompt_count"] = int(state.get("prompt_count", 0)) + 1
    state["updated_at"] = now_iso()
    write_json(state_path, state)

    append_jsonl(
        session_dir / "events.jsonl",
        {
            "e": "user_prompt",
            "ts": now_iso(),
            "turn_id": hook_input.get("turn_id"),
            "hash": f"sha256:{digest}",
            "len": len(prompt),
            "lead": lead,
            "tail": tail,
        },
    )
    pending = pending_compact_review(session_dir, state)
    if pending:
        append_jsonl(
            session_dir / "events.jsonl",
            {
                "e": "post_compact_review_reminder",
                "ts": now_iso(),
                "source": "user_prompt",
                "turn_id": hook_input.get("turn_id"),
                "compact_count": pending.get("compact_count"),
                "reviewed_compact_count": pending.get("reviewed_compact_count"),
            },
        )
        return {
            "continue": True,
            "suppressOutput": True,
            "hookSpecificOutput": {
                "hookEventName": "UserPromptSubmit",
                "additionalContext": compact_review_context(pending),
            },
        }
    return {"continue": True, "suppressOutput": True}


def handle_pre_compact(session_dir: pathlib.Path, hook_input: dict) -> dict:
    trigger = str(hook_input.get("trigger") or "unknown")
    state_path = session_dir / "state.json"
    state = load_state(state_path)
    state["pre_compact_count"] = int(state.get("pre_compact_count", 0)) + 1
    state["last_pre_compact_trigger"] = trigger
    state["last_pre_compact_turn_id"] = hook_input.get("turn_id")
    state["updated_at"] = now_iso()
    write_json(state_path, state)

    append_jsonl(
        session_dir / "events.jsonl",
        {
            "e": "pre_compact",
            "ts": now_iso(),
            "turn_id": hook_input.get("turn_id"),
            "trigger": trigger,
            "pre_compact_count": state.get("pre_compact_count", 0),
            "action": "record_compact_boundary",
        },
    )
    return {"continue": True, "suppressOutput": True}


def handle_post_compact(session_dir: pathlib.Path, hook_input: dict) -> dict:
    trigger = str(hook_input.get("trigger") or "unknown")
    state_path = session_dir / "state.json"
    state = load_state(state_path)
    state["compact_count"] = int(state.get("compact_count", 0)) + 1
    state["last_compact_trigger"] = trigger
    state["last_compact_turn_id"] = hook_input.get("turn_id")
    if trigger == "auto":
        state["auto_compact_count"] = int(state.get("auto_compact_count", 0)) + 1
    elif trigger == "manual":
        state["manual_compact_count"] = int(state.get("manual_compact_count", 0)) + 1
    state["updated_at"] = now_iso()
    write_json(state_path, state)

    append_jsonl(
        session_dir / "events.jsonl",
        {
            "e": "post_compact",
            "ts": now_iso(),
            "turn_id": hook_input.get("turn_id"),
            "trigger": trigger,
            "compact_count": state.get("compact_count", 0),
            "auto_compact_count": state.get("auto_compact_count", 0),
            "action": "invoke_review_checkpoint",
        },
    )

    message = (
        "PostCompact occurred. A checkpoint review is pending. "
        "The next UserPromptSubmit hook will inject `review-checkpoint` context before the agent continues."
    )
    return {"continue": True, "systemMessage": message, "suppressOutput": True}


def main() -> int:
    hook_input = read_input()
    repo_root = find_repo_root(hook_input.get("cwd"))
    session_dir, _ = ensure_session_dir(repo_root, hook_input)
    event = hook_input.get("hook_event_name")

    if event == "SessionStart":
        out = handle_session_start(session_dir, hook_input)
    elif event == "UserPromptSubmit":
        out = handle_user_prompt(session_dir, hook_input)
    elif event == "PreCompact":
        out = handle_pre_compact(session_dir, hook_input)
    elif event == "PostCompact":
        out = handle_post_compact(session_dir, hook_input)
    else:
        append_jsonl(session_dir / "events.jsonl", {"e": "ignored", "ts": now_iso(), "event": event})
        out = {"continue": True, "suppressOutput": True}

    sys.stdout.buffer.write(json.dumps(out, ensure_ascii=False).encode("utf-8"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
