from __future__ import annotations

import argparse
from pathlib import Path

from textum.prd.prd_pack import skill_asset_paths, workspace_paths
from textum.split.split_plan_pack import init_split_plan_pack
from .textum_cli_emit import emit_stage_result
from .textum_cli_runner import check_stage_result
from .textum_cli_result import StageResult


def _cmd_split_plan_init(args: argparse.Namespace) -> int:
    workspace = Path(args.workspace).resolve()
    paths = workspace_paths(workspace)
    skill_paths = skill_asset_paths()

    written, failures = init_split_plan_pack(
        skill_paths["split_plan_template"], paths["split_plan_pack"], force=args.force
    )
    if failures:
        result = check_stage_result(
            workspace_root=workspace,
            stage_id="split-plan-init",
            command=f"uv run --project .claude/skills/textum/scripts textum split plan init --workspace {workspace.as_posix()}",
            failures=failures,
            warnings=[],
            next_on_pass="Split Plan",
            fallback_on_fail="Split Plan",
        )
        emit_stage_result(result)
        return result.exit_code

    result = StageResult(
        status="PASS",
        failures=[],
        warnings=[],
        wrote=[paths["split_plan_pack"].relative_to(workspace).as_posix()] if written else [],
        entry=None,
        next_stage="Split Plan",
        exit_code=0,
    )
    emit_stage_result(result)
    return result.exit_code
