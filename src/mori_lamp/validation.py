from typing import Any


def validate_profile(
    profile: dict[str, Any],
) -> None:
    for skill in profile["skills"]:
        status = skill.get("status")
        evidence = skill.get("evidence")

        if status == "verified" and not evidence:
            name = skill.get("name", "<unnamed>")

            raise ValueError(
                f"verified skill '{name}' requires evidence"
            )