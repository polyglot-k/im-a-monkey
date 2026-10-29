import subprocess
import sys
import unittest

sys.path.insert(0, "scripts")

from human_check import SEP, run  # noqa: E402


class HumanCheckTest(unittest.TestCase):
    def test_scan_counts_lint(self):
        out = run("scan", "이 API를 통해 데이터를 가져오고자 합니다.")
        self.assertEqual(out["by_id"], {"A01": 1, "A03": 1})

    def test_compare_reports_before_after_and_preserve(self):
        out = run("compare", f"이 API를 통해 3건을 가져오고자 합니다.\n{SEP}\n이 API로 3건을 가져옵니다.")
        self.assertEqual(out["before"]["lint_count"], 2)
        self.assertEqual(out["after"]["lint_count"], 0)
        self.assertTrue(out["preserve"]["ok"])

    def test_compare_flags_register_mixing(self):
        orig = "검색이 빨라졌습니다. 필터도 쉬워졌습니다. 정렬 옵션도 들어갔습니다."
        rev = "검색이 빨라졌습니다. 필터도 쉬워졌죠. 정렬 옵션도 들어갔고요."
        self.assertEqual(run("compare", f"{orig}\n{SEP}\n{rev}")["register_mixed"], ["해요체 2문장"])
        same = "검색이 빨라졌습니다. 필터와 정렬 옵션도 들어갔습니다."
        self.assertEqual(run("compare", f"{orig}\n{SEP}\n{same}")["register_mixed"], [])

    def test_compare_without_separator_fails(self):
        r = subprocess.run([sys.executable, "scripts/human_check.py", "compare"],
                           input="원문만", capture_output=True, text=True)
        self.assertEqual(r.returncode, 2)


if __name__ == "__main__":
    unittest.main()
