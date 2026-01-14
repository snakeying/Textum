from __future__ import annotations

from pathlib import Path
from typing import Any

from prd_pack_types import Failure
from split_pack_io import read_json_object


def read_story(path: Path) -> tuple[dict[str, Any] | None, list[Failure]]:
    return read_json_object(path, missing_fix=f"regenerate story file {path.as_posix()}")


def count_lines_chars(path: Path) -> tuple[int, int]:
    content = path.read_text(encoding="utf-8")
    return content.count("\n") + 1, len(content)
