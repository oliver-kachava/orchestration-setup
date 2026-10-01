# Validation and package status

On October 1, 2026, the user accepted native agents with instruction-based role
boundaries and requested a ZIP of the files. The boundary decision is resolved:
there is no adapter. This package has not been installed by the packaging step.

The launcher is `codex-orchestrator`, which selects `orchestrator.config.toml`
with `--profile orchestrator`. `AGENTS.md` includes a coordinator-only skill
entry point, specialist scoping and a resumption checkpoint alongside project
conventions.

## What was observed

A synthetic probe on Codex CLI 0.159.2 discovered the four project-scoped roles
and made exactly two native dispatches with `fork_turns="none"`.

- The implementer edited code and tests and added a usage document. The
  coordinator independently ran all six behavioral tests successfully.
- The implementer's final response was empty. Its selected model ID and runtime
  logs referenced DeepSeek, but the effective provider was not independently
  confirmed. A usable report and correct backend routing remain unverified.
- A harmless reviewer write succeeded despite the requested read-only role
  setting, and the reviewer reported delegation tools still available. This is
  the reason role restrictions are now explicitly behavioral instructions.
- A parent-only diagnostic token was omitted from the dispatch briefs. Full
  effective child context was not independently captured.

The earlier source lookup found a native role override allowlist covering model,
effort and instructions, but not per-role provider or sandbox settings. Those
ineffective overrides have been removed from this package. Roles inherit the
parent session's provider integration and effective permissions.

## Package checks

The TOML files are parsed, the orchestration skill is checked with the
skill-creator validator, and the launcher is checked for valid shell syntax and
exact argument forwarding. The installer passed shell syntax and temporary folder
checks for installing the orchestrator profile at the configuration root and all
four roles under `agents/`, repeat runs, and backups of replaced files and
symlinks. Checks confirmed preservation of the main `config.toml`, unrelated
agents and symlink targets, and preflight failures without partial copies.
Paths with spaces and execution from another working directory were also checked.
No installed Codex files were changed.

ZIP contents are read back and compared with the source files, including the
launcher and installer's executable modes. These packaging checks do not
establish successful live model routing or behavioral compliance.

## Before relying on the installed workflow

Run one small native implementation, coordinator verification and independent
review using the intended models and checkout. Confirm complete reports and the
worktree's starting revision. Then exercise an exhausted attempt count and a
changed candidate to confirm that the coordinator stops appropriately and
invalidates old check/review evidence. Confirm that the task note supports
resumption and is preserved outside the worktree before cleanup.

These live checks remain outstanding. The prior permission failure is an
accepted design tradeoff, not an unresolved approval request. No automatic model
fallback or adapter is included.
