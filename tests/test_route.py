import sys
import unittest

sys.path.insert(0, "evals")
from route import parse_skill  # noqa: E402


class RouteTest(unittest.TestCase):
    def test_parse_skill_takes_last_line(self):
        self.assertEqual(parse_skill("monkey-doc 도 후보였지만\n\nmonkey-clear\n"), "monkey-clear")
        self.assertEqual(parse_skill("모르겠어요"), "")


if __name__ == "__main__":
    unittest.main()
