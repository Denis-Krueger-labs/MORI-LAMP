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
                for item in result[
                    "unknown_requirements"
                ]
            ],
            ["active directory"],
        )

    def test_self_reported_claim_is_not_promoted(
        self,
    ) -> None:
        job = Job.model_validate(
            {
                "source": "manual",
                "title": "Test Internship",
                "company": "Test Company",
                "requirements": [
                    {
                        "name": "python",
                        "category": "technical_skill",
                        "priority": "required",
                    }
                ],
            }
        )
        profile = Profile.model_validate(
            {
                "claims": [
                    {
                        "name": "python",
                        "category": "technical_skill",
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

    def test_same_name_in_wrong_category_does_not_match(
        self,
    ) -> None:
        job = Job.model_validate(
            {
                "source": "manual",
                "title": "Test Internship",
                "company": "Test Company",
                "requirements": [
                    {
                        "name": "german",
                        "category": "language",
                        "priority": "required",
                        "minimum_level": "C1",
                    }
                ],
            }
        )
        profile = Profile.model_validate(
            {
                "claims": [
                    {
                        "name": "german",
                        "category": "technical_skill",
                        "status": "verified",
                        "evidence": [
                            "unrelated technical project"
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
            [
                item["name"]
                for item in result[
                    "unknown_requirements"
                ]
            ],
            ["german"],
        )


if __name__ == "__main__":
    unittest.main()