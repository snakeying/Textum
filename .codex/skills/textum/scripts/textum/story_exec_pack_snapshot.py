from __future__ import annotations

from pathlib import Path

from .prd_pack_types import Failure
from .prd_slices_types import SliceBudget
from .prd_slices_utils import rel_posix
from .story_exec_types import STORY_EXEC_STORY_SNAPSHOT_FILENAME


def write_story_snapshot_and_check_budget(
    *,
    workspace_root: Path,
    out_dir: Path,
    story_text: str,
    budget: SliceBudget,
) -> tuple[Path, int, int, list[Failure]]:
    story_snapshot_path = out_dir / STORY_EXEC_STORY_SNAPSHOT_FILENAME
    story_snapshot_path.write_text(story_text, encoding="utf-8")
    story_lines = story_text.count("\n")
    story_chars = len(story_text)
    if story_lines <= budget.max_lines and story_chars <= budget.max_chars:
        return story_snapshot_path, story_lines, story_chars, []

    return (
        story_snapshot_path,
        story_lines,
        story_chars,
        [
            Failure(
                loc=rel_posix(story_snapshot_path, workspace_root),
                problem=f"story snapshot exceeds budget: {story_lines} lines, {story_chars} chars",
                expected=f"<= {budget.max_lines} lines and <= {budget.max_chars} chars",
                impact="cannot produce low-noise story exec pack",
                fix="split this story into smaller stories in docs/split-plan-pack.json",
            )
        ],
    )

