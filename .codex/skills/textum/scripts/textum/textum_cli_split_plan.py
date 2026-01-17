from __future__ import annotations

import argparse
from pathlib import Path

from .prd_pack import read_prd_pack, skill_asset_paths, workspace_paths
from .scaffold_pack import read_scaffold_pack
from .split_plan_pack import (
    check_split_plan_pack,
    init_split_plan_pack,
    normalize_split_plan_pack,
    read_split_plan_pack,
    write_split_plan_pack,
)
from .textum_cli_artifacts import write_check_artifacts
from .textum_cli_next import _next_stage_for_failures
from .textum_cli_support import _ensure_prd_ready, _ensure_scaffold_ready
from .textum_cli_support import _print_check_items


def _cmd_split_plan_init(args: argparse.Namespace) -> int:
    workspace = Path(args.workspace).resolve()
    paths = workspace_paths(workspace)
    skill_paths = skill_asset_paths()
    written, failures = init_split_plan_pack(skill_paths["split_plan_template"], paths["split_plan_pack"], force=args.force)
    if failures:
        next_stage = _next_stage_for_failures(failures, fallback="Split Plan")
        _, wrote = write_check_artifacts(
            workspace_root=workspace,
            stage_id="split-plan-init",
            command=f"uv run --project .codex/skills/textum/scripts textum split plan init --workspace {workspace.as_posix()}",
            next_stage=next_stage,
            failures=failures,
        )
        print("FAIL")
        for rel in wrote:
            print(f"wrote: {rel}")
        print(f"next: {next_stage}")
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
        next_stage = _next_stage_for_failures(prd_read_failures, fallback="Split Plan")
        _, wrote = write_check_artifacts(
            workspace_root=workspace,
            stage_id="split-plan-check",
            command=f"uv run --project .codex/skills/textum/scripts textum split plan check --workspace {workspace.as_posix()}",
            next_stage=next_stage,
            failures=prd_read_failures,
        )
        print("FAIL")
        _print_check_items(prd_read_failures, label="FAIL")
        for rel in wrote:
            print(f"wrote: {rel}")
        print(f"next: {next_stage}")
        return 1
    assert prd_pack is not None

    prd_ready_failures = _ensure_prd_ready(prd_pack, prd_pack_path=paths["prd_pack"])
    if prd_ready_failures:
        next_stage = _next_stage_for_failures(prd_ready_failures, fallback="Split Plan")
        _, wrote = write_check_artifacts(
            workspace_root=workspace,
            stage_id="split-plan-check",
            command=f"uv run --project .codex/skills/textum/scripts textum split plan check --workspace {workspace.as_posix()}",
            next_stage=next_stage,
            failures=prd_ready_failures,
        )
        print("FAIL")
        _print_check_items(prd_ready_failures, label="FAIL")
        for rel in wrote:
            print(f"wrote: {rel}")
        print(f"next: {next_stage}")
        return 1

    scaffold_pack, scaffold_read_failures = read_scaffold_pack(paths["scaffold_pack"])
    if scaffold_read_failures:
        next_stage = _next_stage_for_failures(scaffold_read_failures, fallback="Split Plan")
        _, wrote = write_check_artifacts(
            workspace_root=workspace,
            stage_id="split-plan-check",
            command=f"uv run --project .codex/skills/textum/scripts textum split plan check --workspace {workspace.as_posix()}",
            next_stage=next_stage,
            failures=scaffold_read_failures,
        )
        print("FAIL")
        _print_check_items(scaffold_read_failures, label="FAIL")
        for rel in wrote:
            print(f"wrote: {rel}")
        print(f"next: {next_stage}")
        return 1
    assert scaffold_pack is not None

    scaffold_updated, scaffold_ready_failures = _ensure_scaffold_ready(
        scaffold_pack,  # type: ignore[arg-type]
        prd_pack_path=paths["prd_pack"],
        prd_pack=prd_pack,  # type: ignore[arg-type]
        scaffold_pack_path=paths["scaffold_pack"],
        fix=args.fix,
    )
    scaffold_pack_written = scaffold_updated and args.fix
    if scaffold_ready_failures:
        next_stage = _next_stage_for_failures(scaffold_ready_failures, fallback="Split Plan")
        _, wrote = write_check_artifacts(
            workspace_root=workspace,
            stage_id="split-plan-check",
            command=f"uv run --project .codex/skills/textum/scripts textum split plan check --workspace {workspace.as_posix()}",
            next_stage=next_stage,
            failures=scaffold_ready_failures,
        )
        print("FAIL")
        _print_check_items(scaffold_ready_failures, label="FAIL")
        if scaffold_pack_written:
            print(f"wrote: {paths['scaffold_pack'].relative_to(workspace).as_posix()}")
        for rel in wrote:
            print(f"wrote: {rel}")
        print(f"next: {next_stage}")
        return 1

    split_plan_pack, read_failures = read_split_plan_pack(paths["split_plan_pack"])
    if read_failures:
        next_stage = _next_stage_for_failures(read_failures, fallback="Split Plan")
        _, wrote = write_check_artifacts(
            workspace_root=workspace,
            stage_id="split-plan-check",
            command=f"uv run --project .codex/skills/textum/scripts textum split plan check --workspace {workspace.as_posix()}",
            next_stage=next_stage,
            failures=read_failures,
        )
        print("FAIL")
        _print_check_items(read_failures, label="FAIL")
        for rel in wrote:
            print(f"wrote: {rel}")
        print(f"next: {next_stage}")
        return 1
    assert split_plan_pack is not None

    updated, norm_failures = normalize_split_plan_pack(
        split_plan_pack,
        workspace_root=workspace,
        prd_pack_path=paths["prd_pack"],
        scaffold_pack_path=paths["scaffold_pack"],
    )
    if norm_failures:
        next_stage = _next_stage_for_failures(norm_failures, fallback="Split Plan")
        _, wrote = write_check_artifacts(
            workspace_root=workspace,
            stage_id="split-plan-check",
            command=f"uv run --project .codex/skills/textum/scripts textum split plan check --workspace {workspace.as_posix()}",
            next_stage=next_stage,
            failures=norm_failures,
        )
        print("FAIL")
        _print_check_items(norm_failures, label="FAIL")
        for rel in wrote:
            print(f"wrote: {rel}")
        print(f"next: {next_stage}")
        return 1
    split_plan_pack_written = False
    if updated and args.fix:
        write_split_plan_pack(paths["split_plan_pack"], split_plan_pack)
        split_plan_pack_written = True

    ready, check_failures, check_warnings = check_split_plan_pack(
        split_plan_pack, prd_pack=prd_pack, strict=getattr(args, "strict", False)
    )
    if not ready:
        strict = getattr(args, "strict", False) is True
        failures_for_next = check_failures + (check_warnings if strict else [])
        next_stage = _next_stage_for_failures(failures_for_next, fallback="Split Plan")
        _, wrote = write_check_artifacts(
            workspace_root=workspace,
            stage_id="split-plan-check",
            command=f"uv run --project .codex/skills/textum/scripts textum split plan check --workspace {workspace.as_posix()}",
            next_stage=next_stage,
            failures=failures_for_next,
            warnings=[] if strict else check_warnings,
        )
        print("FAIL")
        _print_check_items(failures_for_next, label="FAIL")
        if scaffold_pack_written:
            print(f"wrote: {paths['scaffold_pack'].relative_to(workspace).as_posix()}")
        if split_plan_pack_written:
            print(f"wrote: {paths['split_plan_pack'].relative_to(workspace).as_posix()}")
        for rel in wrote:
            print(f"wrote: {rel}")
        print(f"next: {next_stage}")
        return 1

    print("PASS")
    if check_warnings:
        _print_check_items(check_warnings, label="WARN")
    if scaffold_pack_written:
        print(f"wrote: {paths['scaffold_pack'].relative_to(workspace).as_posix()}")
    if split_plan_pack_written:
        print(f"wrote: {paths['split_plan_pack'].relative_to(workspace).as_posix()}")
    _, wrote = write_check_artifacts(
        workspace_root=workspace,
        stage_id="split-plan-check",
        command=f"uv run --project .codex/skills/textum/scripts textum split plan check --workspace {workspace.as_posix()}",
        next_stage="Split Generate",
        failures=[],
        warnings=check_warnings,
    )
    for rel in wrote:
        print(f"wrote: {rel}")
    print("next: Split Generate")
    return 0

