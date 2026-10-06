# Mix orchestration

Codex coordinates and reviews; Pi implements. One skill, one task note and one
subprocess dispatcher. The existing native setup can remain installed. This
package has a separate launcher and profile; extracting it installs nothing.

## Install

Prerequisites: the existing Codex CLI with native custom agents/profile files,
Pi, Python 3.9+ and Git on macOS or Linux. Pi's CLI/event contract was checked
against installed **0.87.1**. The dispatcher uses only Python's standard library.

From the `mix-orchestration` directory:

```sh
npx skills@latest add ./orchestration-mix --agent codex --global --copy
sh ./install-agents.sh
```

The first command installs the entire skill, including its dispatcher, role
brief and implementer configuration. Use the skill directory reported by the
installer; on this machine skills are under `~/.agents/skills/`. See the
[Skills CLI guide](https://github.com/vercel-labs/skills#options).

The second command installs `orchestrator-mix.config.toml` at the Codex config
root and three `dev-*.toml` files under `agents/`. It honors `CODEX_HOME`, defaults
to `~/.codex`, and accepts an explicit folder:

```sh
sh ./install-agents.sh /path/to/codex-home
```

Identical files are skipped. Replaced files or symlinks are backed up under
`backups/orchestration-mix-agents/`; symlink targets are preserved. The main
`config.toml`, native `orchestrator.config.toml` and other roles are preserved.
The three native specialist names are shared with the original setup, so
existing customizations to those files receive backups when replaced.

Install the launcher, preserving any previous file or symlink:

```sh
mkdir -p "$HOME/.local/bin"
if [ -e "$HOME/.local/bin/codex-orchestrator-mix" ] || [ -L "$HOME/.local/bin/codex-orchestrator-mix" ]; then
  launcher_backup=$(mktemp -d "$HOME/.local/bin/orchestration-mix-backup.XXXXXX")
  mv "$HOME/.local/bin/codex-orchestrator-mix" "$launcher_backup/"
fi
install -m 755 ./codex-orchestrator-mix "$HOME/.local/bin/codex-orchestrator-mix"
```

Paste this into zsh to add the directory to PATH now and in future shells:

```sh
grep -qxF 'export PATH="$HOME/.local/bin:$PATH"' "$HOME/.zshrc" 2>/dev/null ||
  printf '\n%s\n' 'export PATH="$HOME/.local/bin:$PATH"' >> "$HOME/.zshrc"
export PATH="$HOME/.local/bin:$PATH"
```

`AGENTS.md` is an optional project guidance template. Merge its entry point into
existing guidance when useful; preserve repository conventions and existing
Context7, CodeGraph and security instructions. The profile also selects the skill,
so a new project AGENTS file is not required just to start this workflow.

## Configure Pi once

`orchestration-mix/implementer.json` selects `ollama`,
`deepseek-v4.1-flash:cloud` and requests `high` thinking. Change this file in the
installed skill to choose another Pi-supported provider/model. A new skill copy
can replace those local choices; keep them when updating. There is no automatic
model fallback or Claude Code backend in this package.

Pi needs that model registered separately. `pi-models.example.json` shows an
Ollama provider using the local server's OpenAI-compatible API. Merge the example
into `~/.pi/agent/models.json` (or your configured Pi agent directory), preserving
existing providers. The installer does not copy it automatically. Its `ollama`
API key is a dummy value for the local Ollama endpoint, not a credential.
Authenticate and make the selected model available through your normal provider
setup. See Pi's [custom model documentation](https://pi.dev/docs/latest/models).

This machine had no Pi Ollama model entry when the package was built. The real
Ollama/DeepSeek route and its thinking behavior remain unverified. The `reasoning`
flag in the example advertises support; it does not prove that a server implements
the requested effort. Repository-specific cloud authorization is recorded before
dispatch. Credentials stay in the provider's approved configuration, outside briefs.

## Use

Start a fresh session after installing:

```sh
cd /path/to/project
codex-orchestrator-mix --worktree
```

The launcher runs `codex --profile orchestrator-mix "$@"`, forwarding every
argument unchanged. Tiny safe edits can use `codex-orchestrator-mix` directly.

The coordinator keeps `.agent-task.md` and `.agent-runs/` locally ignored. It
launches one fresh Pi process for implementation, reads its report, inspects the
diff and runs repository checks itself. A fresh native reviewer then examines
the verified candidate. Debugging and advice are optional. The coordinator owns
commits and integration; specialists return their findings to it.

| Role | Model / requested effort | Runtime |
|---|---|---|
| Coordinator | `gpt-6.1-sol` / high | Codex |
| Implementer | `deepseek-v4.1-flash:cloud` / high | Pi via Ollama |
| `dev-reviewer` | `gpt-6.1-sol` / high | Native Codex agent |
| `dev-debugger` | `gpt-6.1-sol` / high | Native Codex agent, optional |
| `dev-advisor` | `gpt-6-astra` / xhigh | Native Codex agent, optional |

A worktree commit saves a checkpoint on its task branch. It does not update the
original checkout. When integration is wanted, include it in the task, for example:

> Finish this task and integrate the verified changes into the original checkout's
> agreed target branch, preserving unrelated changes and verifying the result there.

The skill records that destination and authorization, verifies delivery and
preserves the completed note before cleaning up a worktree.

## Limits and verification

Any implementer, reviewer or debugger can request advice through the coordinator.
Advisor consultations have no fixed quota. Each must address a specific unresolved
question; revisiting it requires new evidence or changed constraints. The
coordinator records the recommendation and decides the next action. Repeated
consultations without progress lead to a decision or blocker report. The advisor
cannot delegate or initiate another consultation. Advice is carried into the next
fresh specialist assignment, which still counts against that role's task limit.


One writer at a time. Each Pi dispatch defaults to 15 minutes and 40 model turns;
its lock covers dispatchers using the same checkout. Timeout/interruption stops
the owned process group. Each stable task ID (one roadmap item or bounded
deliverable) gets three implementation calls, three reviews and one debugger per
round. Advisor consultations have no fixed quota. A new authorized task starts at zero automatically;
returning to a previous task restores its saved counts. The coordinator preserves
each task's evidence and remaining delivery in the same note. Failed launches
count against their assigned task; restarting, changing models or renaming
unfinished work does not reset it. A retry requires new evidence or a changed approach.

These role and task boundaries are instructions. The dispatcher is not a security
sandbox or a replacement for Git checks. Pi retains its normal settings, project
guidance and extensions; `--no-session` avoids saving/resuming its conversation.
Codex integrations and memory settings inherit the main configuration. Only the
older competing orchestration skills are disabled in the mixed profile.

The dispatcher requires a fresh evidence directory. It saves private `run.json`
metadata and a four-field `report.json`, without raw Pi events or stderr. A
`reported_complete` receipt is a model claim that still requires verification.
On `cleanup_unconfirmed` or a stale receipt, confirm the writer stopped before
starting another. Private permissions and Git ignores are not secret redaction;
review briefs and reports before sharing them.

Run the included synthetic process tests without credentials or a model:

```sh
python3 -B -m unittest discover -s tests -v
```

For an invocation-only check, add `--dry-run` to the dispatch command shown in
the skill. It creates no files and does not test authentication, model availability
or provider behavior. See `VALIDATION.md` for completed checks and the small live
trial still needed. `PLAN.md` records the final design. Pi's
[JSON event documentation](https://pi.dev/docs/latest/json) explains why successful
process exit alone is insufficient evidence of model completion.
