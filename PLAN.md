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

Allow at most three implementation calls, three review calls, one debugger call
per implementation round and two advisor calls per task. Count requested calls,
including failed dispatches, before making them. Retain counts after a restart.
A correction needs new evidence or a changed approach. At a limit or repeated
failure without new evidence, preserve the checkout and report the next useful
decision. A renamed task does not receive a fresh allowance for the same work.

## Work and evidence

1. Read repository guidance, define acceptance criteria and check commands, and
   confirm the task checkout, base branch and SHA. Use a managed worktree for
   substantial work; tiny safe edits may remain in the selected checkout.
2. Record the assignment and count, then spawn a fresh implementer with
   `fork_turns="none"`, a focused brief and explicit ownership. Record its ID.
3. Inspect the changes and report. Commit a coherent candidate, run the relevant
   checks through the coordinator and record outcomes with the exact SHA.
4. Dispatch a fresh reviewer with the brief, base/candidate SHAs and check
   evidence. Exclude the implementer's confidence claims.
5. Judge actionable findings, obtain bounded corrections if needed, and finish
   only when accepted review and verification cover the current candidate.
   Update stale evidence after any candidate or relevant base change.
6. Integrate when authorized. Before cleanup, move the completed task note to
   the original repository's ignored `.agent-notes/<task-id>.md` and verify it.
   Preserve unfinished, dirty or ambiguous worktrees.

Every specialist reports `Status` (complete / partial / blocked), `Result`,
`Evidence` and `Remaining`. A completed review still needs an explicit verdict.
A missing report is unresolved evidence. The coordinator judges findings;
specialists do not negotiate with one another or expand their assignments.

## Tracking and context

Keep one locally ignored `.agent-task.md`, owned by the coordinator. Record the
goal, acceptance criteria, original repository, checkout, branch, base/candidate
SHAs, cloud authorization, role counts, assignment IDs/status/results, checks and
review evidence, finding dispositions and next action. The exact note format is
in the skill; no second state store or reporting directory is needed.

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
development playbooks so they do not compete with `orchestration`.

Package validation covers configuration syntax, skill structure, launcher and
installer behavior, and archive integrity. Live model/provider routing, complete reports,
worktree behavior and recovery scenarios are recorded honestly in
`VALIDATION.md`. Resolve concrete incompatibilities without silently changing
models or rebuilding the retired framework.
