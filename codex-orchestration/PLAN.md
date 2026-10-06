# Orchestration — plan and specification

**Status:** Native agents with instruction-based boundaries accepted October 1,
2026. Files packaged for delivery; installation and remaining live checks are
separate from this ZIP request. No adapter is included.

## Design

Use one Codex coordinator and fresh native specialists. The coordinator owns
scope, assignments, the task note, verification, review decisions and Git.
Ordinary Git and repository checks supply the evidence. Codex owns agent sessions.

| Role | Model / effort | Assignment |
|---|---|---|
| Coordinator | `gpt-6.1-sol` / high | Assign, track, verify, judge findings, commit and integrate |
| `dev-implementer` | `deepseek-v4.1-flash:cloud` / high | Implement assigned code and tests; run checks |
| `dev-reviewer` | `gpt-6.1-sol` / high | Independently review a verified candidate |
| `dev-debugger` | `gpt-6.1-sol` / high | Diagnose an unclear failure without editing |
| `dev-advisor` | `gpt-6-astra` / xhigh | Resolve a consequential design question or conflicting evidence |

Implementation and review are the normal path. Debugging and advice are optional.
Use the implementer for ordinary discovery and known corrections. Keep fixed
models and efforts; report an unavailable model rather than switching silently.
Native model IDs depend on the existing parent session's provider integration.
Verify DeepSeek routing before relying on it, and obtain repository-specific
authorization for cloud calls.

## Boundaries and convergence

All roles share the parent's effective permissions. Read-only assignments,
no-delegation rules and call limits are instructions, not separate enforced
sandboxes or a software circuit breaker. This tradeoff is accepted. Only one
writer operates on task code at a time; the coordinator waits before editing
assigned files. Specialists preserve other work and return to the coordinator.

Identify each bounded deliverable by a stable task ID, such as a roadmap item.
For each ID, allow at most three implementation calls, three review calls, one
debugger call per implementation round. Advisor consultations have no fixed quota. Count requested
calls, including failed dispatches, against that ID before making them.
Moving to a new authorized task starts its counters at zero automatically. Keep
the previous task's counts, evidence and open obligations in the same note's task
history. Returning to it or restarting a session restores its existing counts.
A correction needs new evidence or a changed approach. At a limit or repeated
failure without new evidence, preserve the checkout and report the next useful
decision. A renamed task does not receive a fresh allowance for the same work.

## Work and evidence

Any implementer, reviewer or debugger can request advice through the coordinator.
Advisor consultations have no fixed quota. Each must address a specific unresolved
question; revisiting it requires new evidence or changed constraints. The
coordinator records the recommendation and decides the next action. Repeated
consultations without progress lead to a decision or blocker report. The advisor
cannot delegate or initiate another consultation. Advice is carried into the next
fresh specialist assignment, which still counts against that role's task limit.


1. Read repository guidance, define acceptance criteria and check commands, and
   confirm the original/task checkouts, base SHA, integration branch and authorized
   delivery scope. Use a managed worktree for substantial work; tiny safe edits
   may remain in the selected checkout.
2. Record the assignment and count, then spawn a fresh implementer with
   `fork_turns="none"`, a focused brief and explicit ownership. Record its ID.
3. Inspect the changes and report. Commit a coherent candidate, run the relevant
   checks through the coordinator and record outcomes with the exact SHA.
4. Dispatch a fresh reviewer with the brief, base/candidate SHAs and check
   evidence. Exclude the implementer's confidence claims.
5. Judge actionable findings and obtain bounded corrections if needed. Accepted
   review and verification must cover the current candidate; refresh stale
   evidence after any candidate or relevant base change.
6. Follow the skill's Worktree completion section for worktree commits and delivery,
   including tiny tasks and resumed sessions. Commits are checkpoints; authorized
   integration runs against the original checkout's recorded destination branch.
   Finish only when the agreed delivery scope is verified. Preserve the completed
   task note in the original repository before cleanup; retain unfinished, dirty
   or ambiguous worktrees.

Every specialist reports `Status` (complete / partial / blocked), `Result`,
`Evidence` and `Remaining`. A completed review still needs an explicit verdict.
A missing report is unresolved evidence. The coordinator judges findings;
specialists do not negotiate with one another or expand their assignments.

## Tracking and context

Keep one locally ignored `.agent-task.md`, owned by the coordinator. Record the
goal, acceptance criteria, original/task checkouts and branches, base/candidate
SHAs, delivery scope and authorization, integration status and target SHA, cloud
authorization, active task ID, per-task role counts, assignment IDs/status/results,
checks and review evidence, finding dispositions, task history and next action. The exact note format is in the
skill; no second state store or reporting directory is needed.

Use fresh specialists with focused briefs instead of full-history forks. After
interruption, inspect Git and native agent status before reassigning ownership.
The note is a checkpoint, not atomic recovery. Start a new coordinator session
for unrelated work.

## Files and delivery

The package contains one `orchestrator.config.toml`, four `agents/dev-*.toml` files,
`orchestration/SKILL.md`, a two-line `codex-orchestrator` launcher, an
`install-agents.sh` installer for the profile and roles, a project `AGENTS.md`
template and three documents: README, this plan and validation notes. Installation
destinations and usage are in the README. Preserve existing global/project
guidance, including Context7 and CodeGraph instructions.

There is no custom task engine, process supervisor, automatic retry service,
Git wrapper, token-budget service or CLI adapter. The profile disables older
development playbooks so they do not compete with `orchestration`. MCP
integrations and other feature settings inherit the user's base configuration.
The profile enables native subagents without disabling apps, plugins, hooks or
memories.

Package validation covers configuration syntax, skill structure, launcher and
installer behavior, and archive integrity. Live model/provider routing, complete reports,
worktree behavior and recovery scenarios are recorded honestly in
`VALIDATION.md`. Resolve concrete incompatibilities without silently changing
models or rebuilding the retired framework.
