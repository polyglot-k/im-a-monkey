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


if __name__ == "__main__":
    unittest.main()
