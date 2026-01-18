from __future__ import annotations

from pathlib import Path
from typing import Any

from .prd_pack_types import Failure
from .split_pack_io import ensure_dir
from .split_story_prd import build_table_indices, extract_api_endpoints_by_id, extract_modules_by_id
from .split_story_generate_plan import build_api_by_story, distribute_feature_points, validate_feature_point_assignment
from .split_story_generate_write import write_story_files_for_stories


def generate_story_files(
    *,
    split_plan_pack: dict[str, Any],
    prd_pack: dict[str, Any],
    out_dir: Path,
    clean: bool,
) -> tuple[list[Path], list[Failure]]:
    failures: list[Failure] = []
    written: list[Path] = []

    if clean and out_dir.exists():
        for path in out_dir.glob("story-*.json"):
            path.unlink(missing_ok=True)

    ensure_dir(out_dir)

    modules_by_id = extract_modules_by_id(prd_pack)
    table_name_to_id, table_by_id = build_table_indices(prd_pack)
    api_by_id = extract_api_endpoints_by_id(prd_pack)

    stories_value = split_plan_pack.get("stories")
    if not isinstance(stories_value, list):
        return [], [
            Failure(
                loc="$.stories",
                problem="expected array",
                expected="array",
                impact="cannot generate stories",
                fix="fix split-plan-pack.json stories[]",
            )
        ]

    stories: list[dict[str, Any]] = []
    for item in stories_value:
        if isinstance(item, dict):
            stories.append(item)

    stories.sort(key=lambda x: x.get("n", 0) if isinstance(x.get("n"), int) else 0)

    api_by_story = build_api_by_story(split_plan_pack=split_plan_pack, stories=stories, api_by_id=api_by_id)
    story_fps = distribute_feature_points(stories=stories, modules_by_id=modules_by_id, failures=failures)
    if not validate_feature_point_assignment(modules_by_id=modules_by_id, story_fps=story_fps, failures=failures):
        return [], failures

    written = write_story_files_for_stories(
        stories=stories,
        story_fps=story_fps,
        api_by_story=api_by_story,
        api_by_id=api_by_id,
        table_name_to_id=table_name_to_id,
        table_by_id=table_by_id,
        out_dir=out_dir,
        failures=failures,
    )
    return written, failures

