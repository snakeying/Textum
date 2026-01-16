from __future__ import annotations

import argparse
from pathlib import Path

from prd_pack import read_prd_pack, workspace_paths
from scaffold_pack import read_scaffold_pack
from split_plan_pack import (
    check_split_plan_pack,
    normalize_split_plan_pack,
    read_split_plan_pack,
    write_split_plan_pack,
)
from split_story_generate import generate_story_files
from textum_cli_next import _print_failures_with_next
from textum_cli_support import _ensure_prd_ready, _ensure_scaffold_ready


def _cmd_split_generate(args: argparse.Namespace) -> int:
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

    _, gen_failures = generate_story_files(
        split_plan_pack=split_plan_pack,
        prd_pack=prd_pack,
        out_dir=paths["stories_dir"],
        clean=args.clean,
    )
    if gen_failures:
        _print_failures_with_next(gen_failures, fallback="Split Plan")
        return 1

    print("PASS")
    print("wrote: docs/stories/")
    print("next: Split Check1")
    return 0
