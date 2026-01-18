from __future__ import annotations

import argparse
from typing import Any

from .textum_cli_split_checks import _cmd_split_check1, _cmd_split_check2, _cmd_split_checkout
from .textum_cli_split_generate import _cmd_split_generate
from .textum_cli_split_plan import _cmd_split_plan_check, _cmd_split_plan_init


def register_split_commands(subparsers: Any) -> None:
    split_parser = subparsers.add_parser("split", help="Split plan/story generation commands")
    split_subparsers = split_parser.add_subparsers(dest="split_command", required=True)

    split_plan_parser = split_subparsers.add_parser("plan", help="Split planning pack commands")
    split_plan_sub = split_plan_parser.add_subparsers(dest="split_plan_command", required=True)

    split_plan_init = split_plan_sub.add_parser("init", help="Initialize docs/split-plan-pack.json from assets template")
    split_plan_init.add_argument("--workspace", default=".", help="Workspace root that contains ./docs.")
    split_plan_init.add_argument("--force", action="store_true", help="Overwrite existing docs/split-plan-pack.json")
    split_plan_init.set_defaults(func=_cmd_split_plan_init)

    split_plan_check = split_plan_sub.add_parser("check", help="Validate docs/split-plan-pack.json")
    split_plan_check.add_argument("--workspace", default=".", help="Workspace root that contains ./docs.")
    split_plan_check.add_argument(
        "--fix",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Auto-fix and write back (default: true).",
    )
    split_plan_check.add_argument(
        "--strict",
        action=argparse.BooleanOptionalAction,
        default=False,
        help="Treat warnings as FAIL (default: false).",
    )
    split_plan_check.set_defaults(func=_cmd_split_plan_check)

    split_generate = split_subparsers.add_parser("generate", help="Generate per-story JSON files under docs/stories/")
    split_generate.add_argument("--workspace", default=".", help="Workspace root that contains ./docs.")
    split_generate.add_argument(
        "--fix",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Auto-fix and write back split-plan-pack.json before generating (default: true).",
    )
    split_generate.add_argument(
        "--clean",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Delete docs/stories/story-*.json before writing (default: true).",
    )
    split_generate.set_defaults(func=_cmd_split_generate)

    split_check1 = split_subparsers.add_parser("check1", help="Core split check and index pack generation")
    split_check1.add_argument("--workspace", default=".", help="Workspace root that contains ./docs.")
    split_check1.add_argument("--max-lines", type=int, default=350, help="Max lines per story file (default: 350).")
    split_check1.add_argument("--max-chars", type=int, default=12000, help="Max chars per story file (default: 12000).")
    split_check1.add_argument(
        "--strict",
        action=argparse.BooleanOptionalAction,
        default=False,
        help="Treat threshold warnings as FAIL (default: false).",
    )
    split_check1.set_defaults(func=_cmd_split_check1)

    split_check2 = split_subparsers.add_parser("check2", help="Ref consistency checks (PRD/Scaffold)")
    split_check2.add_argument("--workspace", default=".", help="Workspace root that contains ./docs.")
    split_check2.add_argument(
        "--fix",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Auto-fix PRD/Scaffold packs before checking (default: true).",
    )
    split_check2.set_defaults(func=_cmd_split_check2)

    split_checkout = split_subparsers.add_parser(
        "checkout", help="Export story dependency graph (docs/story-mermaid.md)"
    )
    split_checkout.add_argument("--workspace", default=".", help="Workspace root that contains ./docs.")
    split_checkout.set_defaults(func=_cmd_split_checkout)

