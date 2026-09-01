from pathlib import Path
import unittest

from mori_lamp.evaluation import evaluate_extraction
from mori_lamp.models import Job


ROOT = Path(__file__).resolve().parents[1]


class ExtractionEvaluationTests(unittest.TestCase):
    def setUp(self) -> None:
        fixture_path = (
            ROOT
            / "tests"
            / "fixtures"
            / "listings"
            / "prosec.expected.json"
        )

        self.expected = Job.model_validate_json(
            fixture_path.read_text(encoding="utf-8")
        )

    def test_identical_job_receives_perfect_score(
        self,
    ) -> None:
        evaluation = evaluate_extraction(
            expected=self.expected,
            actual=self.expected,
        )

        self.assertTrue(evaluation.perfect)
        self.assertEqual(evaluation.precision, 1.0)
        self.assertEqual(evaluation.recall, 1.0)
        self.assertEqual(evaluation.f1, 1.0)
        self.assertEqual(evaluation.missing_facts, ())
        self.assertEqual(evaluation.unexpected_facts, ())

    def test_missing_requirement_reduces_recall(
        self,
    ) -> None:
        actual_data = self.expected.model_dump(
            mode="json"
        )
        actual_data["requirements"] = [
            requirement
            for requirement in actual_data["requirements"]
            if requirement["name"]
            != (
                "practical penetration-testing "
                "or red-team experience"
            )
        ]

        actual = Job.model_validate(actual_data)

        evaluation = evaluate_extraction(
            expected=self.expected,
            actual=actual,
        )

        self.assertFalse(evaluation.perfect)
        self.assertLess(evaluation.recall, 1.0)
        self.assertTrue(
            any(
                (
                    "practical penetration-testing "
                    "or red-team experience"
                )
                in fact
                for fact in evaluation.missing_facts
            )
        )

    def test_fabricated_requirement_reduces_precision(
        self,
    ) -> None:
        actual_data = self.expected.model_dump(
            mode="json"
        )
        actual_data["requirements"].append(
            {
                "name": "cybersecurity spaceship piloting",
                "category": "technical_skill",
                "priority": "required",
                "description": (
                    "Experience piloting a cybersecurity "
                    "spaceship."
                ),
                "source_text": (
                    "Pilot the company cybersecurity "
                    "spaceship."
                ),
            }
        )

        actual = Job.model_validate(actual_data)

        evaluation = evaluate_extraction(
            expected=self.expected,
            actual=actual,
        )

        self.assertFalse(evaluation.perfect)
        self.assertLess(evaluation.precision, 1.0)
        self.assertTrue(
            any(
                "cybersecurity spaceship piloting"
                in fact
                for fact in evaluation.unexpected_facts
            )
        )

    def test_whitespace_and_list_order_do_not_affect_score(
        self,
    ) -> None:
        actual_data = self.expected.model_dump(
            mode="json"
        )
        actual_data["title"] = (
            "Junior   Pentester / Red Teamer (m/w/d)"
        )

        for requirement in actual_data["requirements"]:
            requirement["evidence_hints"].reverse()

        actual = Job.model_validate(actual_data)

        evaluation = evaluate_extraction(
            expected=self.expected,
            actual=actual,
        )

        self.assertTrue(evaluation.perfect)

    def test_caller_owned_source_is_not_scored(
        self,
    ) -> None:
        actual_data = self.expected.model_dump(
            mode="json"
        )
        actual_data["source"] = (
            "https://caller.example/different-source"
        )

        actual = Job.model_validate(actual_data)

        evaluation = evaluate_extraction(
            expected=self.expected,
            actual=actual,
        )

        self.assertTrue(evaluation.perfect)


if __name__ == "__main__":
    unittest.main()