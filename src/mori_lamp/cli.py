import argparse
import json
from pathlib import Path
import sys
from typing import TypeVar

from pydantic import BaseModel, ValidationError

from mori_lamp.matching import match_requirements
from mori_lamp.models import Job, Profile


ModelType = TypeVar(
    "ModelType",
    bound=BaseModel,
)


def load_model(
    path: Path,
    model_type: type[ModelType],
) -> ModelType:
    return model_type.model_validate_json(
        path.read_text(encoding="utf-8")
    )


def format_validation_error(
    error: ValidationError,
) -> str:
    messages = []

    for issue in error.errors():
        location = ".".join(
            str(part)
            for part in issue["loc"]
        )
        location = location or "document"

        messages.append(
            f"{location}: {issue['msg']}"
        )

    return "; ".join(messages)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="mori-lamp",
        description=(
            "Evidence-grounded internship "
            "analysis pipeline."
        ),
    )

    subcommands = parser.add_subparsers(
        dest="command",
        required=True,
    )

    match_command = subcommands.add_parser(
        "match",
        help=(
            "Match a normalized job listing "
            "against a candidate profile."
        ),
    )
    match_command.add_argument(
        "job",
        type=Path,
        help="Path to a normalized job JSON file.",
    )
    match_command.add_argument(
        "profile",
        type=Path,
        help="Path to a candidate profile JSON file.",
    )

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    try:
        job = load_model(args.job, Job)
        profile = load_model(args.profile, Profile)
        result = match_requirements(job, profile)
    except OSError as error:
        print(
            f"mori-lamp: error: {error}",
            file=sys.stderr,
        )
        return 2
    except ValidationError as error:
        print(
            "mori-lamp: error: "
            f"{format_validation_error(error)}",
            file=sys.stderr,
        )
        return 2

    print(
        json.dumps(
            result,
            indent=2,
            ensure_ascii=False,
        )
    )

    return 0