from __future__ import annotations

import argparse
from pathlib import Path

from textum.prd.prd_pack import read_prd_pack, workspace_paths
from textum.scaffold.scaffold_pack import read_scaffold_pack
from textum.split.split_check_refs import validate_split_refs
from textum.split.split_pack_io import read_json_object
from .textum_cli_emit import emit_stage_result
from .textum_cli_runner import check_stage_result
from .textum_cli_support import _ensure_prd_ready, _ensure_scaffold_ready


def _cmd_split_check2(args: argparse.Namespace) -> int:
    workspace = Path(args.workspace).resolve()
    paths = workspace_paths(workspace)

    prd_pack, prd_read_failures = read_prd_pack(paths["prd_pack"])
    if prd_read_failures:
        result = check_stage_result(
            workspace_root=workspace,
            stage_id="split-check2",
            command=f"uv run --project .claude/skills/textum/scripts textum split check2 --workspace {workspace.as_posix()}",
            failures=prd_read_failures,
            warnings=[],
            next_on_pass="Split Checkout",
            fallback_on_fail="Split Plan",
        )
        emit_stage_result(result)
        return result.exit_code
    assert prd_pack is not None

    prd_ready_failures = _ensure_prd_ready(prd_pack, prd_pack_path=paths["prd_pack"])
    if prd_ready_failures:
        result = check_stage_result(
            workspace_root=workspace,
            stage_id="split-check2",
            command=f"uv run --project .claude/skills/textum/scripts textum split check2 --workspace {workspace.as_posix()}",
            failures=prd_ready_failures,
            warnings=[],
            next_on_pass="Split Checkout",
            fallback_on_fail="Split Plan",
        )
        emit_stage_result(result)
        return result.exit_code

    scaffold_pack, scaffold_read_failures = read_scaffold_pack(paths["scaffold_pack"])
    if scaffold_read_failures:
        result = check_stage_result(
            workspace_root=workspace,
            stage_id="split-check2",
            command=f"uv run --project .claude/skills/textum/scripts textum split check2 --workspace {workspace.as_posix()}",
            failures=scaffold_read_failures,
            warnings=[],
            next_on_pass="Split Checkout",
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
    wrote = [paths["scaffold_pack"].relative_to(workspace).as_posix()] if scaffold_pack_written else []
    if scaffold_ready_failures:
        result = check_stage_result(
            workspace_root=workspace,
            stage_id="split-check2",
            command=f"uv run --project .claude/skills/textum/scripts textum split check2 --workspace {workspace.as_posix()}",
            failures=scaffold_ready_failures,
            warnings=[],
            wrote=wrote,
            next_on_pass="Split Checkout",
            fallback_on_fail="Split Plan",
        )
        emit_stage_result(result)
        return result.exit_code

    index_pack, index_failures = read_json_object(
        paths["split_check_index_pack"],
        missing_fix="regenerate docs/split-check-index-pack.json",
    )
    if index_failures:
        result = check_stage_result(
            workspace_root=workspace,
            stage_id="split-check2",
            command=f"uv run --project .claude/skills/textum/scripts textum split check2 --workspace {workspace.as_posix()}",
            failures=index_failures,
            warnings=[],
            wrote=wrote,
            next_on_pass="Split Checkout",
            fallback_on_fail="Split Plan",
        )
        emit_stage_result(result)
        return result.exit_code
    assert index_pack is not None

    failures = validate_split_refs(index_pack=index_pack, prd_pack=prd_pack, scaffold_pack=scaffold_pack)
    if failures:
        result = check_stage_result(
            workspace_root=workspace,
            stage_id="split-check2",
            command=f"uv run --project .claude/skills/textum/scripts textum split check2 --workspace {workspace.as_posix()}",
            failures=failures,
            warnings=[],
            wrote=wrote,
            next_on_pass="Split Checkout",
            fallback_on_fail="Split Plan",
        )
        emit_stage_result(result)
        return result.exit_code

    result = check_stage_result(
        workspace_root=workspace,
        stage_id="split-check2",
        command=f"uv run --project .claude/skills/textum/scripts textum split check2 --workspace {workspace.as_posix()}",
        failures=[],
        warnings=[],
        wrote=wrote,
        next_on_pass="Split Checkout",
        fallback_on_fail="Split Plan",
    )
    emit_stage_result(result)
    return result.exit_code
