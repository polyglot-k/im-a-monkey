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


if __name__ == "__main__":
    unittest.main()
