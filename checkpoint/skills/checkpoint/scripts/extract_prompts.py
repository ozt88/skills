#!/usr/bin/env python3
"""Print the user prompts of a Claude Code or Codex transcript, with compaction markers.

Usage: extract_prompts.py <transcript.jsonl> [--limit N] [--max-chars N]

Transcript formats are not a stable interface in either runtime. Unknown lines are
skipped; if nothing is recognized the script exits 2 so the caller can fall back to
the compacted summary.
"""
import argparse
import json
import re
import sys

# Context blocks the harness injects into user turns; they are not what the user typed.
INJECTED = re.compile(
    r"^\s*<(system-reminder|ide_opened_file|ide_selection|task-notification|local-command-stdout"
    r"|local-command-caveat|environment_context|user_instructions)\b.*?</\1>\s*",
    re.DOTALL,
)
COMMAND = re.compile(r"<command-name>(.*?)</command-name>.*?(?:<command-args>(.*?)</command-args>)?", re.DOTALL)


def clean(text: str) -> str:
    m = COMMAND.search(text)
    if m:
        return f"{m.group(1).strip()} {(m.group(2) or '').strip()}".strip()
    prev = None
    while prev != text:
        prev, text = text, INJECTED.sub("", text, count=1)
    return text.strip()


def text_of(content) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = [b.get("text", "") for b in content if isinstance(b, dict) and b.get("type") in ("text", "input_text")]
        return "\n".join(clean(p) for p in parts if p)
    return ""


def events(path: str):
    """Yield ("prompt", text) or ("compact", trigger) in transcript order."""
    codex_event_prompts = []
    codex_item_prompts = []
    with open(path, encoding="utf-8", errors="replace") as f:
        for line in f:
            try:
                j = json.loads(line)
            except json.JSONDecodeError:
                continue
            t = j.get("type")
            # Claude Code
            if t == "system" and j.get("subtype") == "compact_boundary":
                yield "compact", (j.get("compactMetadata") or {}).get("trigger", "")
            elif t == "user" and isinstance(j.get("message"), dict):
                if j.get("isMeta") or j.get("isCompactSummary"):
                    continue
                text = clean(text_of(j["message"].get("content")))
                if text and not text.startswith("[Request interrupted"):
                    yield "prompt", text
            # Codex rollout
            elif t == "compacted":
                yield "compact", ""
            elif t == "event_msg" and (j.get("payload") or {}).get("type") == "user_message":
                text = clean(str(j["payload"].get("message", "")))
                if text:
                    codex_event_prompts.append(text)
                    yield "prompt", text
            elif t == "response_item":
                p = j.get("payload") or {}
                if p.get("type") == "message" and p.get("role") == "user":
                    text = clean(text_of(p.get("content")))
                    if text:
                        codex_item_prompts.append(text)
    # Older Codex rollouts have no event_msg; fall back to response items.
    if not codex_event_prompts:
        for text in codex_item_prompts:
            yield "prompt", text


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("transcript")
    ap.add_argument("--limit", type=int, default=60, help="print only the last N prompts")
    ap.add_argument("--max-chars", type=int, default=300, help="truncate each prompt")
    args = ap.parse_args()
    try:
        evs = list(events(args.transcript))
    except OSError as e:
        print(f"cannot read transcript: {e}", file=sys.stderr)
        return 2
    prompts = [e for e in evs if e[0] == "prompt"]
    if not prompts:
        print("no user prompts recognized; the transcript format may have changed", file=sys.stderr)
        return 2
    keep_from = prompts[-args.limit] if len(prompts) > args.limit else prompts[0]
    start = evs.index(keep_from)
    if start:
        print(f"... {len(prompts) - args.limit} earlier prompts omitted")
    n = len(prompts) - min(len(prompts), args.limit)
    for kind, val in evs[start:]:
        if kind == "compact":
            print(f"--- compaction {val} ---".replace("  ", " "))
            continue
        n += 1
        one = " ".join(val.split())
        if len(one) > args.max_chars:
            one = one[: args.max_chars] + "…"
        print(f"{n}. {one}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
