#!/usr/bin/env python3
"""Run one Pi implementation assignment. Python 3.9+, macOS/Linux, stdlib only."""

import argparse
import fcntl
import hashlib
import json
import math
import os
from pathlib import Path
import selectors
import shutil
import signal
import subprocess
import sys
import time
import uuid
from datetime import datetime, timezone

SKILL = Path(__file__).resolve().parent.parent
MAX_LINE = 4 * 1024 * 1024
MAX_OUTPUT = 32 * 1024 * 1024
TOOLS = "read,edit,write,bash,grep,find,ls"


class DispatchError(Exception):
    """A fixed, non-sensitive failure reason suitable for the run receipt."""


def timestamp():
    return datetime.now(timezone.utc).isoformat()


def save_json(path, data):
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("x", encoding="utf-8") as handle:
        json.dump(data, handle, indent=2, ensure_ascii=False)
        handle.write("\n")
    temporary.replace(path)


def git(worktree, *args):
    result = subprocess.run(
        ["git", "-C", str(worktree), *args], stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL, timeout=10, check=False,
    )
    if result.returncode:
        raise DispatchError("git_preflight_failed")
    return result.stdout.decode("utf-8").strip()


def configuration(path):
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise DispatchError("invalid_config")
    for key in ("provider", "model"):
        if not isinstance(data.get(key), str) or not data[key].strip() or data[key].startswith("-"):
            raise DispatchError("invalid_config")
    if data.get("thinking") not in ("off", "minimal", "low", "medium", "high", "xhigh", "max"):
        raise DispatchError("invalid_thinking_level")
    seconds, turns = data.get("timeout_seconds"), data.get("max_turns")
    if type(seconds) not in (int, float) or not math.isfinite(seconds) or seconds <= 0:
        raise DispatchError("invalid_timeout")
    if type(turns) is not int or turns < 1:
        raise DispatchError("invalid_turn_limit")
    return data


class Events:
    def __init__(self, config):
        self.config = config
        self.last = None
        self.settled = False
        self.turns = 0
        self.session_id = None

    def accept(self, line):
        if not line.strip():
            return
        try:
            event = json.loads(line)
        except (ValueError, UnicodeError):
            raise DispatchError("invalid_json_event") from None
        if not isinstance(event, dict):
            raise DispatchError("invalid_json_event")
        kind = event.get("type")
        if kind == "session":
            self.session_id = event.get("id")
        elif kind == "agent_start":
            self.settled = False
        elif kind == "turn_start":
            self.turns += 1
            if self.turns > self.config["max_turns"]:
                raise DispatchError("turn_limit")
        elif kind == "message_end":
            message = event.get("message")
            if isinstance(message, dict) and message.get("role") == "assistant":
                self.last = message
                self.settled = False
                if (message.get("provider"), message.get("model")) != (
                    self.config["provider"], self.config["model"]
                ):
                    raise DispatchError("model_mismatch")
        elif kind == "agent_settled":
            self.settled = True

    def report(self):
        if not self.settled:
            raise DispatchError("missing_settled_event")
        if not self.last:
            raise DispatchError("missing_report")
        if self.last.get("stopReason") != "stop":
            raise DispatchError("assistant_did_not_finish")
        content = self.last.get("content")
        if not isinstance(content, list):
            raise DispatchError("missing_report")
        text = "\n".join(
            part["text"] for part in content
            if isinstance(part, dict) and part.get("type") == "text" and isinstance(part.get("text"), str)
        ).strip()
        # Tolerate a single Markdown fence; never extract arbitrary embedded JSON.
        if text.startswith("```json\n") and text.endswith("\n```"):
            text = text[8:-4].strip()
        try:
            report = json.loads(text)
        except ValueError:
            raise DispatchError("invalid_report") from None
        if not isinstance(report, dict) or report.get("status") not in ("complete", "partial", "blocked"):
            raise DispatchError("invalid_report")
        keys = ("status", "result", "evidence", "remaining")
        if any(not isinstance(report.get(key), str) or not report[key].strip() for key in keys):
            raise DispatchError("invalid_report")
        return {key: report[key] for key in keys}


def stop_group(process):
    """Terminate the owned process group, including children left after Pi exits."""
    if getattr(process, "dispatch_stopped", False):
        return
    try:
        os.killpg(process.pid, signal.SIGTERM)
    except ProcessLookupError:
        pass
    try:
        process.wait(timeout=2)
    except subprocess.TimeoutExpired:
        pass
    try:
        os.killpg(process.pid, signal.SIGKILL)
    except ProcessLookupError:
        pass
    process.wait(timeout=5)
    process.dispatch_stopped = True


def consume(process, events, seconds):
    deadline = time.monotonic() + seconds
    pending = b""
    total = 0
    cleaned = False
    os.set_blocking(process.stdout.fileno(), False)
    with selectors.DefaultSelector() as selector:
        selector.register(process.stdout, selectors.EVENT_READ)
        while selector.get_map():
            if time.monotonic() >= deadline:
                raise DispatchError("timeout")
            if process.poll() is not None and not cleaned:
                stop_group(process)
                cleaned = True
            for key, _ in selector.select(min(0.2, max(0, deadline - time.monotonic()))):
                chunk = os.read(key.fd, 65536)
                if not chunk:
                    selector.unregister(key.fileobj)
                    break
                total += len(chunk)
                if total > MAX_OUTPUT:
                    raise DispatchError("output_limit")
                pending += chunk
                while b"\n" in pending:
                    line, pending = pending.split(b"\n", 1)
                    if len(line) > MAX_LINE:
                        raise DispatchError("event_size_limit")
                    events.accept(line)
                if len(pending) > MAX_LINE:
                    raise DispatchError("event_size_limit")
        if pending.strip():
            raise DispatchError("truncated_event")
        try:
            return process.wait(timeout=max(0, deadline - time.monotonic()))
        except subprocess.TimeoutExpired:
            raise DispatchError("timeout") from None


def interrupted(_signum, _frame):
    raise KeyboardInterrupt


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--worktree", required=True, type=Path)
    parser.add_argument("--brief", required=True, type=Path)
    parser.add_argument("--run-dir", required=True, type=Path, help="New private evidence directory, outside Git or ignored")
    parser.add_argument("--config", type=Path, default=SKILL / "implementer.json")
    parser.add_argument("--pi", default="pi", help="Pi executable name or absolute path")
    parser.add_argument("--dry-run", action="store_true", help="Print invocation metadata without running Pi or creating files")
    args = parser.parse_args()
    process = None
    lock = None
    receipt = None
    outcome = 1
    run_dir = args.run_dir.expanduser().absolute()
    previous_umask = os.umask(0o077)
    started = time.monotonic()
    try:
        config = configuration(args.config.expanduser())
        worktree = args.worktree.expanduser().resolve(strict=True)
        if not worktree.is_dir():
            raise DispatchError("invalid_worktree")
        checkout = Path(git(worktree, "rev-parse", "--show-toplevel")).resolve()
        initial_head = git(checkout, "rev-parse", "HEAD")
        initial_branch = git(checkout, "rev-parse", "--abbrev-ref", "HEAD")
        brief = args.brief.expanduser().resolve(strict=True)
        if not brief.is_file() or not 0 < brief.stat().st_size <= 128 * 1024:
            raise DispatchError("invalid_brief")
        executable = shutil.which(args.pi)
        if not executable:
            raise DispatchError("pi_not_found")
        command = [executable, "--mode", "json", "--no-session", "--provider", config["provider"],
                   "--model", config["model"], "--thinking", config["thinking"], "--tools", TOOLS,
                   "--append-system-prompt", str(SKILL / "implementer.md")]
        if args.dry_run:
            print(json.dumps({"cwd": str(worktree), "command": command, "brief": str(brief),
                              "run_dir": str(run_dir), "timeout_seconds": config["timeout_seconds"],
                              "max_turns": config["max_turns"]}))
            return 0
        if run_dir.exists() or run_dir.is_symlink():
            raise DispatchError("run_directory_exists")
        # Evidence inside a checkout must be ignored before any file is created.
        try:
            relative = run_dir.resolve().relative_to(checkout)
        except ValueError:
            relative = None
        if relative is not None:
            for name in ("run.json", "report.json", "run.json.tmp", "report.json.tmp"):
                git(checkout, "check-ignore", "--quiet", str(relative / name))
        lock_id = hashlib.sha256(str(checkout).encode()).hexdigest()
        # TMPDIR can differ between shells; the same checkout must share a lock.
        lock_root = Path("/tmp") / ("orchestration-mix-" + str(os.getuid()))
        lock_root.mkdir(mode=0o700, exist_ok=True)
        if lock_root.is_symlink() or lock_root.stat().st_uid != os.getuid():
            raise DispatchError("unsafe_lock_directory")
        lock = (lock_root / (lock_id + ".lock")).open("a")
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise DispatchError("worktree_busy") from None
        run_dir.mkdir(parents=True, mode=0o700)
        receipt = {"run_id": str(uuid.uuid4()), "backend": "pi", "state": "starting", "started_at": timestamp(),
                   "worktree": str(worktree), "provider": config["provider"], "model": config["model"],
                   "thinking_requested": config["thinking"], "base_sha": initial_head,
                   "timeout_seconds": config["timeout_seconds"], "max_turns": config["max_turns"]}
        save_json(run_dir / "run.json", receipt)
        signal.signal(signal.SIGTERM, interrupted)
        events = Events(config)
        with brief.open("rb") as prompt:
            process = subprocess.Popen(command, cwd=worktree, stdin=prompt, stdout=subprocess.PIPE,
                                       stderr=subprocess.DEVNULL, start_new_session=True)
            receipt.update(state="running", pid=process.pid)
            save_json(run_dir / "run.json", receipt)
            print(json.dumps({"run_id": receipt["run_id"], "pid": process.pid, "run_dir": str(run_dir)}), flush=True)
            returncode = consume(process, events, config["timeout_seconds"])
        receipt.update(exit_code=returncode, turns=events.turns, pi_session_id=events.session_id)
        if returncode:
            raise DispatchError("pi_exit_nonzero")
        if git(checkout, "rev-parse", "HEAD") != initial_head or git(checkout, "rev-parse", "--abbrev-ref", "HEAD") != initial_branch:
            raise DispatchError("implementer_changed_git_history")
        report = events.report()
        save_json(run_dir / "report.json", report)
        receipt.update(state="reported_" + report["status"], report="report.json")
        outcome = 0 if report["status"] == "complete" else 1
    except KeyboardInterrupt:
        if receipt is not None:
            receipt.update(state="interrupted", reason="interrupted")
        else:
            print(json.dumps({"state": "interrupted", "reason": "interrupted"}), file=sys.stderr)
        outcome = 130
    except (DispatchError, OSError, ValueError, subprocess.SubprocessError):
        error = sys.exc_info()[1]
        reason = str(error) if isinstance(error, DispatchError) else "dispatch_or_configuration_error"
        if receipt is not None:
            receipt.update(state="failed", reason=reason)
        else:
            print(json.dumps({"state": "failed", "reason": reason}), file=sys.stderr)
        outcome = 1
    finally:
        signal.signal(signal.SIGTERM, signal.SIG_IGN)
        signal.signal(signal.SIGINT, signal.SIG_IGN)
        if process is not None:
            try:
                stop_group(process)
            except (OSError, subprocess.SubprocessError):
                outcome = 1
                if receipt is not None:
                    receipt.update(state="failed", cleanup_reason="cleanup_unconfirmed")
            if process.stdout is not None:
                process.stdout.close()
        if receipt is not None:
            receipt.update(finished_at=timestamp(), elapsed_seconds=round(time.monotonic() - started, 3))
            try:
                save_json(run_dir / "run.json", receipt)
                print(json.dumps({"run_id": receipt["run_id"], "state": receipt["state"],
                                  "reason": receipt.get("reason"), "cleanup_reason": receipt.get("cleanup_reason"),
                                  "run_dir": str(run_dir)}), flush=True)
            except OSError:
                outcome = 1
                print('{"state":"failed","reason":"receipt_write_failed"}', file=sys.stderr)
        if lock is not None:
            lock.close()
        os.umask(previous_umask)
    return outcome


if __name__ == "__main__":
    sys.exit(main())
