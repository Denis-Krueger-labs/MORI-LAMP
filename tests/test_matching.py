from pathlib import Path
import unittest

from mori_lamp.matching import match_requirements
from mori_lamp.models import Job, Profile


ROOT = Path(__file__).resolve().parents[1]


class MatchingTests(unittest.TestCase):
    def setUp(self) -> None:
        self.job = Job.model_validate_json(
            (
                ROOT / "examples" / "job.normalized.json"
            ).read_text(encoding="utf-8")
        )
        self.profile = Profile.model_validate_json(
            (
                ROOT / "examples" / "profile.sample.json"
            ).read_text(encoding="utf-8")
        )

    def test_requirements_are_classified(self) -> None:
        result = match_requirements(
            self.job,
            self.profile,
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

    def test_self_reported_skill_is_not_promoted(
        self,
    ) -> None:
        job = Job.model_validate(
            {
                "source": "test",
                "title": "Test Internship",
                "company": "Test Company",
                "requirements": [
                    {
                        "name": "python",
                        "priority": "required",
                    }
                ],
            }
        )
        profile = Profile.model_validate(
            {
                "skills": [
                    {
                        "name": "python",
                        "status": "self_reported",
                        "evidence": [
                            "unverified personal claim"
                        ],
                    }
                ]
            }
        )

        result = match_requirements(job, profile)

        self.assertEqual(
            result["verified_matches"],
            [],
        )
        self.assertEqual(
            result["needs_evidence"][0]["name"],
            "python",
        )


if __name__ == "__main__":
    unittest.main()