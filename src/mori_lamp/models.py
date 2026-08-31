from typing import Annotated, Literal, Self

from pydantic import (
    AliasChoices,
    BaseModel,
    ConfigDict,
    Field,
    StringConstraints,
    model_validator,
)


NonEmptyText = Annotated[
    str,
    StringConstraints(strip_whitespace=True, min_length=1),
]

RequirementCategory = Literal[
    "technical_skill",
    "experience",
    "language",
    "behavioral",
    "credential",
    "eligibility",
    "values",
]

RequirementPriority = Literal[
    "required",
    "preferred",
    "conditional",
]

ClaimStatus = Literal[
    "verified",
    "self_reported",
]


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class Requirement(StrictModel):
    name: NonEmptyText
    category: RequirementCategory = "technical_skill"
    priority: RequirementPriority
    description: NonEmptyText | None = None
    source_text: NonEmptyText | None = None
    evidence_hints: list[NonEmptyText] = Field(
        default_factory=list
    )
    minimum_level: NonEmptyText | None = None


class Responsibility(StrictModel):
    name: NonEmptyText
    source_text: NonEmptyText


class ApplicationRule(StrictModel):
    name: NonEmptyText
    description: NonEmptyText
    source_text: NonEmptyText


class Job(StrictModel):
    source: NonEmptyText
    title: NonEmptyText
    company: NonEmptyText
    location: NonEmptyText | None = None
    employment_type: NonEmptyText | None = None
    responsibilities: list[Responsibility] = Field(
        default_factory=list
    )
    requirements: list[Requirement]
    application_rules: list[ApplicationRule] = Field(
        default_factory=list
    )

    @model_validator(mode="after")
    def automated_requirements_need_provenance(
        self,
    ) -> Self:
        if self.source == "manual":
            return self

        missing_provenance = [
            requirement.name
            for requirement in self.requirements
            if requirement.description is None
            or requirement.source_text is None
        ]

        if missing_provenance:
            names = ", ".join(missing_provenance)

            raise ValueError(
                "non-manual requirements require "
                f"description and source_text: {names}"
            )

        return self


class Claim(StrictModel):
    name: NonEmptyText
    category: RequirementCategory = "technical_skill"
    status: ClaimStatus
    evidence: list[NonEmptyText] = Field(
        default_factory=list
    )
    level: NonEmptyText | None = None

    @model_validator(mode="after")
    def validate_claim(self) -> Self:
        if self.status == "verified" and not self.evidence:
            raise ValueError(
                f"verified claim '{self.name}' "
                "requires evidence"
            )

        if self.category == "language" and self.level is None:
            raise ValueError(
                f"language claim '{self.name}' "
                "requires a level"
            )

        return self


class Profile(StrictModel):
    claims: list[Claim] = Field(
        validation_alias=AliasChoices(
            "claims",
            "skills",
        )
    )

    @model_validator(mode="after")
    def claim_keys_must_be_unique(self) -> Self:
        seen: set[tuple[str, str]] = set()

        for claim in self.claims:
            key = (
                claim.category,
                claim.name,
            )

            if key in seen:
                raise ValueError(
                    "duplicate candidate claim: "
                    f"{claim.category}/{claim.name}"
                )

            seen.add(key)

        return self

    @property
    def skills(self) -> list[Claim]:
        """Temporary compatibility alias."""

        return self.claims