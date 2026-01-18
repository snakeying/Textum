from __future__ import annotations

from pathlib import Path
from typing import Any

from .prd_pack_types import Failure
from .prd_slices_types import SliceBudget
from .prd_slices_utils import rel_posix, write_json
from .story_exec_types import STORY_EXEC_INDEX_FILENAME, STORY_EXEC_INDEX_SCHEMA_VERSION


def write_story_exec_index(
    *,
    out_dir: Path,
    workspace_root: Path,
    budget: SliceBudget,
    source: dict[str, Any],
    story: dict[str, Any],
    story_snapshot_path: Path,
    base_path: Path,
    business_rules_paths: list[Path],
    table_paths: list[Path],
    files: list[dict[str, Any]],
) -> tuple[Path | None, int, int, list[Failure]]:
    index_obj = {
        "schema_version": STORY_EXEC_INDEX_SCHEMA_VERSION,
        "source": source,
        "budget": {"max_lines": budget.max_lines, "max_chars": budget.max_chars},
        "story": {
            "n": story.get("n"),
            "slug": story.get("slug"),
            "title": story.get("title"),
        },
        "read": [rel_posix(story_snapshot_path, workspace_root), rel_posix(base_path, workspace_root)]
        + [rel_posix(p, workspace_root) for p in business_rules_paths]
        + [rel_posix(p, workspace_root) for p in table_paths],
        "files": files,
    }
    index_path = out_dir / STORY_EXEC_INDEX_FILENAME
    index_lines, index_chars = write_json(index_path, index_obj)
    if index_lines <= budget.max_lines and index_chars <= budget.max_chars:
        return index_path, index_lines, index_chars, []

    return (
        None,
        index_lines,
        index_chars,
        [
            Failure(
                loc=rel_posix(index_path, workspace_root),
                problem=f"index exceeds budget: {index_lines} lines, {index_chars} chars",
                expected=f"<= {budget.max_lines} lines and <= {budget.max_chars} chars",
                impact="cannot produce low-noise story exec pack",
                fix="reduce metadata in index.json",
            )
        ],
    )

