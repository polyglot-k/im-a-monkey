import sys
import unittest

sys.path.insert(0, "scripts")
from rhythm import flags, measure  # noqa: E402


class RhythmTest(unittest.TestCase):
    def test_same_ending_run(self):
        m = measure("가는 거죠. 나는 거죠. 다는 거죠. 라는 거죠.")
        self.assertEqual(m["max_same_ending_run"], 4)
        self.assertTrue(any(f.startswith("A15") for f in flags(m)))

    def test_varied_text_no_flags(self):
        t = "짧다. 이 문장은 조금 더 길게 써서 리듬을 바꾼다. 그래요? 마지막 문장은 다시 꽤 길게 늘여서 여러 어절을 담아 본다. 끝. 정말 끝이에요."
        self.assertEqual([f for f in flags(measure(t)) if f.startswith("A15")], [])

    def test_formal_register_not_flagged(self):
        t = ("배포는 매주 화요일에 합니다. 변경이 큰 주에는 하루 전에 리허설 환경에서 먼저 확인합니다. "
             "문제가 생기면 되돌립니다. 되돌린 뒤에는 원인을 적어 두고 다음 배포 전에 같이 봅니다. "
             "급한 수정은 따로 올립니다. 이때도 리뷰는 한 명 이상에게 받습니다.")
        self.assertEqual([f for f in flags(measure(t)) if f.startswith("A15")], [])

    def test_bullet_ratio(self):
        self.assertAlmostEqual(measure("- a\n- b\n문장이다.\n- c")["bullet_ratio"], 0.75)


    def test_html_lines_not_sentences(self):
        t = "<p>\n  <a href=\"#a\">가</a> ·\n  <a href=\"#b\">나</a> ·\n  <a href=\"#c\">다</a> ·\n  <a href=\"#d\">라</a> ·\n</p>\n본문 문장이에요."
        self.assertEqual(measure(t)["sentences"], 1)


if __name__ == "__main__":
    unittest.main()
