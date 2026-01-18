from __future__ import annotations

import argparse
from pathlib import Path

from textum.prd.prd_pack import read_prd_pack, workspace_paths
from textum.scaffold.scaffold_pack import read_scaffold_pack
from textum.split.split_plan_pack import (
    check_split_plan_pack,
    normalize_split_plan_pack,
    read_split_plan_pack,
    write_split_plan_pack,
)
from .textum_cli_emit import emit_stage_result
from .textum_cli_runner import check_stage_result
from .textum_cli_support import _ensure_prd_ready, _ensure_scaffold_ready, _print_check_items


def _cmd_split_plan_check(args: argparse.Namespace) -> int:
    workspace = Path(args.workspace).resolve()
    paths = workspace_paths(workspace)

    prd_pack, prd_read_failures = read_prd_pack(paths["prd_pack"])
    if prd_read_failures:
        result = check_stage_result(
            workspace_root=workspace,
            stage_id="split-plan-check",
            command=f"uv run --project .codex/skills/textum/scripts textum split plan check --workspace {workspace.as_posix()}",
            failures=prd_read_failures,
            warnings=[],
            next_on_pass="Split Generate",
            fallback_on_fail="Split Plan",
        )
        emit_stage_result(result)
        return result.exit_code
    assert prd_pack is not None

    prd_ready_failures = _ensure_prd_ready(prd_pack, prd_pack_path=paths["prd_pack"])
    if prd_ready_failures:
        result = check_stage_result(
            workspace_root=workspace,
            stage_id="split-plan-check",
            command=f"uv run --project .codex/skills/textum/scripts textum split plan check --workspace {workspace.as_posix()}",
            failures=prd_ready_failures,
            warnings=[],
            next_on_pass="Split Generate",
            fallback_on_fail="Split Plan",
        )
        emit_stage_result(result)
        return result.exit_code

    scaffold_pack, scaffold_read_failures = read_scaffold_pack(paths["scaffold_pack"])
    if scaffold_read_failures:
        result = check_stage_result(
            workspace_root=workspace,
            stage_id="split-plan-check",
            command=f"uv run --project .codex/skills/textum/scripts textum split plan check --workspace {workspace.as_posix()}",
            failures=scaffold_read_failures,
            warnings=[],
            next_on_pass="Split Generate",
            fallback_on_fail="Split Plan",
        )
        emit_stage_result(result)
        return result.exit_code
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
        wrote = [paths["scaffold_pack"].relative_to(workspace).as_posix()] if scaffold_pack_written else []
        result = check_stage_result(
            workspace_root=workspace,
            stage_id="split-plan-check",
            command=f"uv run --project .codex/skills/textum/scripts textum split plan check --workspace {workspace.as_posix()}",
            failures=scaffold_ready_failures,
            warnings=[],
            next_on_pass="Split Generate",
            fallback_on_fail="Split Plan",
            wrote=wrote,
        )
        emit_stage_result(result)
        return result.exit_code

    split_plan_pack, read_failures = read_split_plan_pack(paths["split_plan_pack"])
    if read_failures:
        result = check_stage_result(
            workspace_root=workspace,
            stage_id="split-plan-check",
            command=f"uv run --project .codex/skills/textum/scripts textum split plan check --workspace {workspace.as_posix()}",
            failures=read_failures,
            warnings=[],
            next_on_pass="Split Generate",
            fallback_on_fail="Split Plan",
        )
        emit_stage_result(result)
        return result.exit_code
    assert split_plan_pack is not None

    updated, norm_failures = normalize_split_plan_pack(
        split_plan_pack,
        workspace_root=workspace,
        prd_pack_path=paths["prd_pack"],
        scaffold_pack_path=paths["scaffold_pack"],
    )
    if norm_failures:
        result = check_stage_result(
            workspace_root=workspace,
            stage_id="split-plan-check",
            command=f"uv run --project .codex/skills/textum/scripts textum split plan check --workspace {workspace.as_posix()}",
            failures=norm_failures,
            warnings=[],
            next_on_pass="Split Generate",
            fallback_on_fail="Split Plan",
        )
        emit_stage_result(result)
        return result.exit_code

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
        wrote: list[str] = []
        if scaffold_pack_written:
            wrote.append(paths["scaffold_pack"].relative_to(workspace).as_posix())
        if split_plan_pack_written:
            wrote.append(paths["split_plan_pack"].relative_to(workspace).as_posix())
        result = check_stage_result(
            workspace_root=workspace,
            stage_id="split-plan-check",
            command=f"uv run --project .codex/skills/textum/scripts textum split plan check --workspace {workspace.as_posix()}",
            failures=failures_for_next,
            warnings=[] if strict else check_warnings,
            next_on_pass="Split Generate",
            fallback_on_fail="Split Plan",
            wrote=wrote,
        )
        emit_stage_result(result)
        return result.exit_code

    wrote: list[str] = []
    if scaffold_pack_written:
        wrote.append(paths["scaffold_pack"].relative_to(workspace).as_posix())
    if split_plan_pack_written:
        wrote.append(paths["split_plan_pack"].relative_to(workspace).as_posix())

    result = check_stage_result(
        workspace_root=workspace,
        stage_id="split-plan-check",
        command=f"uv run --project .codex/skills/textum/scripts textum split plan check --workspace {workspace.as_posix()}",
        failures=[],
        warnings=check_warnings,
        next_on_pass="Split Generate",
        fallback_on_fail="Split Plan",
        wrote=wrote,
    )
    emit_stage_result(result)
    return result.exit_code
