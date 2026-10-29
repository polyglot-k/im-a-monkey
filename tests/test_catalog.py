import re
import sys
import unittest

sys.path.insert(0, "scripts")
from textutil import catalog_ids  # noqa: E402

EXPECTED = (
    [f"S0{i}" for i in range(1, 10)]
    + [f"W0{i}" for i in range(1, 9)]
    + [f"T0{i}" for i in range(1, 6)]
    + [f"V0{i}" for i in range(1, 9)]
    + ["M01", "M02"]
    + [f"A{i:02d}" for i in range(1, 17)]
    + ["L01"]
)


class CatalogTest(unittest.TestCase):
    def test_all_ids_present(self):
        self.assertFalse(set(EXPECTED) - catalog_ids("catalog/antipatterns.md"))

    def test_no_duplicate_ids_and_four_bullets(self):
        with open("catalog/antipatterns.md", encoding="utf-8") as f:
            text = f.read()
        ids = re.findall(r"^### ([A-Z]\d{2}) ", text, re.M)
        self.assertEqual(len(ids), len(set(ids)), "중복 ID")
        for part in re.split(r"^### ", text, flags=re.M)[1:]:
            head, body = part.split("\n", 1)
            for label in ("심각도", "왜", "나쁜 예 → 고친 예", "잡는 곳"):
                self.assertRegex(body, rf"(?m)^- {label}:", f"{head}: '{label}' 항목이 없다")


if __name__ == "__main__":
    unittest.main()
