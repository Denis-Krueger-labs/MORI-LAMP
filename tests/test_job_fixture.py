from pathlib import Path
import unittest

from mori_lamp.models import Job


ROOT = Path(__file__).resolve().parents[1]


class JobFixtureTests(unittest.TestCase):
    def setUp(self) -> None:
        expected_path = (
            ROOT
            / "tests"
            / "fixtures"
            / "listings"
            / "prosec.expected.json"
        )

        self.job = Job.model_validate_json(
            expected_path.read_text(encoding="utf-8")
        )

    def test_expected_prosec_job_matches_schema(
        self,
    ) -> None:
        self.assertEqual(
            self.job.title,
            "Junior Pentester / Red Teamer (m/w/d)",
        )
        self.assertEqual(
            len(self.job.requirements),
            9,
        )
        self.assertEqual(
            len(self.job.responsibilities),
            5,
        )
        self.assertEqual(
            len(self.job.application_rules),
            2,
        )

    def test_learning_areas_are_not_requirements(
        self,
    ) -> None:
        requirement_names = {
            requirement.name
            for requirement in self.job.requirements
        }

        self.assertNotIn(
            "active directory",
            requirement_names,
        )
        self.assertIn(
            "Active Directory",
            self.job.responsibilities[2].source_text,
        )

    def test_requirement_semantics_are_preserved(
        self,
    ) -> None:
        requirements = {
            requirement.name: requirement
            for requirement in self.job.requirements
        }

        self.assertEqual(
            requirements[
                "security-review eligibility"
            ].priority,
            "conditional",
        )
        self.assertEqual(
            requirements["german"].minimum_level,
            "C1",
        )
        self.assertEqual(
            requirements["english"].minimum_level,
            "B2",
        )
        self.assertEqual(
            requirements[
                "offensive-security certification"
            ].priority,
            "preferred",
        )


if __name__ == "__main__":
    unittest.main()