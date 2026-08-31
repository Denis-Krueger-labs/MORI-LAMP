from pathlib import Path
import unittest

from pydantic import ValidationError

from mori_lamp.models import Job, Profile, Requirement


ROOT = Path(__file__).resolve().parents[1]


class ModelTests(unittest.TestCase):
    def test_example_documents_are_valid(self) -> None:
        job = Job.model_validate_json(
            (
                ROOT / "examples" / "job.normalized.json"
            ).read_text(encoding="utf-8")
        )
        profile = Profile.model_validate_json(
            (
                ROOT / "examples" / "profile.sample.json"
            ).read_text(encoding="utf-8")
        )

        self.assertEqual(job.title, "Cybersecurity Intern")
        self.assertEqual(profile.skills[0].name, "python")

    def test_verified_skill_without_evidence_is_rejected(
        self,
    ) -> None:
        invalid_json = (
            ROOT
            / "tests"
            / "fixtures"
            / "profile.invalid.json"
        ).read_text(encoding="utf-8")

        with self.assertRaisesRegex(
            ValidationError,
            "verified skill 'python' requires evidence",
        ):
            Profile.model_validate_json(invalid_json)

    def test_unexpected_fields_are_rejected(self) -> None:
        with self.assertRaises(ValidationError) as caught:
            Requirement.model_validate(
                {
                    "name": "python",
                    "priority": "required",
                    "totally_trustworthy_ai_guess": True,
                }
            )

        self.assertEqual(
            caught.exception.errors()[0]["type"],
            "extra_forbidden",
        )


if __name__ == "__main__":
    unittest.main()