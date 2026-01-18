from __future__ import annotations

import argparse
from pathlib import Path

from textum.split.split_check_index_pack import build_split_replan_pack, generate_split_check_index_pack
from textum.split.split_plan_pack import read_split_plan_pack
from .textum_cli_emit import emit_stage_result
from .textum_cli_runner import check_stage_result
from textum.prd.prd_pack import workspace_paths


def _cmd_split_check1(args: argparse.Namespace) -> int:
    workspace = Path(args.workspace).resolve()
    paths = workspace_paths(workspace)

    split_plan_pack, read_failures = read_split_plan_pack(paths["split_plan_pack"])
    if read_failures:
        result = check_stage_result(
            workspace_root=workspace,
            stage_id="split-check1",
            command=f"uv run --project .claude/skills/textum/scripts textum split check1 --workspace {workspace.as_posix()}",
            failures=read_failures,
            warnings=[],
            next_on_pass="Split Check2",
            fallback_on_fail="Split Plan",
        )
        emit_stage_result(result)
        return result.exit_code
    assert split_plan_pack is not None

    index_pack, failures, warnings = generate_split_check_index_pack(
        split_plan_pack_path=paths["split_plan_pack"],
        split_plan_pack=split_plan_pack,
        stories_dir=paths["stories_dir"],
        out_path=paths["split_check_index_pack"],
        max_story_lines=args.max_lines,
        max_story_chars=args.max_chars,
        strict=getattr(args, "strict", False) is True,
    )

    split_replan_written = False
    if isinstance(index_pack, dict):
        replan = build_split_replan_pack(index_pack=index_pack)
        if isinstance(replan.get("oversized_stories"), list) and len(replan["oversized_stories"]) > 0:
            import json

            paths["split_replan_pack"].write_text(
                json.dumps(replan, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
            split_replan_written = True

    wrote = [paths["split_replan_pack"].relative_to(workspace).as_posix()] if split_replan_written else []
    extra = {"split_replan_pack": "docs/split-replan-pack.json"} if split_replan_written else None
    if failures:
        result = check_stage_result(
            workspace_root=workspace,
            stage_id="split-check1",
            command=f"uv run --project .claude/skills/textum/scripts textum split check1 --workspace {workspace.as_posix()}",
            failures=failures,
            warnings=warnings,
            wrote=wrote,
            extra=extra,
            next_on_pass="Split Check2",
            fallback_on_fail="Split Generate",
        )
        emit_stage_result(result)
        return result.exit_code

    result = check_stage_result(
        workspace_root=workspace,
        stage_id="split-check1",
        command=f"uv run --project .claude/skills/textum/scripts textum split check1 --workspace {workspace.as_posix()}",
        failures=[],
        warnings=warnings,
        wrote=wrote,
        extra=extra,
        next_on_pass="Split Check2",
        fallback_on_fail="Split Generate",
    )
    emit_stage_result(result)
    return result.exit_code
