---
name: orchestration
description: Use in the codex-orchestrator coordinator for substantial development with native dev-* subagents. Not for a specialist carrying out an assigned subtask.
---

# Orchestration

Coordinate one task through native Codex agents. You own the task note, checks,
review decisions and Git operations. Use this workflow instead of another
orchestration playbook. A tiny safe change may be handled directly with its checks.

Roles share the parent session's permissions. Read-only assignments and the
no-delegation rule are behavioral instructions, not separate enforced sandboxes.

## Establish the task

Read repository guidance and any `.agent-task.md`. Confirm the task checkout,
intended base branch and SHA, owned paths, acceptance criteria and actual check
commands. Preserve user changes. Use one task worktree for substantial work;
all assigned agents work in that checkout, with only one writer at a time.

Before a cloud-backed implementation call, establish authorization for this
repository and record it in the note. Reuse explicit authorization already given
for that repository; do not infer it from another project.

Keep `.agent-task.md` locally excluded from Git. You alone update it:

```text
Goal and acceptance criteria
Original repository; task checkout; branch; base SHA; candidate SHA
Repository cloud authorization and its source
Calls used: implementation N/3; review N/3; advisor N/2
Assignments: round / role | native agent ID | owned scope | status | result
Checks: command | outcome | verified SHA
Review: verdict | reviewed SHA | finding dispositions
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
5. Complete only when checks and accepted review cover the current candidate.
   Integrate with ordinary Git when authorized. If the base or candidate changes,
   update the branch and repeat the invalidated checks and review.

Use the configured role models and efforts. An unavailable provider or denied
permission is a blocker to report, not permission to change models or bypass it.
Read-only diagnosis that needs instrumentation becomes a bounded implementer edit.
Wait for the active writer before editing its files yourself.

## Bound calls and preserve context

Every specialist call, including debugger and advisor, uses a fresh agent with
`fork_turns="none"` and a focused brief. Do not resume an old specialist.

Allow at most three implementation calls, three review calls, one debugger call
per implementation round and two advisor calls per task. Record each call before
requesting it; failed dispatches count. A restart or model change does not reset
counts. These are instruction-based limits, not a software circuit breaker.

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

Before cleaning up an integrated worktree, move its completed note to the original
repository's locally ignored `.agent-notes/<task-id>.md`. Verify that it exists
there; ignored files may not survive native archival. Preserve dirty, unmerged
or ambiguous worktrees. Use ordinary Git or native cleanup, without a new helper.
