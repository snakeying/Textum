from __future__ import annotations

import argparse
from pathlib import Path

from textum.prd.prd_pack import check_prd_pack, workspace_paths
from .textum_cli_emit import emit_stage_result
from .textum_cli_runner import check_stage_result
from .textum_cli_support import _load_prd_pack_and_normalize


def _cmd_prd_check(args: argparse.Namespace) -> int:
    workspace = Path(args.workspace).resolve()
    paths = workspace_paths(workspace)

    prd_pack, updated, failures = _load_prd_pack_and_normalize(paths, fix=args.fix)
    if failures:
        result = check_stage_result(
            workspace_root=workspace,
            stage_id="prd-check",
            command=f"uv run --project .codex/skills/textum/scripts textum prd check --workspace {workspace.as_posix()}",
            failures=failures,
            warnings=[],
            next_on_pass="PRD Render",
            fallback_on_fail="PRD Plan",
        )
        emit_stage_result(result)
        return result.exit_code
    assert prd_pack is not None

    ready, check_failures = check_prd_pack(prd_pack)
    if not ready:
        result = check_stage_result(
            workspace_root=workspace,
            stage_id="prd-check",
            command=f"uv run --project .codex/skills/textum/scripts textum prd check --workspace {workspace.as_posix()}",
            failures=check_failures,
            warnings=[],
            next_on_pass="PRD Render",
            fallback_on_fail="PRD Plan",
        )
        emit_stage_result(result)
        return result.exit_code

    wrote = [paths["prd_pack"].relative_to(workspace).as_posix()] if (updated and args.fix) else []
    result = check_stage_result(
        workspace_root=workspace,
        stage_id="prd-check",
        command=f"uv run --project .codex/skills/textum/scripts textum prd check --workspace {workspace.as_posix()}",
        failures=[],
        warnings=[],
        next_on_pass="PRD Render",
        fallback_on_fail="PRD Plan",
        wrote=wrote,
    )
    emit_stage_result(result)
    return result.exit_code
