---
name: orchestration
description: Use in the codex-orchestrator coordinator for substantial development with native dev-* subagents, and for worktree commits or completion. Not for a specialist carrying out an assigned subtask.
---

# Orchestration

Coordinate one task at a time through native Codex agents. You own the task note, checks,
review decisions and Git operations. Use this workflow instead of another
orchestration playbook. A tiny safe change may be handled directly with its checks.

Roles share the parent session's permissions. Read-only assignments and the
no-delegation rule are behavioral instructions, not separate enforced sandboxes.

## Establish the task

Read repository guidance and any `.agent-task.md`. Confirm the original checkout,
task checkout, base SHA, intended integration branch, owned paths, acceptance
criteria and actual check commands. Record the agreed delivery scope and its
authorization; the starting branch alone does not authorize integration. Preserve
user changes. Use one task worktree for substantial work; all assigned agents work
in that checkout, with only one writer at a time.

Before a cloud-backed implementation call, establish authorization for this
repository and record it in the note. Reuse explicit authorization already given
for that repository; do not infer it from another project.

Keep `.agent-task.md` locally excluded from Git. You alone update it:

```text
Active task ID; bounded goal; acceptance criteria; status
Original checkout; integration branch; task checkout; task branch; base/candidate SHAs
Delivery scope and authorization; integration status (not requested / pending / integrated / blocked); target SHA
Repository cloud authorization and its source
Calls used for active task: implementation N/3; review N/3; advisor N (no fixed cap); debugger N/1 per round
Assignments: task ID / round / role | native agent ID | owned scope | status | result
Checks: command | outcome | verified SHA
Review: verdict | reviewed SHA | finding dispositions
Advice: task ID / requester | question / evidence | recommendation | coordinator decision / outcome
Task history: ID | scope/status | calls by role/round | candidate SHA/evidence | remaining work and delivery status
Next action or blocker
```

## Implement, verify and review

Choose from these roles by the missing work, rather than keywords:

| Situation | Agent |
|---|---|
| Clear implementation or correction | `dev-implementer` |
| Verified candidate ready for independent inspection | `dev-reviewer` |
| Failure with an unclear cause | `dev-debugger` |
| Consequential design choice or conflicting evidence | `dev-advisor` |

The implementer handles ordinary code discovery. Use the debugger when diagnosis
is unclear; a known cause and correction can go straight to implementation.

1. Record a pending implementation assignment and increment its count. Spawn
   `dev-implementer` through native tools with `fork_turns="none"`; then record the
   returned ID. Give it the goal, acceptance criteria, exact checkout/owned paths,
   constraints, relevant facts and check commands. Let it inspect the code.
2. Wait for its report. Expect `Status` (complete / partial / blocked), `Result`,
   `Evidence` and `Remaining` from every specialist. Treat a missing report as
   unresolved evidence, not completion. Inspect changes and blockers; commit a
   coherent candidate and run the repository checks yourself. Record outcomes
   and the exact SHA.
3. After checks pass on a clean candidate, record a review call and spawn a fresh
   `dev-reviewer` with no history fork. Supply the brief, base/candidate SHAs and
   check evidence, not the implementer's confidence claims. Record its ID.
4. Judge findings against evidence. A review's `complete` status means the review
   finished; its `Result` must still state a verdict. Send valid corrections to a
   new implementer assignment. Use debugger or advisor only for the needs above.
   Specialists report to you; they do not negotiate with other agents.
5. Finish when checks and accepted review cover the current candidate and the
   agreed delivery scope is fulfilled. Follow Worktree completion for worktree
   commits and delivery. If the base or candidate changes, repeat the invalidated
   checks and review.

Use the configured role models and efforts. An unavailable provider or denied
permission is a blocker to report, not permission to change models or bypass it.
Read-only diagnosis that needs instrumentation becomes a bounded implementer edit.
Wait for the active writer before editing its files yourself.

## Advisor consultations

The coordinator, implementer, reviewer and debugger may raise a specific unresolved
question for `dev-advisor`. Route every consultation through the coordinator.
Use documentation or tests for routine factual checks; advice addresses consequential
uncertainty or conflicting evidence.

A specialist returns partial or blocked with an advice request in `Remaining`:
the question, relevant evidence, options considered and decision needed. Preserve
completed work and finish the assignment before another writer starts.

The coordinator records the requester and question, dispatches a fresh advisor,
and records the recommendation, its own decision and the resulting next action.
Supply that decision and evidence in the requesting role's next focused assignment.
Advice does not waive verification or independent review. Fresh implementation,
review and debugger assignments still count against their existing task limits;
consulting an advisor neither resets nor bypasses those limits.

There is no fixed consultation quota. Revisit the same question only for new
evidence or changed constraints. A new agent, session or rephrased question is not
new evidence. If repeated advice produces no progress, the coordinator makes a
supported decision or reports the specific blocker instead of seeking another
opinion. The advisor gives its recommendation and uncertainty; it cannot delegate
or initiate another consultation. Record failures and resolve their cause before
retrying an unavailable advisor.

## Worktree completion

Apply this section before committing or finishing worktree work, including tiny
tasks and resumed sessions. Reuse the task note and still-valid evidence; a
commit or integration request alone does not restart implementation and review.

1. Use Git to confirm the original checkout and any recorded integration branch.
   Resolve an unknown destination before merging instead of assuming `main`.
   A commit/checkpoint request saves work on the task branch. An authorized
   finish/integrate request includes delivery to the original checkout. Reuse standing authorization;
   honor a requested branch- or PR-only delivery scope.
2. Reuse the task branch. If HEAD is detached, create a unique task branch at the
   current HEAD before committing; this also preserves any existing detached
   commits. Stage only task changes and record the committed candidate SHA.
3. When integration is in scope and required checks/review cover the candidate,
   confirm task writers have finished and inspect the destination's branch and
   local changes again. Preserve unrelated work; resolve overlapping changes
   before integration. Run the merge against the original checkout with its
   recorded target branch checked out:
   `git -C <original-checkout> merge --ff-only <task-branch>`.
   If histories diverged, inspect and reconcile them with ordinary Git within
   the authorized scope, then refresh affected checks and review.
4. Verify the destination branch contains the accepted candidate and the original
   checkout's task files reflect the intended result. Record the resulting target
   SHA and integration status. Report committed work awaiting integration as such;
   requested integration that is pending or blocked means delivery is incomplete.
5. Before cleaning up an integrated worktree, move its completed note to the
   original repository's locally ignored `.agent-notes/<task-id>.md` and verify it
   exists there. Preserve dirty, unmerged or ambiguous worktrees. Use ordinary Git
   or native cleanup without a new helper; ignored notes may not survive archival.

## Bound calls and preserve context

Scope call limits to one bounded deliverable with its own acceptance criteria. Use its existing roadmap/ticket ID, or assign a stable
ID before dispatch. A project, roadmap or conversation can contain multiple tasks.

When moving to the next authorized task, save the previous task's counts, status,
evidence and remaining obligations in the task history of `.agent-task.md`. Select
the new task ID and initialize its counters at zero; this needs no limit adjustment
or new approval within the existing authorization. If that ID was worked on before,
restore its saved counts instead. New tasks get their own acceptance/check/review
evidence. Preserve shared checkout, authorization and pending integration details.

Blocked or exhausted tasks keep their counts and unresolved work; continue with
another authorized task only if its dependencies allow it. Correcting, renaming
or subdividing unfinished work to replenish its allowance remains the same task.
A new allowance does not resolve a known provider or environment blocker.

Every specialist call, including debugger and advisor, uses a fresh agent with
`fork_turns="none"` and a focused brief. Do not resume an old specialist.

For each task ID, allow at most three implementation calls, three review calls,
and one debugger call per implementation round. Advisor consultations have no fixed
numeric limit; apply Advisor consultations. Record each call
against that ID before requesting it; failed dispatches count toward that task.
A restart, model change or return to the same task retains its counts. For legacy
session-wide totals, use assignment history to attribute calls to their tasks;
preserve uncertain prior counts rather than assuming attempts were unused.
These are instruction-based limits, not a software circuit breaker.

A further call needs new evidence, a changed assignment or a specific corrective
approach. At a limit, or repeated failure without new evidence, preserve the
checkout and report passing/failing checks, attempted corrections and the next
useful decision. Do not rename the same task to obtain more attempts.

Keep concise assignment results and finding dispositions in the note. Pass focused
failure excerpts or log paths, not transcripts. Reopen a settled finding only for
changed code or new evidence. Keep the coordinator focused on this task; use a new
session for unrelated work.

After interruption, inspect Git and native agent status before reassigning work.
An incomplete report or pending assignment is unresolved evidence; confirm that
its writer has stopped. Reconstruct from the note and current code, retaining
counts. Native session history and the note provide checkpoints, not atomic recovery.
