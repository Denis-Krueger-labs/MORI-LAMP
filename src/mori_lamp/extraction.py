from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any, Protocol

from mori_lamp.grounding import (
    validate_job_grounding,
)
from mori_lamp.models import Job


@dataclass(
    frozen=True,
    slots=True,
)
class ExtractionRequest:
    source: str
    raw_text: str

    def __post_init__(self) -> None:
        if (
            not isinstance(self.source, str)
            or not self.source.strip()
        ):
            raise ValueError(
                "extraction source must not be empty"
            )

        if (
            not isinstance(self.raw_text, str)
            or not self.raw_text.strip()
        ):
            raise ValueError(
                "raw listing text must not be empty"
            )


class ListingExtractor(Protocol):
    def extract(
        self,
        request: ExtractionRequest,
    ) -> Mapping[str, Any]:
        """Return an untrusted candidate job mapping."""


def extract_job(
    request: ExtractionRequest,
    extractor: ListingExtractor,
) -> Job:
    candidate_output = extractor.extract(
        request
    )

    if not isinstance(
        candidate_output,
        Mapping,
    ):
        raise TypeError(
            "extractor must return a mapping"
        )

    candidate = dict(candidate_output)

    extracted_source = candidate.get("source")

    if (
        extracted_source is not None
        and extracted_source != request.source
    ):
        raise ValueError(
            "extractor source does not match "
            "request source"
        )

    # Source identity belongs to the caller rather
    # than the untrusted extraction provider.
    candidate["source"] = request.source

    job = Job.model_validate(candidate)

    validate_job_grounding(
        request.raw_text,
        job,
    )

    return job