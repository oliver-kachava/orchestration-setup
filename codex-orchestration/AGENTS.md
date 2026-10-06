# Project guidance

## Orchestration entry point

If a coordinator gave you a bounded specialist assignment, follow that role and
brief along with the project conventions below. Leave coordination and further
delegation to the coordinator; this file does not make you the orchestrator.
You may request dev-advisor through the coordinator for consequential uncertainty
or conflicting evidence; include the question and evidence in your report.

In the main session launched with `codex-orchestrator` or the `orchestrator`
profile, load the `orchestration` skill before substantial development. That
skill defines role selection, ownership, handoffs, call limits, verification
and completion. Use it as the shared workflow reference.

Before the coordinator commits or finishes work in a worktree, follow the skill's
Worktree completion section, including for tiny tasks and resumed sessions.

When resuming coordinator work, read the existing `.agent-task.md` and inspect
Git and native agent status before assigning more work.

## Project conventions

Keep the target repository's existing guidance. Record only verified project facts:

- Runtime versions and setup prerequisites.
- Actual commands for relevant tests, linting, type checks and builds.
- Source/test layout, generated files and protected paths.
- Project-specific operational or deployment boundaries.

Discover commands from repository scripts and configuration before documenting
them. Preserve existing user changes and record checks actually run. Update
project facts when their source changes.
