---
name: review-checkpoint
description: Review a long, compacted, or drifting session to decide whether it should continue or be closed with save-checkpoint. Use after PostCompact, when context rot or task drift is suspected, when the user changes topics during active work, or when a session boundary needs to be explained. May write session-local rollups, but never writes authoritative checkpoint graph state.
---

# Review Checkpoint

Use this skill to review the current session boundary.

It can be invoked manually when the user notices context drift, or when hook-injected context says a `PostCompact` review is pending.

`review-checkpoint` starts the checkpoint lifecycle. It does not save or plan by itself:

```text
review-checkpoint -> save-checkpoint -> plan-checkpoint when needed -> clear/new session -> next-checkpoint
```

## Core Rule

Explain whether the session should continue or be closed.

Do not make authoritative graph changes. Do not run `save-checkpoint` automatically.

Hooks may request this skill, but hooks must not replace it. Hooks record evidence and may inject next-turn context; this skill reviews the boundary and talks to the user.

## Review Inputs

Use the best available evidence:

- current conversation flow
- latest user request
- compact/resume context
- optional session-local logs under `.checkpoint/sessions/<session_id>/`
- local files only when needed to explain a boundary risk

Session logs are optional evidence. Never fail because logs are missing.

## PostCompact Review

When invoked after `PostCompact`:

1. State that context compaction occurred.
2. Summarize the pre-compact request flow from current context and optional logs.
3. Identify possible drift or branching without treating it as a final verdict.
4. If session logs exist, compile the just-ended segment into a session-local rollup.
5. If `state.json` exists, update `reviewed_compact_count` to the compact count covered by the rollup.
6. Ask whether to continue or close the session with `save-checkpoint`.

Do not call this "completed work" unless the completion is already explicit. Prefer "request flow", "session flow", or "pre-compact flow".

The pending compact review is not complete until the pending state is cleared. Clear it by doing at least one of:

- write a rollup under `.checkpoint/sessions/<session_id>/rollups/*.md`
- update `.checkpoint/sessions/<session_id>/state.json` so `reviewed_compact_count` is greater than or equal to `compact_count`

If neither happens, the hook should keep injecting `review-checkpoint` context on later prompts.

## Session-Local Rollup

If `.checkpoint/sessions/<session_id>/` exists, `review-checkpoint` may maintain session-local files:

```text
.checkpoint/sessions/<session_id>/
  session.json
  events.jsonl
  rollups/
    001-post-compact.md
```

Allowed:

- write a compact boundary rollup
- update `state.json` `reviewed_compact_count` after the rollup is written
- archive or rotate active prompt events into a segment file
- keep the rollup non-authoritative

Forbidden:

- modify `.checkpoint/graphs/**`
- write graph `index.md`
- write graph `DECISIONS.md`
- mark nodes Done/Blocked/Ready
- run `save-checkpoint`, `plan-checkpoint`, `next-checkpoint`, or `audit-checkpoint` automatically

### Clearing Pending Review State

When `review-checkpoint` is invoked because hook-injected context says `PostCompact` review is pending:

1. Use the exact `session_id` from the hook-injected context when present.
2. Read `.checkpoint/sessions/<session_id>/state.json`.
3. Read nearby `events.jsonl` entries around the latest `post_compact`.
4. Write a rollup such as `rollups/001-post-compact.md`.
5. Update `state.json`:

```json
{
  "reviewed_compact_count": 1,
  "last_reviewed_at": "<ISO timestamp>"
}
```

Set `reviewed_compact_count` to the `compact_count` that the rollup covers. Preserve existing state keys.

Do not guess the session by newest directory if the injected context includes `session_id`; stale compact reminders can come from an older resumed session.

### Rollup Content

The rollup should be a session-flow review, not an authoritative work report:

```md
# PostCompact Review

## Compact Facts
- trigger:
- compact count:
- source:

## Pre-Compact Request Flow
- ...

## Possible Drift Or Branching
- ...

## Handoff Risk
- ...

## Recommendation
- continue | save-checkpoint recommended
```

Do not claim decisions were accepted unless they are explicit. Do not infer completed work from prompt flow alone.

## Hook Integration

Expected integration:

```text
SessionStart
  -> initialize session.json and append session_start source

UserPromptSubmit
  -> append prompt hash/len/lead/tail to events.jsonl

PreCompact
  -> append pre-compact boundary before context is rewritten

PostCompact
  -> append compact event
  -> mark compact review as pending

SessionStart(source=compact) or UserPromptSubmit
  -> if compact review is still pending
  -> inject additionalContext requiring review-checkpoint
```

`PreCompact` gives the review a more stable boundary marker before compaction rewrites context. `PostCompact` should not ask the user to run `review-checkpoint`; it should persist pending review state after compaction succeeds. Because Codex does not route `PostCompact` output into model-visible context, the next context-injecting hook must carry the review requirement. The review then asks the user whether to continue or save.

## Classify The New Request

Classify a new request as one of:

- Same active problem: continue without asking.
- New slice of the same problem: continue or suggest saving if it may span sessions.
- Separate problem or context switch: save the current session first, then switch only after user confirms.
- Existing checkpoint resume: do not handle here; the user should call `next-checkpoint` directly.

## User Prompt

When the boundary matters, offer only relevant choices:

```text
현재 세션 경계를 검토했습니다.

요약:
- <pre-compact/session flow>
- <possible drift or branch>
- <risk if continued>

어떻게 할까요?

1. 현재 세션에서 계속 진행
2. save-checkpoint로 현재 세션을 닫고 다음 세션을 준비
```

If only pre-compaction risk exists, use:

```text
세션이 길어져서 현재 작업을 save-checkpoint로 저장해두는 편이 안전해 보입니다. 계속 진행할까요, 아니면 먼저 저장할까요?
```

## Delegation

- Use `save-checkpoint` when the user wants to preserve current or existing session work.
- Use `plan-checkpoint` only after the current session has been saved or when the user explicitly asks to prepare future work.
- Use `next-checkpoint` only in a fresh or resumed session that is opening existing checkpoint work.
- Use `audit-checkpoint` only to validate checkpoint artifacts.

## Do Not Over-Interrupt

If the user recently declined saving or splitting, do not ask again unless:

- the task becomes substantially larger,
- another compact/resume boundary occurs,
- or new evidence shows important context may be lost.
