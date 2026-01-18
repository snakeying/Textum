from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Callable, Iterable

from .prd_pack_types import Failure
from .prd_slices_types import SliceBudget


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def json_text(obj: Any) -> str:
    return json.dumps(obj, ensure_ascii=False, indent=2) + "\n"


def measure_json(obj: Any) -> tuple[int, int]:
    text = json_text(obj)
    return (text.count("\n"), len(text))


def write_json(path: Path, obj: Any) -> tuple[int, int]:
    text = json_text(obj)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return (text.count("\n"), len(text))


def rel_posix(path: Path, workspace_root: Path) -> str:
    try:
        return path.relative_to(workspace_root).as_posix()
    except ValueError:
        return path.as_posix()


def id_range(ids: Iterable[str]) -> tuple[str | None, str | None]:
    first: str | None = None
    last: str | None = None
    for item_id in ids:
        if first is None:
            first = item_id
        last = item_id
    return first, last


def chunk_list(
    items: list[Any],
    build_obj: Callable[[list[Any]], dict[str, Any]],
    *,
    budget: SliceBudget,
    loc: str,
    item_label: str,
) -> tuple[list[dict[str, Any]], list[Failure]]:
    if len(items) == 0:
        obj = build_obj([])
        lines, chars = measure_json(obj)
        if lines > budget.max_lines or chars > budget.max_chars:
            return (
                [],
                [
                    Failure(
                        loc=loc,
                        problem=f"empty {item_label} slice exceeds budget",
                        expected=f"<= {budget.max_lines} lines and <= {budget.max_chars} chars",
                        impact="cannot produce low-noise slices",
                        fix="reduce slice metadata",
                    )
                ],
            )
        return [obj], []

    parts: list[dict[str, Any]] = []
    failures: list[Failure] = []
    current: list[Any] = []

    for index, item in enumerate(items):
        candidate = current + [item]
        candidate_obj = build_obj(candidate)
        lines, chars = measure_json(candidate_obj)

        if lines <= budget.max_lines and chars <= budget.max_chars:
            current = candidate
            continue

        if len(current) == 0:
            single_obj = build_obj([item])
            single_lines, single_chars = measure_json(single_obj)
            failures.append(
                Failure(
                    loc=f"{loc}[{index}]",
                    problem=f"single {item_label} item exceeds budget: {single_lines} lines, {single_chars} chars",
                    expected=f"<= {budget.max_lines} lines and <= {budget.max_chars} chars",
                    impact="cannot auto-chunk this item further",
                    fix="reduce this item content in docs/prd-pack.json",
                )
            )
            return [], failures

        parts.append(build_obj(current))
        current = [item]

    if current:
        parts.append(build_obj(current))

    return parts, failures

