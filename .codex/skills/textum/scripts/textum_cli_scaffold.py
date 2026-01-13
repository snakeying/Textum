from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from prd_pack import skill_asset_paths, workspace_paths
from scaffold_pack import init_scaffold_pack
from scaffold_render import render_global_context_markdown
from textum_cli_support import (
    _load_prd_pack_and_ensure_ready,
    _load_scaffold_pack_and_ensure_ready,
    _print_failures,
)


def _cmd_scaffold_init(args: argparse.Namespace) -> int:
    workspace = Path(args.workspace).resolve()
    paths = workspace_paths(workspace)
    skill_paths = skill_asset_paths()
    written, failures = init_scaffold_pack(skill_paths["scaffold_template"], paths["scaffold_pack"], force=args.force)
    if failures:
        _print_failures(failures)
        return 1
    if written:
        print(f"OK: wrote {paths['scaffold_pack'].as_posix()}")
    else:
        print(f"SKIP: {paths['scaffold_pack'].as_posix()} already exists (use --force to overwrite)")
    return 0


def _cmd_scaffold_check(args: argparse.Namespace) -> int:
    workspace = Path(args.workspace).resolve()
    paths = workspace_paths(workspace)

    prd_pack, prd_failures = _load_prd_pack_and_ensure_ready(paths)
    if prd_failures:
        _print_failures(prd_failures)
        return 1
    assert prd_pack is not None

    scaffold_pack, _, scaffold_failures = _load_scaffold_pack_and_ensure_ready(
        paths, prd_pack=prd_pack, fix=args.fix
    )
    if scaffold_failures:
        _print_failures(scaffold_failures)
        return 1
    assert scaffold_pack is not None

    print("PASS")
    return 0


def _cmd_scaffold_render(args: argparse.Namespace) -> int:
    workspace = Path(args.workspace).resolve()
    paths = workspace_paths(workspace)

    prd_pack, prd_failures = _load_prd_pack_and_ensure_ready(paths)
    if prd_failures:
        _print_failures(prd_failures)
        return 1
    assert prd_pack is not None

    scaffold_pack, _, scaffold_failures = _load_scaffold_pack_and_ensure_ready(
        paths, prd_pack=prd_pack, fix=args.fix
    )
    if scaffold_failures:
        _print_failures(scaffold_failures)
        return 1
    assert scaffold_pack is not None

    markdown = render_global_context_markdown(scaffold_pack)
    paths["docs_dir"].mkdir(parents=True, exist_ok=True)
    paths["global_context"].write_text(markdown, encoding="utf-8")
    print("PASS")
    print(f"wrote: {paths['global_context'].relative_to(workspace).as_posix()}")
    return 0


def register_scaffold_commands(subparsers: Any) -> None:
    scaffold_parser = subparsers.add_parser("scaffold", help="Scaffold/global context commands")
    scaffold_subparsers = scaffold_parser.add_subparsers(dest="scaffold_command", required=True)

    scaffold_init = scaffold_subparsers.add_parser(
        "init", help="Initialize docs/scaffold-pack.json from assets template"
    )
    scaffold_init.add_argument("--workspace", default=".", help="Workspace root that contains ./docs.")
    scaffold_init.add_argument("--force", action="store_true", help="Overwrite existing docs/scaffold-pack.json")
    scaffold_init.set_defaults(func=_cmd_scaffold_init)

    scaffold_check = scaffold_subparsers.add_parser("check", help="Validate docs/scaffold-pack.json")
    scaffold_check.add_argument("--workspace", default=".", help="Workspace root that contains ./docs.")
    scaffold_check.add_argument(
        "--fix",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Auto-fix and write back (default: true).",
    )
    scaffold_check.set_defaults(func=_cmd_scaffold_check)

    scaffold_render = scaffold_subparsers.add_parser(
        "render", help="Render docs/GLOBAL-CONTEXT.md from docs/scaffold-pack.json"
    )
    scaffold_render.add_argument("--workspace", default=".", help="Workspace root that contains ./docs.")
    scaffold_render.add_argument(
        "--fix",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Auto-fix and write back scaffold-pack.json before rendering (default: true).",
    )
    scaffold_render.set_defaults(func=_cmd_scaffold_render)
