from typing import Annotated, Literal, Self

from pydantic import (
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


class Skill(StrictModel):
    name: NonEmptyText
    status: Literal["verified", "self_reported"]
    evidence: list[NonEmptyText] = Field(
        default_factory=list
    )

    @model_validator(mode="after")
    def verified_skill_requires_evidence(
        self,
    ) -> Self:
        if self.status == "verified" and not self.evidence:
            raise ValueError(
                f"verified skill '{self.name}' "
                "requires evidence"
            )

        return self


class Profile(StrictModel):
    skills: list[Skill]