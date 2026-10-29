import sys
import unittest

sys.path.insert(0, "scripts")
from lint import lint_text  # noqa: E402
from patterns import PATTERNS  # noqa: E402
from textutil import catalog_ids  # noqa: E402


class LintTest(unittest.TestCase):
    def test_detects_translationese(self):
        ids = {f.id for f in lint_text("이 API를 통해 데이터를 가져오고자 합니다.")}
        self.assertEqual(ids, {"A01", "A03"})

    def test_ignores_code(self):
        self.assertEqual(lint_text("`통해` 와\n```\nfoo.py:12 를 통해\n```"), [])

    def test_ignore_region(self):
        src = "<!-- monkey-lint: off -->\n이를 통해\n<!-- monkey-lint: on -->"
        self.assertEqual(lint_text(src), [])

    def test_code_map_section_allows_paths(self):
        src = "본문 a.py:3 참고\n\n## 코드 읽기 지도\n- a.py:3"
        self.assertEqual([f.line for f in lint_text(src) if f.id == "T03"], [1])

    def test_crlf_line_numbers(self):
        self.assertEqual(lint_text("첫 줄\r\n이를 통해 간다")[0].line, 2)

    def test_pr_type_has_floor(self):
        self.assertEqual([f.id for f in lint_text("말 " * 79, doc_type="pr")], ["L02"])
        self.assertEqual(lint_text("말 " * 80, doc_type="pr"), [])

    def test_length_limit(self):
        f = lint_text("말 " * 151, doc_type="message")
        self.assertEqual([x.id for x in f], ["L01"])
        self.assertEqual(lint_text("말 " * 150, doc_type="message"), [])

    def test_length_minimum(self):
        f = lint_text("말 " * 99, doc_type="howto")
        self.assertEqual([x.id for x in f], ["L02"])
        self.assertEqual(lint_text("말 " * 100, doc_type="howto"), [])
        self.assertEqual(lint_text("말 " * 5), [])

    def test_emoji_excludes_technical_symbols(self):
        self.assertEqual([f for f in lint_text("✓ 완료 ✗ 실패 ★ ⚠") if f.id == "A09"], [])
        self.assertEqual([f.id for f in lint_text("🚀 배포")], ["A09"])

    def test_every_pattern_id_in_catalog(self):
        self.assertTrue({p[0] for p in PATTERNS} <= catalog_ids("catalog/antipatterns.md"))

    def test_fixtures(self):
        with open("tests/fixtures/bad_ai.md", encoding="utf-8") as f:
            bad = f.read()
        with open("tests/fixtures/good.md", encoding="utf-8") as f:
            good = f.read()
        self.assertGreaterEqual(len({f.id for f in lint_text(bad)}), 8)
        self.assertEqual(lint_text(good), [])

    def test_multiple_files_and_dirs_prefix_path(self):
        import os, subprocess, tempfile
        with tempfile.TemporaryDirectory() as d:
            os.makedirs(os.path.join(d, "sub"))
            for n, body in (("ok.md", "깨끗한 문장이에요.\n"), ("sub/bad.md", "이를 통해 해결했다.\n")):
                with open(os.path.join(d, n), "w", encoding="utf-8") as f:
                    f.write(body)
            r = subprocess.run(["python3", "scripts/lint.py", d], capture_output=True, text=True)
            self.assertEqual(r.returncode, 1)
            self.assertTrue(r.stdout.startswith(os.path.join(d, "sub", "bad.md") + ":"), r.stdout)
            r = subprocess.run(["python3", "scripts/lint.py", os.path.join(d, "ok.md")], capture_output=True, text=True)
            self.assertEqual((r.returncode, r.stdout), (0, ""))


if __name__ == "__main__":
    unittest.main()
