import sys
import unittest

sys.path.insert(0, "scripts")
sys.path.insert(0, "evals")
from judge import combine, majority, parse_verdict  # noqa: E402


class JudgeTest(unittest.TestCase):
    def test_parse_verdict(self):
        self.assertEqual(parse_verdict("이유...\nVERDICT: SECOND"), "SECOND")
        self.assertEqual(parse_verdict("모르겠다"), "TIE")

    def test_combine_consistent(self):
        self.assertEqual(combine("SECOND", "FIRST"), "skill")
        self.assertEqual(combine("FIRST", "SECOND"), "baseline")

    def test_combine_position_bias_is_tie(self):
        self.assertEqual(combine("FIRST", "FIRST"), "tie")

    def test_majority(self):
        self.assertEqual(majority(["skill", "skill", "tie"]), "skill")
        self.assertEqual(majority(["skill", "baseline"]), "tie")
        self.assertEqual(majority(["tie"]), "tie")
        self.assertEqual(majority(["skill", "baseline", "tie"]), "tie")


if __name__ == "__main__":
    unittest.main()
