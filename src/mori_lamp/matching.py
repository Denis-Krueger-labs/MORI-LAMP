from typing import Any

from mori_lamp.models import (
    Claim,
    Job,
    Profile,
    Requirement,
)


CEFR_RANK = {
    "A1": 1,
    "A2": 2,
    "B1": 3,
    "B2": 4,
    "C1": 5,
    "C2": 6,
}


def build_assessment(
    requirement: Requirement,
) -> dict[str, Any]:
    assessment: dict[str, Any] = {
        "name": requirement.name,
        "category": requirement.category,
        "priority": requirement.priority,
    }

    if requirement.description is not None:
        assessment["description"] = (
            requirement.description
        )

    if requirement.source_text is not None:
        assessment["source_text"] = (
            requirement.source_text
        )

    if requirement.evidence_hints:
        assessment["evidence_hints"] = (
            requirement.evidence_hints
        )

    if requirement.minimum_level is not None:
        assessment["minimum_level"] = (
            requirement.minimum_level
        )

    return assessment


def claim_meets_required_level(
    requirement: Requirement,
    claim: Claim,
) -> bool:
    if requirement.category != "language":
        return True

    if requirement.minimum_level is None:
        return True

    if claim.level is None:
        return False

    required_rank = CEFR_RANK.get(
        requirement.minimum_level.upper()
    )
    claim_rank = CEFR_RANK.get(
        claim.level.upper()
    )

    if required_rank is None or claim_rank is None:
        return False

    return claim_rank >= required_rank


def match_requirements(
    job: Job,
    profile: Profile,
) -> dict[str, Any]:
    claims_by_key = {
        (
            claim.category,
            claim.name,
        ): claim
        for claim in profile.claims
    }

    result: dict[str, Any] = {
        "job": {
            "title": job.title,
            "company": job.company,
        },
        "verified_matches": [],
        "needs_evidence": [],
        "unmet_requirements": [],
        "unknown_requirements": [],
    }

    for requirement in job.requirements:
        claim = claims_by_key.get(
            (
                requirement.category,
                requirement.name,
            )
        )

        assessment = build_assessment(requirement)

        if claim is None:
            result["unknown_requirements"].append(
                assessment
            )
            continue

        if claim.status == "self_reported":
            assessment["status"] = claim.status

            if claim.level is not None:
                assessment["claim_level"] = claim.level

            result["needs_evidence"].append(
                assessment
            )
            continue

        assessment["evidence"] = claim.evidence

        if claim.level is not None:
            assessment["claim_level"] = claim.level

        if not claim_meets_required_level(
            requirement,
            claim,
        ):
            assessment["reason"] = (
                f"claim level {claim.level} does not "
                "meet minimum "
                f"{requirement.minimum_level}"
            )
            result["unmet_requirements"].append(
                assessment
            )
            continue

        result["verified_matches"].append(
            assessment
        )

    return result