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
from textum_cli_support import _ensure_prd_ready, _ensure_scaffold_ready, _print_failures


def _cmd_split_plan_init(args: argparse.Namespace) -> int:
    workspace = Path(args.workspace).resolve()
    paths = workspace_paths(workspace)
    skill_paths = skill_asset_paths()
    written, failures = init_split_plan_pack(skill_paths["split_plan_template"], paths["split_plan_pack"], force=args.force)
    if failures:
        _print_failures(failures)
        return 1
    if written:
        print(f"OK: wrote {paths['split_plan_pack'].as_posix()}")
    else:
        print(f"SKIP: {paths['split_plan_pack'].as_posix()} already exists (use --force to overwrite)")
    return 0


def _cmd_split_plan_check(args: argparse.Namespace) -> int:
    workspace = Path(args.workspace).resolve()
    paths = workspace_paths(workspace)

    prd_pack, prd_read_failures = read_prd_pack(paths["prd_pack"])
    if prd_read_failures:
        _print_failures(prd_read_failures)
        return 1
    assert prd_pack is not None

    prd_ready_failures = _ensure_prd_ready(prd_pack, prd_pack_path=paths["prd_pack"])
    if prd_ready_failures:
        _print_failures(prd_ready_failures)
        return 1

    scaffold_pack, scaffold_read_failures = read_scaffold_pack(paths["scaffold_pack"])
    if scaffold_read_failures:
        _print_failures(scaffold_read_failures)
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
        _print_failures(scaffold_ready_failures)
        return 1

    split_plan_pack, read_failures = read_split_plan_pack(paths["split_plan_pack"])
    if read_failures:
        _print_failures(read_failures)
        return 1
    assert split_plan_pack is not None

    updated, norm_failures = normalize_split_plan_pack(
        split_plan_pack,
        workspace_root=workspace,
        prd_pack_path=paths["prd_pack"],
        scaffold_pack_path=paths["scaffold_pack"],
    )
    if norm_failures:
        _print_failures(norm_failures)
        return 1
    if updated and args.fix:
        write_split_plan_pack(paths["split_plan_pack"], split_plan_pack)

    ready, check_failures = check_split_plan_pack(split_plan_pack, prd_pack=prd_pack)
    if not ready:
        _print_failures(check_failures)
        return 1

    api_counts: dict[str, int] = {}
    api_rows = split_plan_pack.get("api_assignments") if isinstance(split_plan_pack.get("api_assignments"), list) else []
    for row in api_rows:
        if not isinstance(row, dict):
            continue
        story = row.get("story")
        if isinstance(story, str) and story.strip():
            api_counts[story] = api_counts.get(story, 0) + 1
    decisions = [(s, c) for s, c in sorted(api_counts.items(), key=lambda x: x[0]) if c in (4, 5)]

    if decisions:
        print("DECISION")
        for i, (story, count) in enumerate(decisions, start=1):
            print(f"- D-{i:03d}; story={story}; api_assigned={count}; action=consider splitting/redistributing")
        print(f"OK: wrote {paths['split_plan_pack'].as_posix()}")
        return 0

    print("PASS")
    if updated and args.fix:
        print(f"UPDATED: {paths['split_plan_pack'].as_posix()}")
    return 0

