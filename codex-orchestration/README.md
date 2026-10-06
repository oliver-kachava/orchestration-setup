# Orchestration

One Codex coordinator, four native specialist roles, one skill and one task note.
This package uses instruction-based role boundaries and attempt limits. It adds
no adapter or runtime dependency. Packaging does not install the files.

## Files and installation

Open a terminal inside the `codex-orchestration` directory.
Install the skill for Codex with:

```sh
npx skills@latest add ./orchestration --agent codex --global --copy
```

This installs a copy of the `orchestration` skill for use across projects. It
does not install the agent definitions, profile or launcher. The
[Skills CLI guide](https://github.com/vercel-labs/skills#options) documents its
options.

Install the orchestrator profile and four agent definitions with:

```sh
sh ./install-agents.sh
```

The script copies `orchestrator.config.toml` into `~/.codex/` and the four
`dev-*.toml` files into `~/.codex/agents/`, creating the directories as needed.
The profile is required by `codex-orchestrator`, which launches Codex with
`--profile orchestrator`. The script skips identical files and backs up replaced
files or symlinks under `~/.codex/backups/orchestration-agents/`. It preserves
symlink targets, the main `config.toml` and unrelated agents. It uses `CODEX_HOME`
when set; to choose a different Codex configuration folder explicitly, run:

```sh
sh ./install-agents.sh /path/to/codex-home
```

`AGENTS.md` remains an optional project template. Copy the launcher to the
destination below, backing up any existing launcher first. If `codex-orchestrator`
is a symlink, move that link aside before copying the new launcher so the copy
does not overwrite its old target.

| Included file | Destination |
|---|---|
| `orchestrator.config.toml` | Installed by `install-agents.sh` into `~/.codex/orchestrator.config.toml` |
| `agents/dev-*.toml` | Installed by `install-agents.sh` into `~/.codex/agents/` |
| `install-agents.sh` | Run from this package; no installation needed |
| `orchestration/SKILL.md` | Installed by the command above into `~/.codex/skills/orchestration/` |
| `codex-orchestrator` | `~/.local/bin/codex-orchestrator`; make executable |
| `AGENTS.md` | Optional guidance template; keep your repository's existing guidance |
| `PLAN.md`, `VALIDATION.md` | Design and verification notes; no installation needed |

The paths above assume the default Codex configuration folder, `~/.codex`.
Create the remaining destination directories if needed.
If the executable bit is lost during extraction, run:

```sh
chmod +x ~/.local/bin/codex-orchestrator
```

After copying the launcher to `~/.local/bin`, paste this into zsh to add that
directory to PATH now and in future shells. It avoids appending the same line to
`~/.zshrc` again when rerun:

```sh
grep -qxF 'export PATH="$HOME/.local/bin:$PATH"' "$HOME/.zshrc" 2>/dev/null ||
  printf '\n%s\n' 'export PATH="$HOME/.local/bin:$PATH"' >> "$HOME/.zshrc"
export PATH="$HOME/.local/bin:$PATH"
```

Preserve the main Codex configuration, unrelated agents and existing global
Context7/CodeGraph guidance. The orchestrator inherits your normal MCP, app,
plugin, hook and memory settings. Integrations disabled in your base configuration
stay disabled. The profile disables only the older `agentic-dev` and
`agentic-development` playbooks for this workflow. Finish or recover any task
using legacy helpers before retiring those helpers. Start a fresh Codex session
after installation or a profile update so it loads the current configuration,
skill and roles.

## Use

For a substantial task:

```sh
cd /path/to/project
codex-orchestrator --worktree
```

For a tiny change in the selected checkout, use `codex-orchestrator`. The launcher forwards
native Codex arguments unchanged via `codex --profile orchestrator`. The
coordinator reads `orchestration`, assigns
work, verifies the candidate and obtains independent review. It keeps IDs, call
counts, results and check/review SHAs in one locally ignored `.agent-task.md`.

Call limits belong to each roadmap item or bounded deliverable, identified by a
stable task ID. Moving from R04 to a new, authorized R05 starts R05 at 0/3
implementation calls automatically. R04's counts, evidence and pending delivery
remain in the note; returning to R04 restores its counts. Failed calls count
toward their assigned task. A retry or renamed unfinished task keeps its allowance.

### Completing worktree tasks

A worktree commit does not update the files in the original checkout. A request
to commit creates a checkpoint on the task branch; a request to finish and
integrate includes delivery into the recorded destination branch. For example:

> Finish this task and integrate the verified changes into the original checkout's
> agreed target branch. Preserve unrelated local changes and verify the result there.

The coordinator follows the skill's Worktree completion section, including for
tiny tasks and resumed sessions. It records the destination and authorization,
names detached work before committing, and reports whether integration is pending,
blocked or verified. Existing authorization carries forward; the starting branch
does not itself grant permission to merge. The worktree and task note are retained
until delivery is verified and the note is preserved in the original repository.
Git integration updates the code; it does not move the active CLI session.

## Models and boundaries

Any implementer, reviewer or debugger can request advice through the coordinator.
Advisor consultations have no fixed quota. Each must address a specific unresolved
question; revisiting it requires new evidence or changed constraints. The
coordinator records the recommendation and decides the next action. Repeated
consultations without progress lead to a decision or blocker report. The advisor
cannot delegate or initiate another consultation. Advice is carried into the next
fresh specialist assignment, which still counts against that role's task limit.


Sol 6.1/high coordinates and reviews. DeepSeek V4.1 Flash/high implements;
Sol 6.1/high debugging and Astra/xhigh advice are optional. Only one writer works
on task code at a time. Reviewers, debuggers and advisors receive read-only
assignments; specialists report to the coordinator without delegating further.
These are instructions within the parent's actual sandbox and permissions.

This package targets the existing Codex/Ollama installation. Native role files
select model IDs; they do not establish separate provider connections. DeepSeek
must be routable through the parent session's existing model integration. No
credentials, model catalogs or personal provider configuration are included.
Repository-specific cloud authorization is required before implementation calls.

Before using the workflow on a real task, confirm the intended model/provider,
a complete specialist report and an independent review in a small test checkout.
See `VALIDATION.md` for observed behavior and the checks still outstanding. An
unavailable model is reported as a blocker; the workflow does not switch models
automatically.
