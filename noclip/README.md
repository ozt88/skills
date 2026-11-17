# noclip

A session that is deep in a task picks its next step inside the frame it has already built. The assumptions holding that frame up (the walls) are hard to see from inside. noclip lets the session pass through them: just before it commits to the next action, a fresh agent checks the assumptions under the current plan against the material and hands back one alternative from outside the frame.

It does not solve the problem again from scratch. It says "before you do that, look at this", and the user decides.

Supported runtime: **Claude Code**. The procedures assume Claude Code's Agent and SendMessage tools.

## How it works

1. **Request.** The session writes `.noclip/<date>-<name>/request.md` with two parts: *facts* (goal, what was tried and what happened, fixed constraints and decisions, paths to the material) and *current plan* (the next action and why). The conversation transcript is never passed on, because it carries the frame along with it.
2. **Fast mode (default).** One new subagent gets the request and a short rules prompt. It lists the assumptions the plan rests on, sets up hypotheses that leave the plan's frame, writes for each what would confirm it and what would falsify it, then opens the material itself to check. Cost, side effects, or "something else was already approved" do not count as falsifying an alternative. If any outside hypothesis is left unfalsified, the memo cannot say "keep the plan".
3. **Intervention memo.** Both modes return the same format: a verdict (keep, revise, or replace the plan) with a one-line reason, the plan's assumptions that the material broke, one outside-the-frame alternative with file:line evidence, one to three next actions, the evidence-backed findings and obligations that must be kept, and switch conditions. A *revise* verdict must put the alternative, or a check that settles it, into the next actions; tacking a check onto the current plan alone counts as *keep*. The memo never changes the plan by itself. The session shows it to the user, who chooses.
4. **Adoption log.** After the user decides, the session records per item whether it was adopted, rejected, or modified, and why, in `adoption.md` next to the request and memo.

## When it runs

- When you type `/noclip`, or ask the session to look outside its current approach.
- The session may *suggest* it in three cases only: right before an expensive or hard-to-undo action, after fixing the same problem more than twice, or when a result differs from what was expected. It runs only after you approve.

## Example

A made-up scenario. A session has spent an hour tuning a cache eviction policy because a nightly report job keeps timing out. Its plan is to try a third policy and rerun the job.

```
/noclip
```

The session writes the request: the goal (the report finishes before 6 a.m.), the two policies tried and their run times, the constraint that the job's schedule is fixed, and paths to the job script, the cache config, and last week's run logs. The current plan goes in its own section.

The memo comes back as **Replace**. The broken assumption is "the time goes into cache misses": the logs show most of the run waiting on a single unindexed query (`logs/run-0312.txt:88-104`). The alternative is to add the index and rerun once before touching the cache again. Switch condition: if the query time stays above a few minutes after indexing, go back to cache tuning. Under *must keep*, it lists the fixed schedule as an obligation (`[의무]`), with its source. You read it, adopt the index step, reject a suggested follow-up to move the report's heaviest query into a materialized view, and the session logs both decisions.

## Fast mode and seat mode

| | Fast mode (default) | Seat mode (experimental) |
|---|---|---|
| What runs | one subagent with a rules prompt | a vector generator, 2 to 3 exploration seats with different starting hypotheses and forbidden zones, one exchange round, a Judge; plus the fast mode on the same request |
| Who sees the current plan | the subagent | only the session and the Judge; seats get the facts only |
| Typical cost | about 1 to 2 USD, 2 to 4 minutes | about 5 to 10 USD for the seats, 15 to 30 minutes, plus 1 to 2 USD for the paired fast mode |
| When | every call by default | only when you name it explicitly |

Seat mode is experimental because, in a small blind comparison on a few past decisions with known outcomes, the seats did not clearly beat the single rules-driven agent. They came out ahead on a minority of cases, were not better at pushing the outside alternative into the main recommendation, and their conclusions were less directly actionable, at several times the cost. So every seat-mode call is a *paired run*: the fast mode runs on the same request, both memos are shown side by side without saying which is which, and the adoption log records which memo each adopted item came from. Once enough pairs pile up, you can decide whether seat mode earns its cost.

## How it differs from adversarial-review

[adversarial-review](../adversarial-review) judges a finished piece of work against your goals. noclip intervenes in work still in progress, before the next action, and returns one alternative rather than a verdict per goal.

## Files

```
skills/noclip/
  SKILL.md              when to call, request, modes, memo format, records
  references/fast.md    the fast-mode subagent prompt
  references/seats.md   seat-mode procedure (vectors, exploration and sealing, drift, exchange)
  references/judge.md   seat-mode Judge and memo
```

Each run leaves `.noclip/<date>-<name>/` in the project with `request.md`, `memo.md` (or `memo-fast.md` and `memo-seats.md` for a paired run), and `adoption.md`. A seat-mode run also leaves `seats/` with the facts, vectors, sealed seat notes, exchange notes, and the Judge's tables. If seat mode stops partway, `seats/stopped.md` records why and only `memo-fast.md` is left. Requests, memos, and `seats/` all quote paths and facts from your work, so add `.noclip/` to `.gitignore` in public repositories.

## Install

From the `noclip` directory:

```bash
bash scripts/install-claude.sh
```

This removes any existing `~/.claude/skills/noclip` and copies `skills/noclip` there, so local edits to the installed copy are lost.
