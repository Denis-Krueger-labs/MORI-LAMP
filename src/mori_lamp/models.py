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


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class Requirement(StrictModel):
    name: NonEmptyText
    priority: Literal["required", "preferred"]


class Job(StrictModel):
    source: NonEmptyText
    title: NonEmptyText
    company: NonEmptyText
    requirements: list[Requirement]


class Skill(StrictModel):
    name: NonEmptyText
    status: Literal["verified", "self_reported"]
    evidence: list[NonEmptyText] = Field(default_factory=list)

    @model_validator(mode="after")
    def verified_skill_requires_evidence(self) -> Self:
        if self.status == "verified" and not self.evidence:
            raise ValueError(
                f"verified skill '{self.name}' requires evidence"
            )

        return self


class Profile(StrictModel):
    skills: list[Skill]