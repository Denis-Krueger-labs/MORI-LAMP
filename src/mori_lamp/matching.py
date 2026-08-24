from typing import Any

from mori_lamp.validation import validate_profile


def match_requirements(
    job: dict[str, Any],
    profile: dict[str, Any],
) -> dict[str, Any]:
    validate_profile(profile)

    skills_by_name = {
        skill["name"]: skill
        for skill in profile["skills"]
    }

    result = {
        "job": {
            "title": job["title"],
            "company": job["company"],
        },
        "verified_matches": [],
        "needs_evidence": [],
        "unknown_requirements": [],
    }

    for requirement in job["requirements"]:
        skill = skills_by_name.get(requirement["name"])

        assessment = {
            "name": requirement["name"],
            "priority": requirement["priority"],
        }

        if skill is None:
            result["unknown_requirements"].append(
                assessment
            )
        elif skill["status"] == "verified":
            assessment["evidence"] = skill["evidence"]
            result["verified_matches"].append(
                assessment
            )
        else:
            assessment["status"] = skill["status"]
            result["needs_evidence"].append(
                assessment
            )

    return result