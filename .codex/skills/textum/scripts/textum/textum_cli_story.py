from __future__ import annotations

import argparse
from typing import Any

from .textum_cli_story_check import _cmd_story_check
from .textum_cli_story_pack import _cmd_story_pack


def register_story_commands(subparsers: Any) -> None:
    story_parser = subparsers.add_parser("story", help="Story execution pack commands")
    story_subparsers = story_parser.add_subparsers(dest="story_command", required=True)

    story_check = story_subparsers.add_parser("check", help="Validate a single docs/stories/story-###-*.json")
    story_check.add_argument("--workspace", default=".", help="Workspace root that contains ./docs.")
    story_check.add_argument("--n", type=int, required=True, help="Story number (e.g. 1).")
    story_check.add_argument("--max-lines", type=int, default=350, help="Max lines per story file (default: 350).")
    story_check.add_argument("--max-chars", type=int, default=12000, help="Max chars per story file (default: 12000).")
    story_check.set_defaults(func=_cmd_story_check)

    story_pack = story_subparsers.add_parser(
        "pack", help="Generate low-noise story exec pack under docs/story-exec/"
    )
    story_pack.add_argument("--workspace", default=".", help="Workspace root that contains ./docs.")
    story_pack.add_argument("--n", type=int, required=True, help="Story number (e.g. 1).")
    story_pack.add_argument(
        "--clean",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Delete existing docs/story-exec/story-###-*/ before writing (default: true).",
    )
    story_pack.add_argument("--max-lines", type=int, default=350, help="Max lines per file (default: 350).")
    story_pack.add_argument("--max-chars", type=int, default=12000, help="Max chars per file (default: 12000).")
    story_pack.set_defaults(func=_cmd_story_pack)

