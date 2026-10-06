"""Process-contract tests using a synthetic Pi executable; no model or credentials."""

import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import tempfile
import time
import unittest

PACKAGE = Path(__file__).resolve().parents[1]
DISPATCH = PACKAGE / "orchestration-mix/scripts/dispatch.py"

FAKE_PI = r'''#!/usr/bin/env python3
import json, os, pathlib, subprocess, sys, time
brief = json.load(sys.stdin)
mode = brief.get("mode", "success")
pathlib.Path("invocation.json").write_text(json.dumps({"argv":sys.argv[1:], "cwd":os.getcwd()}))
def emit(event):
    print(json.dumps(event, ensure_ascii=False), flush=True)
def assistant(status="complete", reason="stop", model="test-model"):
    report = {"status":status, "result":"Changed sample.py\u2028preserved text", "evidence":"synthetic check passed", "remaining":"none"}
    if mode == "missing_field": del report["evidence"]
    text = "not a report" if mode == "invalid_report" else json.dumps(report, ensure_ascii=False)
    if mode == "fenced": text = "```json\n" + text + "\n```"
    emit({"type":"message_end", "message":{"role":"assistant", "provider":"test", "model":model,
         "stopReason":reason, "errorMessage":"SYNTHETIC_PRIVATE_VALUE", "content":[{"type":"text","text":text}]}})
emit({"type":"session", "id":"synthetic-session"})
emit({"type":"agent_start"})
emit({"type":"turn_start"})
if mode in ("hang", "child", "closed_stdout"):
    if mode == "child":
        child = subprocess.Popen([sys.executable,"-c","import signal,time; signal.signal(signal.SIGTERM,signal.SIG_IGN); time.sleep(60)"])
        pathlib.Path("child.pid").write_text(str(child.pid))
    if mode == "closed_stdout": os.close(1)
    time.sleep(60)
elif mode == "invalid_event":
    print("SYNTHETIC_PRIVATE_VALUE", flush=True)
elif mode == "truncated":
    sys.stdout.write('{"type":"agent_settled"}')
elif mode == "turn_limit":
    for _ in range(8): emit({"type":"turn_start"})
elif mode == "exit_nonzero":
    print("SYNTHETIC_PRIVATE_VALUE",file=sys.stderr)
    sys.exit(7)
else:
    if mode == "history":
        pathlib.Path("unexpected.txt").write_text("synthetic")
        subprocess.run(["git","add","unexpected.txt"],check=True,stdout=subprocess.DEVNULL)
        subprocess.run(["git","-c","user.name=Test","-c","user.email=test@example.invalid","-c","commit.gpgsign=false","commit","-m","synthetic"],check=True,stdout=subprocess.DEVNULL)
    if mode == "recovery":
        assistant(reason="error")
        emit({"type":"agent_end","willRetry":True})
        emit({"type":"agent_start"})
        emit({"type":"turn_start"})
    status = mode if mode in ("partial","blocked") else "complete"
    reason = {"provider_error":"error","aborted":"aborted","length":"length"}.get(mode,"stop")
    assistant(status,reason,"wrong-model" if mode == "wrong_model" else "test-model")
    emit({"type":"agent_end","willRetry":False})
    if mode != "unsettled": emit({"type":"agent_settled"})
'''


class DispatchTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="mix test ")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.checkout = self.root / "task checkout"
        self.checkout.mkdir()
        self.env = dict(os.environ, GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1")
        self.git("init", "-q")
        (self.checkout / "base.txt").write_text("synthetic base\n")
        self.git("add", "base.txt")
        self.git("-c", "user.name=Test", "-c", "user.email=test@example.invalid",
                 "-c", "commit.gpgsign=false", "commit", "-qm", "synthetic base")
        self.pi = self.root / "fake pi"
        self.pi.write_text(FAKE_PI)
        self.pi.chmod(0o755)
        self.brief = self.root / "brief.json"
        self.calls = 0
        self.config = self.root / "config.json"
        self.settings = {"provider":"test", "model":"test-model", "thinking":"high",
                         "timeout_seconds":5, "max_turns":4}
        self.config.write_text(json.dumps(self.settings))
        self.output = self.root / "private evidence"

    def git(self, *args):
        return subprocess.run(["git", "-C", str(self.checkout), *args], check=True,
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=self.env)

    def command(self, mode="success", output=None):
        self.calls += 1
        self.brief = self.root / ("brief-%d.json" % self.calls)
        self.brief.write_text(json.dumps({"mode":mode}))
        return [sys.executable,str(DISPATCH),"--worktree",str(self.checkout),
                "--brief",str(self.brief),"--run-dir",str(output or self.output),
                "--config",str(self.config),"--pi",str(self.pi)]

    def run_case(self, mode="success", extra=(), output=None):
        result = subprocess.run(self.command(mode,output) + list(extra), capture_output=True,
                                text=True, timeout=12, env=self.env)
        receipt = self.output / "run.json"
        return result, json.loads(receipt.read_text()) if receipt.is_file() else None

    def test_success_and_argument_boundaries(self):
        result, receipt = self.run_case()
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertEqual(receipt["state"],"reported_complete")
        report = json.loads((self.output / "report.json").read_text())
        self.assertIn("\u2028",report["result"])
        invocation = json.loads((self.checkout / "invocation.json").read_text())
        self.assertEqual(Path(invocation["cwd"]).resolve(),self.checkout.resolve())
        args = invocation["argv"]
        for flag,value in [("--provider","test"),("--model","test-model"),("--thinking","high")]:
            self.assertEqual(args[args.index(flag)+1],value)
        self.assertIn("--no-session",args)
        self.assertNotIn("--continue",args)
        self.assertNotIn("--resume",args)
        self.assertEqual((self.output / "report.json").stat().st_mode & 0o777,0o600)
        self.assertEqual(self.output.stat().st_mode & 0o777,0o700)

    def test_partial_and_blocked_reports_are_not_success(self):
        for mode in ["partial","blocked"]:
            with self.subTest(mode=mode):
                output = self.root / mode
                result,_ = self.run_case(mode,output=output)
                self.assertEqual(result.returncode,1)
                self.assertEqual(json.loads((output / "run.json").read_text())["state"],"reported_"+mode)

    def test_failed_model_response_with_zero_exit(self):
        for mode in ["provider_error","aborted","length"]:
            with self.subTest(mode=mode):
                output = self.root / mode
                result,_ = self.run_case(mode,output=output)
                receipt = json.loads((output / "run.json").read_text())
                self.assertEqual(result.returncode,1)
                self.assertEqual(receipt["exit_code"],0)
                self.assertEqual(receipt["reason"],"assistant_did_not_finish")
                self.assertFalse((output / "report.json").exists())

    def test_recovered_run_and_fenced_report(self):
        for mode in ["recovery","fenced"]:
            with self.subTest(mode=mode):
                result,_ = self.run_case(mode,output=self.root / mode)
                self.assertEqual(result.returncode,0,result.stderr)

    def test_invalid_events_reports_and_model_identity_fail(self):
        cases = {"invalid_event":"invalid_json_event", "truncated":"truncated_event",
                 "unsettled":"missing_settled_event", "invalid_report":"invalid_report",
                 "missing_field":"invalid_report", "wrong_model":"model_mismatch",
                 "turn_limit":"turn_limit", "exit_nonzero":"pi_exit_nonzero"}
        for mode,reason in cases.items():
            with self.subTest(mode=mode):
                output = self.root / mode
                result,_ = self.run_case(mode,output=output)
                receipt = json.loads((output / "run.json").read_text())
                self.assertEqual(result.returncode,1)
                self.assertEqual(receipt["reason"],reason)
                self.assertNotIn("SYNTHETIC_PRIVATE_VALUE",result.stdout+result.stderr+(output / "run.json").read_text())

    def test_deadline_with_silent_or_closed_output(self):
        self.settings["timeout_seconds"] = 0.3
        self.config.write_text(json.dumps(self.settings))
        for mode in ["hang","closed_stdout"]:
            with self.subTest(mode=mode):
                output = self.root / mode
                start = time.monotonic()
                result,_ = self.run_case(mode,output=output)
                self.assertEqual(result.returncode,1)
                self.assertLess(time.monotonic()-start,4)
                self.assertEqual(json.loads((output / "run.json").read_text())["reason"],"timeout")

    def test_timeout_stops_owned_descendant(self):
        self.settings["timeout_seconds"] = 0.5
        self.config.write_text(json.dumps(self.settings))
        result,receipt = self.run_case("child")
        self.assertEqual(result.returncode,1)
        self.assertEqual(receipt["reason"],"timeout")
        child = int((self.checkout / "child.pid").read_text())
        deadline = time.monotonic()+2
        while time.monotonic() < deadline:
            try:
                os.kill(child,0)
            except ProcessLookupError:
                break
            time.sleep(0.05)
        else:
            self.fail("owned descendant is still present")

    def test_existing_evidence_is_preserved(self):
        self.output.mkdir()
        (self.output / "sentinel").write_text("preserve")
        result,receipt = self.run_case()
        self.assertEqual(result.returncode,1)
        self.assertIsNone(receipt)
        self.assertEqual((self.output / "sentinel").read_text(),"preserve")
        self.assertFalse((self.checkout / "invocation.json").exists())

    def test_dry_run_creates_nothing_and_does_not_run_pi(self):
        result,receipt = self.run_case(extra=["--dry-run"])
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertIsNone(receipt)
        self.assertFalse(self.output.exists())
        self.assertFalse((self.checkout / "invocation.json").exists())

    def test_rejects_unignored_evidence_and_accepts_ignored_evidence(self):
        inside = self.checkout / ".agent-runs/test"
        result,_ = self.run_case(output=inside)
        self.assertEqual(result.returncode,1)
        self.assertFalse(inside.exists())
        (self.checkout / ".git/info/exclude").write_text("/.agent-runs/\n")
        result,_ = self.run_case(output=inside)
        self.assertEqual(result.returncode,0,result.stderr)

    def test_history_change_is_reported_without_rollback(self):
        original = self.git("rev-parse","HEAD").stdout
        result,receipt = self.run_case("history")
        self.assertEqual(result.returncode,1)
        self.assertEqual(receipt["reason"],"implementer_changed_git_history")
        self.assertNotEqual(self.git("rev-parse","HEAD").stdout,original)
        self.assertTrue((self.checkout / "unexpected.txt").exists())

    def test_partial_ignore_rules_do_not_leak_report_or_temporary_files(self):
        inside = self.checkout / ".agent-runs/test"
        for rules in ["/.agent-runs/test/run.json\n",
                      "/.agent-runs/test/*\n!/.agent-runs/test/report.json.tmp\n"]:
            with self.subTest(rules=rules):
                (self.checkout / ".git/info/exclude").write_text(rules)
                result,_ = self.run_case(output=inside)
                self.assertEqual(result.returncode,1)
                self.assertFalse(inside.exists())
                self.assertFalse((self.checkout / "invocation.json").exists())

    def test_one_runner_per_checkout_and_interruption_receipt(self):
        running = subprocess.Popen(self.command("hang"),stdout=subprocess.PIPE,stderr=subprocess.PIPE,env=self.env)
        def cleanup():
            if running.poll() is None:
                running.send_signal(signal.SIGTERM)
            running.communicate(timeout=6)
        self.addCleanup(cleanup)
        deadline = time.monotonic()+5
        receipt = self.output / "run.json"
        while time.monotonic() < deadline:
            if receipt.exists() and json.loads(receipt.read_text()).get("state") == "running": break
            time.sleep(0.02)
        self.assertEqual(json.loads(receipt.read_text())["state"],"running")
        second = self.root / "second"
        other_tmp = self.root / "other tmpdir"
        other_tmp.mkdir()
        self.env["TMPDIR"] = str(other_tmp)
        result,_ = self.run_case(output=second)
        self.assertEqual(result.returncode,1)
        self.assertIn("worktree_busy",result.stderr)
        self.assertFalse(second.exists())
        running.send_signal(signal.SIGTERM)
        running.communicate(timeout=6)
        self.assertEqual(running.returncode,130)
        self.assertEqual(json.loads(receipt.read_text())["state"],"interrupted")

    def test_invalid_configuration_does_not_run_pi(self):
        self.settings["timeout_seconds"] = -1
        self.config.write_text(json.dumps(self.settings))
        result,receipt = self.run_case()
        self.assertEqual(result.returncode,1)
        self.assertIsNone(receipt)
        self.assertIn("invalid_timeout",result.stderr)
        self.assertFalse((self.checkout / "invocation.json").exists())


if __name__ == "__main__":
    unittest.main()
