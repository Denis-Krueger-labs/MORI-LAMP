import json
from pathlib import Path
import unittest

from mori_lamp.matching import match_requirements


ROOT = Path(__file__).resolve().parents[1]


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


class MatchingTests(unittest.TestCase):
    def setUp(self) -> None:
        self.job = load_json(
            ROOT / "examples" / "job.normalized.json"
        )
        self.valid_profile = load_json(
            ROOT / "examples" / "profile.sample.json"
        )

    def test_requirements_are_classified(self) -> None:
        result = match_requirements(
            self.job,
            self.valid_profile,
        )

        self.assertEqual(
            [
                item["name"]
                for item in result["verified_matches"]
            ],
            ["python", "linux"],
        )
        self.assertEqual(
            [
                item["name"]
                for item in result["needs_evidence"]
            ],
            ["burp suite"],
        )
        self.assertEqual(
            [
                item["name"]
                for item in result["unknown_requirements"]
            ],
            ["active directory"],
        )

    def test_verified_skill_without_evidence_is_rejected(
        self,
    ) -> None:
        invalid_profile = load_json(
            ROOT
            / "tests"
            / "fixtures"
            / "profile.invalid.json"
        )

        with self.assertRaisesRegex(
            ValueError,
            "verified skill 'python' requires evidence",
        ):
            match_requirements(
                self.job,
                invalid_profile,
            )


if __name__ == "__main__":
    unittest.main()