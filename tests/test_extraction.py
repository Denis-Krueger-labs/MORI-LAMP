import json
from collections.abc import Mapping
from pathlib import Path
from typing import Any
import unittest

from pydantic import ValidationError

from mori_lamp.extraction import (
    ExtractionRequest,
    ListingExtractor,
    extract_job,
)
from mori_lamp.models import Job


ROOT = Path(__file__).resolve().parents[1]


class FixtureExtractor:
    def __init__(
        self,
        candidate: dict[str, Any],
    ) -> None:
        self.candidate = candidate
        self.requests: list[ExtractionRequest] = []

    def extract(
        self,
        request: ExtractionRequest,
    ) -> Mapping[str, Any]:
        self.requests.append(request)

        return self.candidate


class ExtractionTests(unittest.TestCase):
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

        self.candidate = json.loads(
            (
                fixture_directory
                / "prosec.expected.json"
            ).read_text(encoding="utf-8")
        )

        source = self.candidate.pop("source")

        self.request = ExtractionRequest(
            source=source,
            raw_text=self.raw_text,
        )

    def test_candidate_is_validated_and_grounded(
        self,
    ) -> None:
        fixture_extractor = FixtureExtractor(
            self.candidate
        )
        extractor: ListingExtractor = (
            fixture_extractor
        )

        job = extract_job(
            self.request,
            extractor,
        )

        self.assertIsInstance(job, Job)
        self.assertEqual(
            job.source,
            self.request.source,
        )
        self.assertEqual(
            job.title,
            "Junior Pentester / Red Teamer (m/w/d)",
        )
        self.assertEqual(
            fixture_extractor.requests,
            [self.request],
        )

    def test_invalid_candidate_schema_is_rejected(
        self,
    ) -> None:
        self.candidate["unexpected_field"] = (
            "must not survive validation"
        )

        extractor = FixtureExtractor(
            self.candidate
        )

        with self.assertRaises(ValidationError):
            extract_job(
                self.request,
                extractor,
            )

    def test_ungrounded_candidate_is_rejected(
        self,
    ) -> None:
        self.candidate["requirements"][0][
            "source_text"
        ] = (
            "Candidate must own a cybersecurity "
            "spaceship."
        )

        extractor = FixtureExtractor(
            self.candidate
        )

        with self.assertRaisesRegex(
            ValueError,
            "ungrounded source text",
        ):
            extract_job(
                self.request,
                extractor,
            )

    def test_conflicting_source_is_rejected(
        self,
    ) -> None:
        self.candidate["source"] = (
            "https://example.invalid/fabricated"
        )

        extractor = FixtureExtractor(
            self.candidate
        )

        with self.assertRaisesRegex(
            ValueError,
            "extractor source does not match "
            "request source",
        ):
            extract_job(
                self.request,
                extractor,
            )


if __name__ == "__main__":
    unittest.main()