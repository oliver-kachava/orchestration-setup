# Validation — mix-orchestration

Built October 3, 2026. These checks cover the package and dispatch contract.
They do not establish a successful live DeepSeek implementation/review workflow.
The installed native setup was not changed.

## Documentation and process checks

Pi 0.87.1 CLI help, installed official JSON/model documentation and print-mode
source were inspected. Context7's versioned Pi documentation was also retrieved.
The dispatcher uses `message_end.message` for the authoritative assistant response
and requires `agent_settled`; `agent_end` may be followed by automatic recovery.
Pi can exit zero after a model error, which the helper treats as failure.

Fourteen automated unittest cases passed using a synthetic Pi executable and
temporary Git repositories. They cover explicit arguments and working directories,
fresh sessions, private evidence permissions, Unicode framing, complete/partial/
blocked reports, automatic recovery, invalid or truncated output, unsuccessful
assistant responses, model mismatch, turn limits, process failures, deadlines,
descendant cleanup, interruption, concurrent dispatches with different `TMPDIR`
values, ignored artifacts, preservation of existing evidence, dry runs, invalid
configuration and detection of an unauthorized Git commit without rollback.

The first sandboxed run exposed test-fixture issues and a macOS process-signal
restriction. Fixtures now use immutable per-call briefs and signal-based PID
checks. Cleanup errors now produce `cleanup_unconfirmed` and a failed receipt.
The passing full suite ran outside the sandbox to validate actual process-group
termination. The shipping code reports uncertainty instead of bypassing denied
process operations.

An independent read-only review identified two issues: incomplete Git-ignore
coverage and locks varying with `TMPDIR`. Both were fixed. The reviewer then
passed six targeted checks and an injected cleanup-permission failure check.

The installed Pi 0.87.1 executable also passed a local integration probe with an
isolated temporary Pi configuration and a synthetic OpenAI-compatible HTTP
provider. Pi executed a real `write` tool call in a disposable Git checkout,
completed two model turns, and produced the exact four-field report accepted by
the dispatcher. This verifies CLI invocation, tool execution, event parsing and
report capture; it used no real model, external endpoint or user credentials.

## Remaining live checks

The machine had Pi installed but no Ollama entry in Pi's `models.json`. No real
model call, credential change, installation into user config or project merge
was performed. The included provider file is an example, not a confirmed routing
configuration. Actual DeepSeek availability, requested thinking behavior and
native review/advisor availability in the mixed profile remain unverified.

After installation and provider setup, use a disposable repository for one tiny
implementation, coordinator verification and fresh native review. Confirm a real
edit, complete four-field report, expected provider/model and current-SHA review.
Then check a resumed task retains its call counts, a changed candidate invalidates
old review evidence, a commit-only request leaves the original checkout unchanged,
and authorized integration updates the intended destination.

Task call limits, ownership, no-delegation rules and worktree completion were
manually reviewed as instructions. They are not proven by process-contract tests.
Fresh Pi history does not prove absence of global instructions/extensions or
measure maximum token efficiency.

## Package checks

All four TOML files and the JSON files parsed successfully. The dispatcher parsed
with Python 3.9 syntax. Skill-creator's structural validator passed using an
existing cached PyYAML installation. Both shell files passed syntax checks, and
a fake Codex executable confirmed exact launcher argument forwarding.

The installer passed temporary-folder checks for four installed files, repeat
runs, paths with spaces, backups of changed files and symlinks, preservation of
symlink targets and unrelated/native configuration, and preflight failures before
any copying. No package dependency was installed. Installed Codex CLI 0.160.0
help confirms the profile-file and worktree flags; live mixed-profile agent
dispatch was not tested.

Gitleaks scanned the package with fully redacted reporting and found no leaks.
Checksums confirmed the original native source package and ZIP are unchanged.
The delivery ZIP was read back to check CRCs, file contents and executable modes.

## October 5 per-task call limits

The mixed skill now uses the same stable task IDs and per-task counters as the
native skill. New authorized tasks start at zero; revisited tasks retain their
counts. Task history preserves prior evidence and unresolved delivery. This update
changes instructions and documentation only; the Pi dispatcher and its limits are
unchanged. The October 3 process tests were not rerun for this wording change.

Skill structure was validated. Manual instruction review covered a new roadmap
item, a return to an exhausted item, failed dispatch attribution, a resumed
session, renamed unfinished work and pending integration during a transition.
No live agent behavior test was run for this update.

## Advisor consultation update

All implementation, review and debugging roles can request dev-advisor through
the coordinator. The fixed two-consultation cap is removed; question tracking,
new-evidence requirements and a stop-on-no-progress rule govern further advice.
The advisor cannot delegate or initiate consultations. Continuations remain fresh
assignments charged to their role's existing per-task limits. Pi retains its
four-field report contract and uses `remaining` for its advice request.

Both skills passed structural validation and all role/profile TOMLs parsed.
Manual review covered all requesting roles, repeat questions, changed evidence,
no-progress outcomes, an exhausted implementation allowance and the Pi handoff.
No live agent consultation was tested. Runtime code and model selections are unchanged.
