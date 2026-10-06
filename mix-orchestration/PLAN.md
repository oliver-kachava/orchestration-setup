# Orchestration mix — plan and specification

User-selected backend: Pi. This separate package keeps Codex as coordinator and
reviewer and moves implementation to Pi. It retains the existing role models,
bounded calls, task note and worktree completion rules. It does not install or
replace the native setup during packaging.

## Responsibilities

The coordinator scopes work, owns `.agent-task.md`, prepares focused briefs,
dispatches specialists, verifies changes, judges review findings and handles Git.
Pi implements the assigned paths and checks. Native `dev-reviewer` independently
inspects a verified candidate; native `dev-debugger` and `dev-advisor` are optional.
All specialists report to the coordinator and leave further delegation to it.

Model choices are explicit. Codex uses Sol 6.1/high for coordination, review and
debugging, Astra/xhigh for advice. Pi requests DeepSeek V4.1 Flash/high through
Ollama. Its provider/model/effort live in the skill's `implementer.json`; another
Pi-supported model can be selected there. Unavailable models are blockers.
The real provider route must be configured and verified before relying on it.

## Task flow

1. Read project guidance and existing task evidence. Establish acceptance criteria,
   actual check commands, ownership, repository cloud authorization, original/task
   checkouts, base SHA, integration destination and authorized delivery scope.
2. Record the implementation attempt and dispatch Pi in the task checkout with a
   fresh brief. Track its run ID, process handle, PID, model and receipt path.
3. After the writer stops, inspect its report and diff. The coordinator commits a
   coherent candidate and runs the relevant checks, recording the exact SHA.
4. Request fresh native review of the base-to-candidate diff, acceptance criteria
   and check evidence. Judge findings and request a bounded correction if needed.
5. Deliver the authorized scope. In a worktree, a commit is a checkpoint; authorized
   integration is executed against the original checkout's recorded branch and
   verified there. Preserve the completed note before cleanup.

## Convergence and context

Use one writer and identify each bounded deliverable by a stable task ID, such as
a roadmap item. Each ID gets at most three implementation calls, three reviews,
and one debugger per implementation round. Advisor consultations have no fixed quota. Count dispatch
failures against their assigned task. A new authorized task starts at zero;
returning to an existing task restores its saved counts. Preserve each task's
evidence, counts and open obligations in the same note's task history. Another
model or session does not reset an existing task's allowance. A correction
needs new evidence or a changed approach. Stop at a limit or repeated failure
without progress and report the remaining decision.

Native specialists use `fork_turns="none"`. Pi uses a fresh process and
`--no-session`. Both receive focused briefs, not the coordinator's transcript.
Pi still loads its own settings, guidance and extensions. `.agent-task.md` is the
only task tracker; `.agent-runs/` holds private evidence. Recovery consults Git,
native status and external receipts/processes before assigning ownership again.

## Dispatcher boundary

Any implementer, reviewer or debugger can request advice through the coordinator.
Advisor consultations have no fixed quota. Each must address a specific unresolved
question; revisiting it requires new evidence or changed constraints. The
coordinator records the recommendation and decides the next action. Repeated
consultations without progress lead to a decision or blocker report. The advisor
cannot delegate or initiate another consultation. Advice is carried into the next
fresh specialist assignment, which still counts against that role's task limit.


One standard-library Python helper launches Pi with explicit cwd/provider/model,
reads JSONL events and validates the final report. It enforces a process deadline,
turn cap and lock per checkout, terminates its process group on interruption and
never retries or switches models itself. It checks Pi's emitted model identity,
successful final assistant completion and settled event as well as process exit.
It detects HEAD/branch changes and reports them without rolling back user work.

The helper does not enforce path ownership, prevent Git commands, sandbox Pi,
implement a cross-session task budget or control external processes that escape
its process group. Those limits remain coordinator instructions and launch-environment
controls. A stale receipt or uncertain cleanup requires checking actual writer
status. A complete model report does not replace independent checks and review.

## Package

The package has a distinct `codex-orchestrator-mix` launcher and
`orchestrator-mix.config.toml`, three native role files, one `orchestration-mix`
skill with its dispatcher/config/role brief, an optional `AGENTS.md` template,
the profile/roles installer, a Pi provider example, process-contract tests and
installation/validation documents. There is no persistent service, task database,
automatic retry queue, Git wrapper or second external CLI backend.
