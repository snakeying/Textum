from __future__ import annotations

import argparse
from typing import Any

from .textum_cli_prd_check import _cmd_prd_check
from .textum_cli_prd_init import _cmd_prd_init
from .textum_cli_prd_render import _cmd_prd_render
from .textum_cli_prd_slice import _cmd_prd_slice
from .textum_cli_prd_patch import register_prd_patch_command


def register_prd_commands(subparsers: Any) -> None:
    prd_parser = subparsers.add_parser("prd", help="PRD pack commands")
    prd_subparsers = prd_parser.add_subparsers(dest="prd_command", required=True)

    prd_init = prd_subparsers.add_parser("init", help="Initialize docs/prd-pack.json from assets template")
    prd_init.add_argument("--workspace", default=".", help="Workspace root that contains ./docs.")
    prd_init.add_argument("--force", action="store_true", help="Overwrite existing docs/prd-pack.json")
    prd_init.set_defaults(func=_cmd_prd_init)

    prd_check = prd_subparsers.add_parser("check", help="Validate docs/prd-pack.json")
    prd_check.add_argument("--workspace", default=".", help="Workspace root that contains ./docs.")
    prd_check.add_argument(
        "--fix",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Auto-fix and write back (default: true).",
    )
    prd_check.set_defaults(func=_cmd_prd_check)

    prd_render = prd_subparsers.add_parser("render", help="Render docs/PRD.md from docs/prd-pack.json")
    prd_render.add_argument("--workspace", default=".", help="Workspace root that contains ./docs.")
    prd_render.add_argument(
        "--fix",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Auto-fix and write back (default: true).",
    )
    prd_render.add_argument(
        "--lang",
        default="auto",
        choices=["auto", "zh", "en"],
        help="PRD.md language: auto/zh/en (default: auto).",
    )
    prd_render.set_defaults(func=_cmd_prd_render)

    prd_slice = prd_subparsers.add_parser("slice", help="Generate low-noise slices under docs/prd-slices/")
    prd_slice.add_argument("--workspace", default=".", help="Workspace root that contains ./docs.")
    prd_slice.add_argument(
        "--fix",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Auto-fix and write back docs/prd-pack.json before slicing (default: true).",
    )
    prd_slice.add_argument(
        "--clean",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Delete docs/prd-slices/ before writing (default: true).",
    )
    prd_slice.add_argument("--max-lines", type=int, default=350, help="Max lines per slice file (default: 350).")
    prd_slice.add_argument("--max-chars", type=int, default=12000, help="Max chars per slice file (default: 12000).")
    prd_slice.set_defaults(func=_cmd_prd_slice)

    register_prd_patch_command(prd_subparsers)

