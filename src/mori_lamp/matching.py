from typing import Any

from mori_lamp.models import Job, Profile, Requirement


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
        elif claim.status == "verified":
            assessment["evidence"] = claim.evidence

            if claim.level is not None:
                assessment["claim_level"] = claim.level

            result["verified_matches"].append(
                assessment
            )
        else:
            assessment["status"] = claim.status

            if claim.level is not None:
                assessment["claim_level"] = claim.level

            result["needs_evidence"].append(
                assessment
            )

    return result