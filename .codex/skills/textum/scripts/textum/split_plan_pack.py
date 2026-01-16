from __future__ import annotations

from pathlib import Path
from typing import Any

from .prd_pack_types import Failure
from .split_pack_io import read_json_object, write_json
from .split_plan_pack_validate import check_split_plan_pack, normalize_split_plan_pack

__all__ = [
    "check_split_plan_pack",
    "init_split_plan_pack",
    "normalize_split_plan_pack",
    "read_split_plan_pack",
    "write_split_plan_pack",
]


def read_split_plan_pack(path: Path) -> tuple[dict[str, Any] | None, list[Failure]]:
    return read_json_object(path, missing_fix="create docs/split-plan-pack.json")


def write_split_plan_pack(path: Path, split_plan_pack: dict[str, Any]) -> None:
    write_json(path, split_plan_pack)


def init_split_plan_pack(template_path: Path, out_path: Path, *, force: bool) -> tuple[bool, list[Failure]]:
    if out_path.exists() and not force:
        return False, []
    if not template_path.exists():
        return False, [
            Failure(
                loc=template_path.as_posix(),
                problem="template not found",
                expected="skill assets split-plan-pack.template.json exists",
                impact="cannot initialize split plan pack",
                fix="restore split-plan-pack.template.json under the skill assets/",
            )
        ]
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(template_path.read_text(encoding="utf-8"), encoding="utf-8")
    return True, []

