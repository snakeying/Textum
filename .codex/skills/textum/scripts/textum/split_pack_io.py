from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .prd_pack_types import Failure


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def read_json_object(path: Path, *, missing_fix: str) -> tuple[dict[str, Any] | None, list[Failure]]:
    if not path.exists():
        return None, [
            Failure(
                loc=str(path),
                problem="file not found",
                expected="file exists",
                impact="cannot proceed",
                fix=missing_fix,
            )
        ]
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        return None, [
            Failure(
                loc=str(path),
                problem=f"invalid JSON: {error.msg} at line {error.lineno} col {error.colno}",
                expected="valid JSON document",
                impact="cannot proceed",
                fix=f"fix JSON syntax in {path.as_posix()}",
            )
        ]
    if not isinstance(data, dict):
        return None, [
            Failure(
                loc="$",
                problem=f"root must be object, got {type(data).__name__}",
                expected="JSON object at root",
                impact="cannot proceed",
                fix=f"rewrite {path.as_posix()} root as an object",
            )
        ]
    return data, []


def write_json(path: Path, value: dict[str, Any]) -> None:
    ensure_dir(path.parent)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


