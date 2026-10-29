import sys
import unittest

sys.path.insert(0, "scripts")
from visual import check  # noqa: E402


class VisualTest(unittest.TestCase):
    def test_leftover_marker(self):
        self.assertEqual([f.id for f in check("<!-- visual: flow | Q: 어디서 갈리나? -->")], ["V01"])

    def test_figure_needs_question_caption(self):
        self.assertEqual([f.id for f in check("```mermaid\ngraph TD\n```\n그림 1. 흐름이다.")], ["V02"])
        self.assertEqual(check("```mermaid\ngraph TD\n```\n그림 1. 요청은 어디서 갈리나? 결제 전이다."), [])

    def test_html_svg_captions(self):
        q = "그림 1. 요청은 어디서 갈리나? 결제 전이다."
        self.assertEqual(check('<svg viewBox="0 0 10 10"><rect/></svg>\n<p>' + q + "</p>"), [])
        self.assertEqual(check('<figure><svg viewBox="0 0 1 1"/><figcaption class="c">' + q
                               + "</figcaption></figure>"), [])
        self.assertEqual(check("<svg>\n  <g>\n    <rect/>\n  </g>\n</svg>\n" + q), [])
        self.assertEqual([f.id for f in check("<svg><rect/></svg>\n<p>그림 1. 흐름이다.</p>")], ["V02"])

    def test_mermaid_inside_outer_fence_is_not_a_figure(self):
        src = "````md\n```mermaid\nflowchart LR\n```\n````\n"
        self.assertEqual([f.id for f in check(src)], [])

    def test_compare_needs_emphasis(self):
        self.assertIn("V03", {f.id for f in check("<!-- visual: compare | Q: 무엇이 다른가? -->")})

    def test_badge_density(self):
        src = "## A\n> [!NOTE]\n> x\n[추정] 3건 [측정] 5건\n## B\n[측정] 1건"
        self.assertEqual([f.id for f in check(src)], ["V04"])

    def test_multiple_files_and_dirs_prefix_path(self):
        import os, subprocess, tempfile
        with tempfile.TemporaryDirectory() as d:
            os.makedirs(os.path.join(d, "sub"))
            for n, body in (("ok.md", "깨끗한 문장이에요.\n"), ("sub/bad.md", "<!-- visual: flow | Q: 어디서? -->\n")):
                with open(os.path.join(d, n), "w", encoding="utf-8") as f:
                    f.write(body)
            r = subprocess.run(["python3", "scripts/visual.py", d], capture_output=True, text=True)
            self.assertEqual(r.returncode, 1)
            self.assertTrue(r.stdout.startswith(os.path.join(d, "sub", "bad.md") + ":"), r.stdout)
            r = subprocess.run(["python3", "scripts/visual.py", os.path.join(d, "ok.md")], capture_output=True, text=True)
            self.assertEqual((r.returncode, r.stdout), (0, ""))


if __name__ == "__main__":
    unittest.main()
