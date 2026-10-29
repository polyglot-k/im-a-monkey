import sys
import unittest

sys.path.insert(0, "scripts")
from rhythm import flags, measure  # noqa: E402


class RhythmTest(unittest.TestCase):
    def test_same_ending_run(self):
        m = measure("가는 합니다. 나는 합니다. 다는 합니다. 라는 합니다.")
        self.assertEqual(m["max_same_ending_run"], 4)
        self.assertTrue(any(f.startswith("A15") for f in flags(m)))

    def test_varied_text_no_flags(self):
        t = "짧다. 이 문장은 조금 더 길게 써서 리듬을 바꾼다. 그래요? 마지막 문장은 다시 꽤 길게 늘여서 여러 어절을 담아 본다. 끝. 정말 끝이에요."
        self.assertEqual([f for f in flags(measure(t)) if f.startswith("A15")], [])

    def test_bullet_ratio(self):
        self.assertAlmostEqual(measure("- a\n- b\n문장이다.\n- c")["bullet_ratio"], 0.75)


if __name__ == "__main__":
    unittest.main()
