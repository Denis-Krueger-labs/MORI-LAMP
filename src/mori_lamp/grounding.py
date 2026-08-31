from mori_lamp.models import Job


def normalize_source_text(text: str) -> str:
    return " ".join(
        text.casefold().split()
    )


def validate_job_grounding(
    raw_text: str,
    job: Job,
) -> None:
    normalized_raw = normalize_source_text(raw_text)

    extracted_sources: list[
        tuple[str, str, str]
    ] = []

    for responsibility in job.responsibilities:
        extracted_sources.append(
            (
                "responsibility",
                responsibility.name,
                responsibility.source_text,
            )
        )

    for requirement in job.requirements:
        if requirement.source_text is not None:
            extracted_sources.append(
                (
                    "requirement",
                    requirement.name,
                    requirement.source_text,
                )
            )

    for rule in job.application_rules:
        extracted_sources.append(
            (
                "application rule",
                rule.name,
                rule.source_text,
            )
        )

    ungrounded = []

    for kind, name, source_text in extracted_sources:
        normalized_source = normalize_source_text(
            source_text
        )

        if normalized_source not in normalized_raw:
            ungrounded.append(
                f"{kind} '{name}'"
            )

    if ungrounded:
        fields = ", ".join(ungrounded)

        raise ValueError(
            "job contains ungrounded source text: "
            f"{fields}"
        )