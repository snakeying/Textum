from __future__ import annotations

import argparse
from pathlib import Path

from prd_pack import read_prd_pack, skill_asset_paths, workspace_paths
from scaffold_pack import read_scaffold_pack
from split_plan_pack import (
    check_split_plan_pack,
    init_split_plan_pack,
    normalize_split_plan_pack,
    read_split_plan_pack,
    write_split_plan_pack,
)
from textum_cli_next import _print_failures_with_next
from textum_cli_support import _ensure_prd_ready, _ensure_scaffold_ready


def _cmd_split_plan_init(args: argparse.Namespace) -> int:
    workspace = Path(args.workspace).resolve()
    paths = workspace_paths(workspace)
    skill_paths = skill_asset_paths()
    written, failures = init_split_plan_pack(skill_paths["split_plan_template"], paths["split_plan_pack"], force=args.force)
    if failures:
        _print_failures_with_next(failures, fallback="Split Plan")
        return 1
    print("PASS")
    if written:
        print(f"wrote: {paths['split_plan_pack'].relative_to(workspace).as_posix()}")
    print("next: Split Plan")
    return 0


def _cmd_split_plan_check(args: argparse.Namespace) -> int:
    workspace = Path(args.workspace).resolve()
    paths = workspace_paths(workspace)

    prd_pack, prd_read_failures = read_prd_pack(paths["prd_pack"])
    if prd_read_failures:
        _print_failures_with_next(prd_read_failures, fallback="Split Plan")
        return 1
    assert prd_pack is not None

    prd_ready_failures = _ensure_prd_ready(prd_pack, prd_pack_path=paths["prd_pack"])
    if prd_ready_failures:
        _print_failures_with_next(prd_ready_failures, fallback="Split Plan")
        return 1

    scaffold_pack, scaffold_read_failures = read_scaffold_pack(paths["scaffold_pack"])
    if scaffold_read_failures:
        _print_failures_with_next(scaffold_read_failures, fallback="Split Plan")
        return 1
    assert scaffold_pack is not None

    _, scaffold_ready_failures = _ensure_scaffold_ready(
        scaffold_pack,  # type: ignore[arg-type]
        prd_pack_path=paths["prd_pack"],
        prd_pack=prd_pack,  # type: ignore[arg-type]
        scaffold_pack_path=paths["scaffold_pack"],
        fix=args.fix,
    )
    if scaffold_ready_failures:
        _print_failures_with_next(scaffold_ready_failures, fallback="Split Plan")
        return 1

    split_plan_pack, read_failures = read_split_plan_pack(paths["split_plan_pack"])
    if read_failures:
        _print_failures_with_next(read_failures, fallback="Split Plan")
        return 1
    assert split_plan_pack is not None

    updated, norm_failures = normalize_split_plan_pack(
        split_plan_pack,
        workspace_root=workspace,
        prd_pack_path=paths["prd_pack"],
        scaffold_pack_path=paths["scaffold_pack"],
    )
    if norm_failures:
        _print_failures_with_next(norm_failures, fallback="Split Plan")
        return 1
    if updated and args.fix:
        write_split_plan_pack(paths["split_plan_pack"], split_plan_pack)

    ready, check_failures = check_split_plan_pack(split_plan_pack, prd_pack=prd_pack)
    if not ready:
        _print_failures_with_next(check_failures, fallback="Split Plan")
        return 1

    print("PASS")
    print("next: Split Generate")
    return 0
