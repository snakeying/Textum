from __future__ import annotations

from typing import Any, Iterable

from .prd_pack_types import Failure, PLACEHOLDER_SENTINEL


def iter_json_paths(value: Any, path: str = "$") -> Iterable[tuple[str, Any]]:
    yield path, value
    if isinstance(value, dict):
        for key, child in value.items():
            yield from iter_json_paths(child, f"{path}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from iter_json_paths(child, f"{path}[{index}]")


def _examples_summary(examples: list[str], *, limit: int = 8) -> str:
    if len(examples) <= limit:
        return ", ".join(examples)
    shown = examples[:limit]
    remaining = len(examples) - limit
    return ", ".join(shown) + f", ... (+{remaining} more)"


def collect_placeholders(scaffold_pack: dict[str, Any]) -> list[Failure]:
    fill_paths: list[str] = []
    todo_paths: list[str] = []
    ellipsis_paths: list[str] = []
    fence_paths: list[str] = []
    for path, value in iter_json_paths(scaffold_pack):
        if not isinstance(value, str):
            continue

        if PLACEHOLDER_SENTINEL in value:
            fill_paths.append(path)

        stripped = value.strip()
        if stripped.upper() in ("TBD", "TODO"):
            todo_paths.append(f"{path}={stripped.upper()}")
        if "[...]" in stripped:
            ellipsis_paths.append(path)
        if "```" in value:
            fence_paths.append(path)

    failures: list[Failure] = []
    if fill_paths:
        failures.append(
            Failure(
                loc="$",
                problem=f"placeholder found: {PLACEHOLDER_SENTINEL} ({len(fill_paths)}) at {_examples_summary(fill_paths)}",
                expected=f"no {PLACEHOLDER_SENTINEL} placeholders",
                impact="scaffold pack is not ready",
                fix=f"replace all {PLACEHOLDER_SENTINEL} placeholders in docs/scaffold-pack.json",
            )
        )
    if todo_paths:
        failures.append(
            Failure(
                loc="$",
                problem=f"placeholder found: TBD/TODO ({len(todo_paths)}) at {_examples_summary(todo_paths)}",
                expected="no TBD/TODO placeholders",
                impact="scaffold pack is not ready",
                fix="replace all TBD/TODO placeholders in docs/scaffold-pack.json",
            )
        )
    if ellipsis_paths:
        failures.append(
            Failure(
                loc="$",
                problem=f"placeholder found: [...] ({len(ellipsis_paths)}) at {_examples_summary(ellipsis_paths)}",
                expected="no [...] placeholders",
                impact="scaffold pack is not ready",
                fix="replace all [...] placeholders in docs/scaffold-pack.json",
            )
        )
    if fence_paths:
        failures.append(
            Failure(
                loc="$",
                problem=f"markdown fence found (```) ({len(fence_paths)}) at {_examples_summary(fence_paths)}",
                expected="no fenced code blocks",
                impact="rendered markdown must not contain code fences",
                fix="remove all ``` fences from docs/scaffold-pack.json",
            )
        )
    return failures

