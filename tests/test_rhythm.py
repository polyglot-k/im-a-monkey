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

    def test_formal_register_run_flagged(self):
        t = ("배포는 매주 화요일에 나갑니다. 변경이 큰 주에는 하루 전에 리허설 환경에서 먼저 확인했습니다. "
             "문제가 생기면 바로 되돌렸습니다. 되돌린 뒤에는 원인을 적어 두고 다음 배포 전에 같이 봤습니다. "
             "급한 수정은 따로 올렸습니다. 이때도 리뷰는 한 명 이상에게 받았습니다.")
        self.assertIn("A15 같은 어미 연속 5회", flags(measure(t)))

    def test_varied_formal_endings_not_flagged(self):
        t = ("배포는 매주 화요일에 합니다. 변경이 큰 주에는 하루 전에 리허설 환경에서 먼저 확인했습니다. "
             "문제가 생기면 어떻게 할까요? 되돌린 뒤 원인을 적어 두고 다음 배포 전에 같이 봅니다. "
             "급한 수정은 예외입니다. 이때도 리뷰는 한 명 이상에게 받아야 됩니다.")
        self.assertEqual([f for f in flags(measure(t)) if f.startswith("A15")], [])

    def test_formal_share_counts_three_chars(self):
        t = " ".join(["설정을 바꿨습니다.", "기본값은 열 개입니다.", "로그가 남습니다.", "재시작이 필요합니다.", "캐시는 비웠습니다.",
                      "다음 단계는 배포입니다.", "검증은 끝났습니까?", "롤백 절차는 그대로입니다.", "담당자는 두 명이 됩니다.", "끝."])
        self.assertEqual([f for f in flags(measure(t)) if "비율" in f], [])

    def test_same_ending_share_flagged(self):
        a, rest = "설정을 바꿔요.", ["값을 읽었죠.", "로그가 남습니다.", "끝났나요?", "다음 단계."]
        t = " ".join([a, rest[0], a, rest[1], a, rest[2], a, rest[3], rest[0], rest[1]])
        self.assertEqual(measure(t)["max_same_ending_run"], 1)
        self.assertIn("A15 같은 어미 비율 40%", flags(measure(t)))

    def test_no_long_sentences_flagged(self):
        short = ["설정을 바꿔요.", "값을 읽었죠.", "다시 돌렸어요?", "로그가 남습니다.", "끝."] * 3
        self.assertIn("A15 긴 문장이 거의 없음: 붙어 다니는 두 문장을 이어 쓰세요", flags(measure(" ".join(short))))
        long_ = "어제 저녁 배포 뒤 결제 화면이 느려졌다는 문의가 들어와서 로그를 보니 외부 결제사 응답이 평소보다 세 배쯤 늦게 돌아오고 있었고 그 사이 앱의 재시도가 겹쳐 대기열이 점점 길어졌어요."
        self.assertGreaterEqual(len(long_), 100)
        self.assertFalse(any("긴 문장이 거의 없음" in f for f in flags(measure(" ".join(short + [long_])))))

    def test_bullet_ratio(self):
        self.assertAlmostEqual(measure("- a\n- b\n문장이다.\n- c")["bullet_ratio"], 0.75)


    def test_overused_variation_ending(self):
        sents = ["이 문장은 길이가 조금씩 다르게 쓰였죠.", "짧죠.", "여기 문장은 조금 더 길게 늘여서 썼어요.", "그래서 고르게 보이지 않죠.",
                 "끝은 다시 해요체로 맺어요.", "이번에도 섞었죠.", "그다음 문장은 평범하게 끝나요.", "마지막으로 하나 더 넣었죠.",
                 "정리하면 이렇습니다.", "그리고 한 줄 더 써 봐요."]
        self.assertTrue(any("죠" in f for f in flags(measure(" ".join(sents)))))

    def test_html_lines_not_sentences(self):
        t = "<p>\n  <a href=\"#a\">가</a> ·\n  <a href=\"#b\">나</a> ·\n  <a href=\"#c\">다</a> ·\n  <a href=\"#d\">라</a> ·\n</p>\n본문 문장이에요."
        self.assertEqual(measure(t)["sentences"], 1)


if __name__ == "__main__":
    unittest.main()
