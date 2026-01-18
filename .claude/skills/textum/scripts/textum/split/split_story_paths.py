from __future__ import annotations

import re
from pathlib import Path


_STORY_FILENAME_RE = re.compile(r"^story-(\d{3})-([a-z0-9]+(?:-[a-z0-9]+)*)\.json$")


def story_filename(n: int, slug: str) -> str:
    return f"story-{n:03d}-{slug}.json"


def parse_story_filename(filename: str) -> tuple[int, str] | None:
    match = _STORY_FILENAME_RE.match(filename)
    if match is None:
        return None
    return int(match.group(1)), match.group(2)


def iter_story_files(dir_path: Path) -> list[Path]:
    if not dir_path.exists():
        return []
    result: list[Path] = []
    for path in dir_path.iterdir():
        if not path.is_file():
            continue
        if parse_story_filename(path.name) is None:
            continue
        result.append(path)
    result.sort(key=lambda p: p.name)
    return result

