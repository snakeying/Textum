from __future__ import annotations

import json
from pathlib import Path

from .prd_pack import Failure
from .story_exec_paths import find_story_source


def load_story_source(*, stories_dir: Path, n: int) -> tuple[Path | None, str | None, dict | None, list[Failure]]:
    story_path, failures = find_story_source(stories_dir, n=n)
    if failures:
        return None, None, None, failures

    story_text = story_path.read_text(encoding="utf-8")
    try:
        story = json.loads(story_text)
    except json.JSONDecodeError as error:
        return (
            None,
            None,
            None,
            [
                Failure(
                    loc=story_path.as_posix(),
                    problem=f"invalid JSON: {error.msg} at line {error.lineno} col {error.colno}",
                    expected="valid JSON document",
                    impact="cannot proceed",
                    fix=f"regenerate {story_path.as_posix()}",
                )
            ],
        )
    if not isinstance(story, dict):
        return (
            None,
            None,
            None,
            [
                Failure(
                    loc="$",
                    problem=f"root must be object, got {type(story).__name__}",
                    expected="JSON object at root",
                    impact="cannot proceed",
                    fix=f"regenerate {story_path.as_posix()}",
                )
            ],
        )

    return story_path, story_text, story, []

