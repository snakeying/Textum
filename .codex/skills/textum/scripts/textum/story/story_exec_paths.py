from __future__ import annotations

from pathlib import Path

from .prd_pack_types import Failure
from .split_story_paths import iter_story_files, parse_story_filename
from .story_exec_types import STORY_EXEC_DIRNAME


def find_story_source(stories_dir: Path, *, n: int) -> tuple[Path | None, list[Failure]]:
    matches: list[Path] = []
    for path in iter_story_files(stories_dir):
        parsed = parse_story_filename(path.name)
        if parsed is None:
            continue
        story_n, _ = parsed
        if story_n == n:
            matches.append(path)
    if len(matches) == 0:
        return None, [
            Failure(
                loc=str(stories_dir),
                problem=f"story file not found for n={n}",
                expected=f"one file matching story-{n:03d}-*.json under docs/stories/",
                impact="cannot proceed",
                fix=f"create docs/stories/story-{n:03d}-*.json",
            )
        ]
    if len(matches) > 1:
        return None, [
            Failure(
                loc=str(stories_dir),
                problem=f"multiple story files found for n={n}",
                expected=f"exactly one file matching story-{n:03d}-*.json",
                impact="ambiguous story source",
                fix=f"delete duplicate story files under {stories_dir.as_posix()} so only one remains",
            )
        ]
    return matches[0], []


def story_exec_dir(docs_dir: Path, *, story_source: Path) -> Path:
    return docs_dir / STORY_EXEC_DIRNAME / story_source.stem

