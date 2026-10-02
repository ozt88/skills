# review

Decide whether the session has reached a work boundary and, if so, offer to save. Never write graph files.

## Signals

Judge from the conversation itself:
- The user moved to a task unrelated to the work so far.
- The same problem has been corrected more than twice, so failed attempts now fill the context.
- A task just finished and the next request is a different slice of work.
- A compaction happened (the hook reminder says so).

Session length or token count alone is not a signal. Do not cut work short because the context is large. If the user is still on the same problem, continue without asking.

## After a compaction

The hook reminder carries `transcript_path`. To see what was asked before the compaction, run from this skill's directory:

```bash
python3 scripts/extract_prompts.py <transcript_path>
```

It prints the user prompts in order with `--- compaction ---` markers. If the path is missing or the script exits non-zero, judge from the compacted summary and say that you did.

## Reply

Two to four lines: what the session has covered, the boundary you see, and the risk of continuing in this context. Then offer two choices: continue here, or `/checkpoint save` followed by `/clear`.

If the user declined recently, do not ask again until a new boundary or another compaction appears.
