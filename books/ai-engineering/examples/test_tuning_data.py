from copy import deepcopy
from pathlib import Path
import unittest

from tuning_data import load_rows, validate_samples


class TuningDataTests(unittest.TestCase):
    def setUp(self):
        self.rows = load_rows(Path(__file__).parent / "fixtures/tuning-samples.jsonl")

    def test_fixture(self):
        result = validate_samples(self.rows)
        self.assertEqual(result["splits"], {"train": 4, "dev": 2, "test": 3})

    def test_family_leak(self):
        self.rows[1]["split"] = "dev"
        with self.assertRaisesRegex(ValueError, "family_leak"):
            validate_samples(self.rows)

    def test_renamed_source_and_whitespace_still_leak(self):
        duplicate = deepcopy(self.rows[0])
        duplicate.update(id="X", family="different", split="test")
        duplicate["question"] = "  " + duplicate["question"] + "\n"
        duplicate["evidence"] = {"renamed": self.rows[0]["evidence"]["s1"]}
        duplicate["target"]["citations"][0]["source_id"] = "renamed"
        with self.assertRaisesRegex(ValueError, "input_leak"):
            validate_samples(self.rows + [duplicate])

    def test_unknown_quote(self):
        self.rows[0]["target"]["citations"][0]["quote"] = "승인 없이 신청한다."
        with self.assertRaisesRegex(ValueError, "quote_not_found"):
            validate_samples(self.rows)

    def test_missing_required_field(self):
        del self.rows[0]["target"]["clarification"]
        with self.assertRaises(ValueError):
            validate_samples(self.rows)

    def test_missing_split(self):
        with self.assertRaisesRegex(ValueError, "missing_split"):
            validate_samples([r for r in self.rows if r["split"] != "test"])

    def test_duplicate_id(self):
        with self.assertRaisesRegex(ValueError, "duplicate_id"):
            validate_samples(self.rows + [deepcopy(self.rows[0])])

    def test_semantic_error_is_not_detected(self):
        self.rows[0]["target"]["answer"] = "승인 없이 신청할 수 있다."
        # 인용 문자열 일치가 정답의 의미를 보증하지 않는 경계를 고정한다.
        self.assertEqual(validate_samples(self.rows)["samples"], 9)


if __name__ == "__main__":
    unittest.main()
