import json
from collections import Counter
from dataclasses import dataclass
from typing import Any

from mori_lamp.models import Job


Fact = tuple[str, str]
FactCounter = Counter[Fact]


@dataclass(
    frozen=True,
    slots=True,
)
class ExtractionEvaluation:
    matched_facts: int
    expected_facts: int
    actual_facts: int
    precision: float
    recall: float
    f1: float
    missing_facts: tuple[str, ...]
    unexpected_facts: tuple[str, ...]

    @property
    def perfect(self) -> bool:
        return (
            not self.missing_facts
            and not self.unexpected_facts
        )


def normalize_value(value: Any) -> str:
    if isinstance(value, str):
        return " ".join(value.split())

    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )


def add_fact(
    facts: FactCounter,
    path: str,
    value: Any,
) -> None:
    facts[
        (
            path,
            normalize_value(value),
        )
    ] += 1


def job_facts(job: Job) -> FactCounter:
    facts: FactCounter = Counter()

    # The source belongs to the caller and is
    # intentionally excluded from extraction scoring.
    for field_name in (
        "title",
        "company",
        "location",
        "employment_type",
    ):
        value = getattr(job, field_name)

        if value is not None:
            add_fact(
                facts,
                f"job/{field_name}",
                value,
            )

    for responsibility in job.responsibilities:
        base_path = (
            "responsibilities/"
            f"{normalize_value(responsibility.name)}"
        )

        add_fact(
            facts,
            f"{base_path}/present",
            True,
        )
        add_fact(
            facts,
            f"{base_path}/source_text",
            responsibility.source_text,
        )

    for requirement in job.requirements:
        base_path = (
            "requirements/"
            f"{normalize_value(requirement.category)}/"
            f"{normalize_value(requirement.name)}"
        )

        add_fact(
            facts,
            f"{base_path}/present",
            True,
        )
        add_fact(
            facts,
            f"{base_path}/priority",
            requirement.priority,
        )

        if requirement.description is not None:
            add_fact(
                facts,
                f"{base_path}/description",
                requirement.description,
            )

        if requirement.source_text is not None:
            add_fact(
                facts,
                f"{base_path}/source_text",
                requirement.source_text,
            )

        if requirement.minimum_level is not None:
            add_fact(
                facts,
                f"{base_path}/minimum_level",
                requirement.minimum_level,
            )

        for evidence_hint in requirement.evidence_hints:
            add_fact(
                facts,
                f"{base_path}/evidence_hints",
                evidence_hint,
            )

    for rule in job.application_rules:
        base_path = (
            "application_rules/"
            f"{normalize_value(rule.name)}"
        )

        add_fact(
            facts,
            f"{base_path}/present",
            True,
        )
        add_fact(
            facts,
            f"{base_path}/description",
            rule.description,
        )
        add_fact(
            facts,
            f"{base_path}/source_text",
            rule.source_text,
        )

    return facts


def format_facts(
    facts: FactCounter,
) -> tuple[str, ...]:
    formatted = [
        f"{path} = {value}"
        for (path, value), count in facts.items()
        for _ in range(count)
    ]

    return tuple(sorted(formatted))


def evaluate_extraction(
    expected: Job,
    actual: Job,
) -> ExtractionEvaluation:
    expected_fact_set = job_facts(expected)
    actual_fact_set = job_facts(actual)

    matched = expected_fact_set & actual_fact_set
    missing = expected_fact_set - actual_fact_set
    unexpected = actual_fact_set - expected_fact_set

    matched_count = sum(matched.values())
    expected_count = sum(expected_fact_set.values())
    actual_count = sum(actual_fact_set.values())

    if actual_count == 0:
        precision = (
            1.0
            if expected_count == 0
            else 0.0
        )
    else:
        precision = matched_count / actual_count

    if expected_count == 0:
        recall = 1.0
    else:
        recall = matched_count / expected_count

    if precision + recall == 0:
        f1 = 0.0
    else:
        f1 = (
            2
            * precision
            * recall
            / (precision + recall)
        )

    return ExtractionEvaluation(
        matched_facts=matched_count,
        expected_facts=expected_count,
        actual_facts=actual_count,
        precision=precision,
        recall=recall,
        f1=f1,
        missing_facts=format_facts(missing),
        unexpected_facts=format_facts(unexpected),
    )