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

    def test_compare_needs_emphasis(self):
        self.assertIn("V03", {f.id for f in check("<!-- visual: compare | Q: 무엇이 다른가? -->")})

    def test_badge_density(self):
        src = "## A\n> [!NOTE]\n> x\n[추정] 3건 [측정] 5건\n## B\n[측정] 1건"
        self.assertEqual([f.id for f in check(src)], ["V04"])


if __name__ == "__main__":
    unittest.main()
