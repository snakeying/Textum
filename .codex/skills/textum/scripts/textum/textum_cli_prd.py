from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from .prd_pack import check_prd_pack, init_prd_pack, skill_asset_paths, workspace_paths
from .prd_render import render_prd_markdown
from .prd_slices import SliceBudget, generate_prd_slices
from .textum_cli_artifacts import write_check_artifacts
from .textum_cli_next import _next_stage_for_failures
from .textum_cli_prd_patch import register_prd_patch_command
from .textum_cli_support import _load_prd_pack_and_normalize, _print_failures


def _cmd_prd_init(args: argparse.Namespace) -> int:
    workspace = Path(args.workspace).resolve()
    paths = workspace_paths(workspace)
    skill_paths = skill_asset_paths()
    written, failures = init_prd_pack(skill_paths["prd_template"], paths["prd_pack"], force=args.force)
    if failures:
        _print_failures(failures)
        print("next: PRD Plan")
        return 1
    print("PASS")
    if written:
        print(f"wrote: {paths['prd_pack'].relative_to(workspace).as_posix()}")
    print("next: PRD Plan")
    return 0


def _cmd_prd_check(args: argparse.Namespace) -> int:
    workspace = Path(args.workspace).resolve()
    paths = workspace_paths(workspace)
    prd_pack, updated, failures = _load_prd_pack_and_normalize(paths, fix=args.fix)
    if failures:
        next_stage = _next_stage_for_failures(failures, fallback="PRD Plan")
        _, wrote = write_check_artifacts(
            workspace_root=workspace,
            stage_id="prd-check",
            command=f"uv run --project .codex/skills/textum/scripts textum prd check --workspace {workspace.as_posix()}",
            next_stage=next_stage,
            failures=failures,
        )
        print("FAIL")
        for rel in wrote:
            print(f"wrote: {rel}")
        print(f"next: {next_stage}")
        return 1
    assert prd_pack is not None

    ready, check_failures = check_prd_pack(prd_pack)
    if not ready:
        next_stage = _next_stage_for_failures(check_failures, fallback="PRD Plan")
        _, wrote = write_check_artifacts(
            workspace_root=workspace,
            stage_id="prd-check",
            command=f"uv run --project .codex/skills/textum/scripts textum prd check --workspace {workspace.as_posix()}",
            next_stage=next_stage,
            failures=check_failures,
        )
        print("FAIL")
        for rel in wrote:
            print(f"wrote: {rel}")
        print(f"next: {next_stage}")
        return 1

    print("PASS")
    if updated and args.fix:
        print(f"wrote: {paths['prd_pack'].relative_to(workspace).as_posix()}")
    _, wrote = write_check_artifacts(
        workspace_root=workspace,
        stage_id="prd-check",
        command=f"uv run --project .codex/skills/textum/scripts textum prd check --workspace {workspace.as_posix()}",
        next_stage="PRD Render",
        failures=[],
    )
    for rel in wrote:
        print(f"wrote: {rel}")
    print("next: PRD Render")
    return 0


def _cmd_prd_render(args: argparse.Namespace) -> int:
    workspace = Path(args.workspace).resolve()
    paths = workspace_paths(workspace)
    prd_pack, _, failures = _load_prd_pack_and_normalize(paths, fix=args.fix)
    if failures:
        _print_failures(failures)
        print("next: PRD Plan")
        return 1
    assert prd_pack is not None

    markdown = render_prd_markdown(prd_pack, lang=args.lang)
    paths["docs_dir"].mkdir(parents=True, exist_ok=True)
    paths["prd_render"].write_text(markdown, encoding="utf-8")
    print("PASS")
    print(f"wrote: {paths['prd_render'].relative_to(workspace).as_posix()}")
    print("next: PRD Slice")
    return 0


def _cmd_prd_slice(args: argparse.Namespace) -> int:
    workspace = Path(args.workspace).resolve()
    paths = workspace_paths(workspace)
    prd_pack, _, failures = _load_prd_pack_and_normalize(paths, fix=args.fix)
    if failures:
        _print_failures(failures)
        print("next: PRD Plan")
        return 1
    assert prd_pack is not None

    ready, check_failures = check_prd_pack(prd_pack)
    if not ready:
        _print_failures(check_failures)
        print("next: PRD Plan")
        return 1

    budget = SliceBudget(max_lines=args.max_lines, max_chars=args.max_chars)
    written, failures = generate_prd_slices(
        prd_pack_path=paths["prd_pack"],
        prd_pack=prd_pack,
        out_dir=paths["prd_slices_dir"],
        budget=budget,
        clean=args.clean,
    )
    if failures:
        _print_failures(failures)
        print("next: PRD Plan")
        return 1

    print("PASS")
    print(f"wrote: {paths['prd_slices_dir'].relative_to(workspace).as_posix()}/")
    print("next: Scaffold Plan")
    return 0


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


