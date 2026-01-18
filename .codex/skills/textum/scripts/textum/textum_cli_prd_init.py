from __future__ import annotations

import argparse
from pathlib import Path

from textum.prd.prd_pack import init_prd_pack, skill_asset_paths, workspace_paths
from .textum_cli_emit import emit_stage_result
from .textum_cli_result import StageResult


def _cmd_prd_init(args: argparse.Namespace) -> int:
    workspace = Path(args.workspace).resolve()
    paths = workspace_paths(workspace)
    skill_paths = skill_asset_paths()

    written, failures = init_prd_pack(skill_paths["prd_template"], paths["prd_pack"], force=args.force)
    result = StageResult(
        status="FAIL" if failures else "PASS",
        failures=failures,
        warnings=[],
        wrote=[paths["prd_pack"].relative_to(workspace).as_posix()] if written else [],
        entry=None,
        next_stage="PRD Plan",
        exit_code=1 if failures else 0,
    )
    emit_stage_result(result)
    return result.exit_code
