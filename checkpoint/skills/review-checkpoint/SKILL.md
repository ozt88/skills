---
name: review-checkpoint
description: Review a long, compacted, or drifting session to decide whether it should continue or be closed with save-checkpoint. Use after PostCompact, when context rot or task drift is suspected, when the user changes topics during active work, or when a session boundary needs to be explained. May write session-local rollups, but never writes authoritative checkpoint graph state.
---

# Review Checkpoint

Use this skill to review the current session boundary.

It can be invoked manually when the user notices context drift, or automatically after `PostCompact`.

`review-checkpoint` starts the checkpoint lifecycle. It does not save or plan by itself:

```text
review-checkpoint -> save-checkpoint -> plan-checkpoint when needed -> clear/new session -> next-checkpoint
```

## Core Rule

Explain whether the session should continue or be closed.

Do not make authoritative graph changes. Do not run `save-checkpoint` automatically.

Hooks may trigger this skill, but hooks must not replace it. Hooks record evidence; this skill reviews the boundary and talks to the user.

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
5. Ask whether to continue or close the session with `save-checkpoint`.

Do not call this "completed work" unless the completion is already explicit. Prefer "request flow", "session flow", or "pre-compact flow".

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
- archive or rotate active prompt events into a segment file
- keep the rollup non-authoritative

Forbidden:

- modify `.checkpoint/graphs/**`
- write graph `index.md`
- write graph `DECISIONS.md`
- mark nodes Done/Blocked/Ready
- run `save-checkpoint`, `plan-checkpoint`, `next-checkpoint`, or `audit-checkpoint` automatically

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

PostCompact
  -> append compact event
  -> return a systemMessage requiring review-checkpoint before continuing
```

`PostCompact` should not ask the user to run `review-checkpoint`; it should trigger the review through the hook channel available in Codex. The review then asks the user whether to continue or save.

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
