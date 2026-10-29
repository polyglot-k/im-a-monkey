import os
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, "scripts")
from coderef import check  # noqa: E402


def git(repo, *args):
    cfg = ["-c", "user.name=t", "-c", "user.email=t@example.com", "-c", "commit.gpgsign=false"]
    return subprocess.run(["git", "-C", repo, *cfg, *args], check=True, capture_output=True, text=True).stdout.strip()


class CoderefTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.repo = self._tmp.name
        git(self.repo, "init", "-q")
        with open(os.path.join(self.repo, "a.py"), "w", encoding="utf-8") as f:
            f.write("import os\ndef cancel_order():\n    pass\n")
        git(self.repo, "add", "a.py")
        git(self.repo, "commit", "-q", "-m", "init")
        self.sha = git(self.repo, "rev-parse", "HEAD")

    def test_valid_ref(self):
        self.assertEqual(check(f"`a.py:2@{self.sha}`", self.repo), [])

    def test_out_of_range(self):
        self.assertEqual(check(f"`a.py:9@{self.sha}`", self.repo)[0].message, "줄 범위 밖")

    def test_symbol_mismatch(self):
        url = f"https://github.com/o/r/blob/{self.sha}/a.py#L1"
        self.assertIn("cancel_order", check(f"[`cancel_order`]({url})", self.repo)[0].message)

    def test_unknown_sha(self):
        self.assertEqual(len(check("`a.py:1@deadbeef`", self.repo)), 1)

    def test_skips_fenced_and_off_regions(self):
        bad = f"`a.py:99@{self.sha}`"
        src = f"```\n{bad}\n```\n<!-- monkey-lint: off -->\n{bad}\n<!-- monkey-lint: on -->\n{bad}"
        found = check(src, self.repo)
        self.assertEqual([f.line for f in found], [7])

    def test_bracket_inside_backticked_label(self):
        url = f"https://github.com/o/r/blob/{self.sha}/a.py#L2"
        self.assertEqual(check(f"[`cancel_order[0]`]({url})", self.repo), [])
        out = check(f"[`cancel_order[0]`]({url[:-1]}9)", self.repo)  # 줄 범위 밖인 링크도 잡아야 한다
        self.assertEqual([f.message for f in out], ["줄 범위 밖"])

    def test_git_missing_exits_2(self):
        with tempfile.TemporaryDirectory() as d:
            doc = os.path.join(d, "d.md")
            with open(doc, "w", encoding="utf-8") as f:
                f.write(f"`a.py:1@{self.sha}`")
            r = subprocess.run([sys.executable, "scripts/coderef.py", doc, "--repo", d],
                               capture_output=True, text=True, env={"PATH": d})
        self.assertEqual(r.returncode, 2)
        self.assertIn("git", r.stderr)
        self.assertNotIn("Traceback", r.stderr)


if __name__ == "__main__":
    unittest.main()
