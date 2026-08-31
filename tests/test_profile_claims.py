import unittest

from mori_lamp.models import Profile


class ProfileClaimTests(unittest.TestCase):
    def test_profile_supports_multiple_claim_categories(
        self,
    ) -> None:
        profile = Profile.model_validate(
            {
                "claims": [
                    {
                        "name": "python",
                        "category": "technical_skill",
                        "status": "verified",
                        "evidence": [
                            "documented Python project"
                        ],
                    },
                    {
                        "name": "german",
                        "category": "language",
                        "status": "verified",
                        "level": "C1",
                        "evidence": [
                            "official language evidence"
                        ],
                    },
                    {
                        "name": (
                            "practical penetration-testing "
                            "or red-team experience"
                        ),
                        "category": "experience",
                        "status": "verified",
                        "evidence": [
                            "documented security lab"
                        ],
                    },
                    {
                        "name": "security-review eligibility",
                        "category": "eligibility",
                        "status": "self_reported",
                        "evidence": [],
                    },
                ]
            }
        )

        self.assertEqual(
            len(profile.claims),
            4,
        )
        self.assertEqual(
            profile.claims[1].category,
            "language",
        )
        self.assertEqual(
            profile.claims[1].level,
            "C1",
        )


if __name__ == "__main__":
    unittest.main()