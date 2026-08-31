import unittest

from mori_lamp.matching import match_requirements
from mori_lamp.models import Job, Profile


class LanguageLevelTests(unittest.TestCase):
    def test_lower_verified_level_is_unmet(
        self,
    ) -> None:
        job = Job.model_validate(
            {
                "source": "manual",
                "title": "Security Internship",
                "company": "Example Company",
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
                        "category": "language",
                        "status": "verified",
                        "level": "B1",
                        "evidence": [
                            "verified B1 language certificate"
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
            result["unmet_requirements"][0]["name"],
            "german",
        )
        self.assertEqual(
            result["unmet_requirements"][0]["reason"],
            "claim level B1 does not meet minimum C1",
        )


if __name__ == "__main__":
    unittest.main()