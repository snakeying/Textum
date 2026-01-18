from __future__ import annotations

import argparse
from pathlib import Path

from textum.prd.prd_pack import check_prd_pack, workspace_paths
from textum.prd.prd_slices import SliceBudget, generate_prd_slices
from .textum_cli_emit import emit_stage_result
from .textum_cli_runner import simple_stage_result
from .textum_cli_support import _load_prd_pack_and_normalize


def _cmd_prd_slice(args: argparse.Namespace) -> int:
    workspace = Path(args.workspace).resolve()
    paths = workspace_paths(workspace)

    prd_pack, _, failures = _load_prd_pack_and_normalize(paths, fix=args.fix)
    if failures:
        result = simple_stage_result(
            failures=failures,
            warnings=[],
            wrote=[],
            entry=None,
            next_on_pass="Scaffold Plan",
            fallback_on_fail="PRD Plan",
        )
        emit_stage_result(result)
        return result.exit_code
    assert prd_pack is not None

    ready, check_failures = check_prd_pack(prd_pack)
    if not ready:
        result = simple_stage_result(
            failures=check_failures,
            warnings=[],
            wrote=[],
            entry=None,
            next_on_pass="Scaffold Plan",
            fallback_on_fail="PRD Plan",
        )
        emit_stage_result(result)
        return result.exit_code

    budget = SliceBudget(max_lines=args.max_lines, max_chars=args.max_chars)
    _, failures = generate_prd_slices(
        prd_pack_path=paths["prd_pack"],
        prd_pack=prd_pack,
        out_dir=paths["prd_slices_dir"],
        budget=budget,
        clean=args.clean,
    )
    if failures:
        result = simple_stage_result(
            failures=failures,
            warnings=[],
            wrote=[],
            entry=None,
            next_on_pass="Scaffold Plan",
            fallback_on_fail="PRD Plan",
        )
        emit_stage_result(result)
        return result.exit_code

    result = simple_stage_result(
        failures=[],
        warnings=[],
        wrote=[f"{paths['prd_slices_dir'].relative_to(workspace).as_posix()}/"],
        entry=None,
        next_on_pass="Scaffold Plan",
        fallback_on_fail="PRD Plan",
    )
    emit_stage_result(result)
    return result.exit_code
