from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from prd_pack_types import Failure, PRD_TEMPLATE_FILENAME


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def read_prd_pack(path: Path) -> tuple[dict[str, Any] | None, list[Failure]]:
    if not path.exists():
        return None, [
            Failure(
                loc=str(path),
                problem="file not found",
                expected="file exists",
                impact="cannot proceed",
                fix="create docs/prd-pack.json",
            )
        ]
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        loc_hint = f"line {error.lineno} col {error.colno}"
        return None, [
            Failure(
                loc=str(path),
                problem=f"invalid JSON: {error.msg} at line {error.lineno} col {error.colno}",
                expected="valid JSON document",
                impact="cannot proceed",
                fix=f"edit {path.as_posix()} to fix JSON syntax at {loc_hint}",
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


def write_prd_pack(path: Path, prd_pack: dict[str, Any]) -> None:
    ensure_dir(path.parent)
    path.write_text(json.dumps(prd_pack, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def init_prd_pack(template_path: Path, out_path: Path, *, force: bool) -> tuple[bool, list[Failure]]:
    if out_path.exists() and not force:
        return False, []
    if not template_path.exists():
        return False, [
            Failure(
                loc=template_path.as_posix(),
                problem="template not found",
                expected="skill assets prd-pack.template.json exists",
                impact="cannot initialize PRD pack",
                fix=f"restore {PRD_TEMPLATE_FILENAME} under the skill assets/",
            )
        ]
    ensure_dir(out_path.parent)
    out_path.write_text(template_path.read_text(encoding="utf-8"), encoding="utf-8")
    return True, []
