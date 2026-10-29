import sys
import unittest

sys.path.insert(0, "scripts")
from textutil import Finding, has_hangul, line_col, strip_ignored  # noqa: E402


class TextutilTest(unittest.TestCase):
    def test_strip_keeps_positions(self):
        src = "앞 `통해` 뒤\n```\n코드 통해\n```\n끝"
        out = strip_ignored(src)
        self.assertEqual(len(out), len(src))
        self.assertNotIn("통해", out)
        self.assertEqual(out.count("\n"), src.count("\n"))

    def test_strip_ignore_region(self):
        src = "가\n<!-- monkey-lint: off -->\n이를 통해\n<!-- monkey-lint: on -->\n나"
        self.assertNotIn("통해", strip_ignored(src))

    def test_strip_keeps_visual_marker(self):
        self.assertIn("<!-- visual:", strip_ignored("<!-- visual: flow | Q: 어디서 갈리나? -->"))

    def test_outer_four_backtick_fence_not_closed_by_three(self):
        src = "````md\n```\n통해\n```\n통해\n````\n끝 통해"
        out = strip_ignored(src)
        self.assertEqual(out.count("통해"), 1)
        self.assertIn("끝 통해", out)

    def test_closing_fence_with_text_does_not_close(self):
        src = "```\n통해\n``` 설명\n통해\n```\n끝"
        self.assertNotIn("통해", strip_ignored(src))

    def test_inline_code_with_comment_open_keeps_following_text(self):
        self.assertIn("통해", strip_ignored("`<!--` 이를 통해 설명"))

    def test_line_col(self):
        self.assertEqual(line_col("ab\ncd", 3), (2, 1))

    def test_has_hangul(self):
        self.assertFalse(has_hangul("hello world " * 10))
        self.assertTrue(has_hangul("가나다라마바사아자차" * 3))

    def test_finding_str(self):
        self.assertEqual(str(Finding("A01", 2, 3, "통해", "msg")), "2:3 A01 msg | 통해")


if __name__ == "__main__":
    unittest.main()
