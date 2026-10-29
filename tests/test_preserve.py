import sys
import unittest

sys.path.insert(0, "scripts")
from preserve import compare  # noqa: E402


class PreserveTest(unittest.TestCase):
    def test_number_loss(self):
        r = compare("p95가 820ms에서 310ms로 줄었다.", "p95가 크게 줄었다.")
        self.assertEqual(r["missing_numbers"], ["820", "310"])
        self.assertFalse(r["ok"])

    def test_negation_flip(self):
        self.assertEqual(compare("재시도하지 않는다.", "재시도한다.")["negation_delta"], -1)

    def test_style_only_change_ok(self):
        r = compare("이 API를 통해 3건을 가져오고자 합니다.", "이 API로 3건을 가져옵니다.")
        self.assertTrue(r["ok"])
        self.assertGreater(r["edit_rate"], 0)

    def test_token_trailing_period(self):
        self.assertEqual(compare("캐시는 Redis.", "Redis와 함께 쓴다.")["missing_tokens"], [])

    def test_link_kept(self):
        self.assertFalse(compare("[문서](https://x.y/a) 참고", "문서 참고")["ok"])


if __name__ == "__main__":
    unittest.main()
