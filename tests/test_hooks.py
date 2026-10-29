import json
import os
import re
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class HookCase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.env = {**os.environ, "XDG_CONFIG_HOME": self.tmp}
        self.env.pop("IM_A_MONKEY_VOICE", None)

    def run_hook(self, name, payload):
        r = subprocess.run([sys.executable, os.path.join(ROOT, "hooks", name)],
                           input=json.dumps(payload), capture_output=True, text=True, env=self.env)
        self.assertEqual(r.returncode, 0)
        return r.stdout.strip()

    def cli(self, *args):
        return subprocess.run([sys.executable, os.path.join(ROOT, "hooks", "config.py"), *args],
                              capture_output=True, text=True, env=self.env)

    def write_tmp(self, name, text):
        p = os.path.join(self.tmp, name)
        with open(p, "w", encoding="utf-8") as f:
            f.write(text)
        return p


class TestHooks(HookCase):
    def test_session_start_injects_and_respects_off(self):
        out = self.run_hook("session_start.py", {"hook_event_name": "SessionStart"})
        self.assertIn("결론 먼저", json.loads(out)["hookSpecificOutput"]["additionalContext"])
        self.assertEqual(self.cli("set", "off").returncode, 0)
        self.assertEqual(self.run_hook("session_start.py", {}), "")

    def test_reminder_only_for_korean(self):
        self.assertEqual(self.run_hook("prompt_reminder.py", {"prompt": "fix the bug"}), "")
        self.assertNotEqual(self.run_hook("prompt_reminder.py", {"prompt": "버그 고쳐줘"}), "")

    def test_post_write_reports_findings(self):
        p = self.write_tmp("a.md", "이 API를 통해 데이터를 가져오고자 합니다. " * 3)
        out = self.run_hook("post_write_lint.py", {"tool_name": "Write", "tool_input": {"file_path": p}})
        self.assertIn("A01", out)

    def test_post_write_skips_non_korean(self):
        p = self.write_tmp("README.md", "Use this through the API. " * 20)
        self.assertEqual(self.run_hook("post_write_lint.py", {"tool_name": "Write", "tool_input": {"file_path": p}}), "")

    def test_post_write_skips_large(self):
        p = self.write_tmp("big.md", "이를 통해 " * 40000)
        self.assertEqual(self.run_hook("post_write_lint.py", {"tool_name": "Write", "tool_input": {"file_path": p}}), "")

    def test_hooks_survive_bad_stdin(self):
        for h in ["session_start.py", "prompt_reminder.py", "post_write_lint.py"]:
            r = subprocess.run([sys.executable, os.path.join(ROOT, "hooks", h)], input="not json",
                               capture_output=True, text=True, env=self.env)
            self.assertEqual(r.returncode, 0)

    def test_config_rejects_bad_voice(self):
        self.assertEqual(self.cli("set", "pirate").returncode, 2)

    def test_persona_rule_count(self):
        with open(os.path.join(ROOT, "persona", "core.md"), encoding="utf-8") as f:
            rules = [l for l in f if re.match(r"^\d+\. ", l)]
        self.assertLessEqual(len(rules), 10)


if __name__ == "__main__":
    unittest.main()
