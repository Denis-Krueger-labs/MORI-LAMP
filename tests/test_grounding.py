from pathlib import Path
import unittest

from mori_lamp.grounding import (
    validate_job_grounding,
)
from mori_lamp.models import Job


ROOT = Path(__file__).resolve().parents[1]


class GroundingTests(unittest.TestCase):
    def setUp(self) -> None:
        fixture_directory = (
            ROOT
            / "tests"
            / "fixtures"
            / "listings"
        )

        self.raw_text = (
            fixture_directory / "prosec.sample.txt"
        ).read_text(encoding="utf-8")

        self.job = Job.model_validate_json(
            (
                fixture_directory
                / "prosec.expected.json"
            ).read_text(encoding="utf-8")
        )

    def test_expected_job_is_grounded(
        self,
    ) -> None:
        validate_job_grounding(
            self.raw_text,
            self.job,
        )

    def test_fabricated_source_text_is_rejected(
        self,
    ) -> None:
        requirements = list(self.job.requirements)

        requirements[0] = requirements[0].model_copy(
            update={
                "source_text": (
                    "Candidate must own a cybersecurity "
                    "spaceship."
                )
            }
        )

        fabricated_job = self.job.model_copy(
            update={
                "requirements": requirements,
            }
        )

        with self.assertRaisesRegex(
            ValueError,
            "alignment with company mission",
        ):
            validate_job_grounding(
                self.raw_text,
                fabricated_job,
            )


if __name__ == "__main__":
    unittest.main()