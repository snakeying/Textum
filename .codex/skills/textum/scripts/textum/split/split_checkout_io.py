from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .prd_pack_types import Failure


def read_story_json(path: Path) -> tuple[dict[str, Any] | None, str | None, list[Failure]]:
    if not path.exists():
        return None, None, [
            Failure(
                loc=path.as_posix(),
                problem="file not found",
                expected="file exists",
                impact="cannot build dependency graph",
                fix="generate docs/stories/story-###-<slug>.json",
            )
        ]
    text = path.read_text(encoding="utf-8")
    try:
        obj = json.loads(text)
    except json.JSONDecodeError as error:
        return None, None, [
            Failure(
                loc=path.as_posix(),
                problem=f"invalid JSON: {error.msg} at line {error.lineno} col {error.colno}",
                expected="valid JSON document",
                impact="cannot build dependency graph",
                fix=f"fix JSON syntax in {path.as_posix()}",
            )
        ]
    if not isinstance(obj, dict):
        return None, None, [
            Failure(
                loc=path.as_posix(),
                problem=f"root must be object, got {type(obj).__name__}",
                expected="JSON object at root",
                impact="cannot build dependency graph",
                fix=f"rewrite {path.as_posix()} root as an object",
            )
        ]
    return obj, text, []

