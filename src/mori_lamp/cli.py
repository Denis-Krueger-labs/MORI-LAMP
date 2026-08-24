import argparse
import json
from pathlib import Path
import sys
from typing import Any

from mori_lamp.matching import match_requirements


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(
        path.read_text(encoding="utf-8")
    )


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
        job = load_json(args.job)
        profile = load_json(args.profile)
        result = match_requirements(job, profile)
    except (OSError, ValueError) as error:
        print(
            f"mori-lamp: error: {error}",
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