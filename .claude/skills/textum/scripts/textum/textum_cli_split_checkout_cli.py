from __future__ import annotations

import argparse
from pathlib import Path

from textum.prd.prd_pack import workspace_paths
from textum.split.split_checkout import write_story_dependency_mermaid
from .textum_cli_emit import emit_stage_result
from .textum_cli_runner import check_stage_result


def _cmd_split_checkout(args: argparse.Namespace) -> int:
    workspace = Path(args.workspace).resolve()
    paths = workspace_paths(workspace)

    failures = write_story_dependency_mermaid(stories_dir=paths["stories_dir"], out_path=paths["story_mermaid"])
    wrote = [paths["story_mermaid"].relative_to(workspace).as_posix()] if not failures else []
    result = check_stage_result(
        workspace_root=workspace,
        stage_id="split-checkout",
        command=f"uv run --project .claude/skills/textum/scripts textum split checkout --workspace {workspace.as_posix()}",
        failures=failures,
        warnings=[],
        wrote=wrote,
        next_on_pass="Story Check",
        fallback_on_fail="Split Generate",
    )
    emit_stage_result(result)
    return result.exit_code
