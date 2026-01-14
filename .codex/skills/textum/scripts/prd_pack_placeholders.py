from __future__ import annotations

from typing import Any, Iterable

from prd_pack_types import Failure, PLACEHOLDER_SENTINEL


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


def collect_placeholders(prd_pack: dict[str, Any]) -> list[Failure]:
    placeholder_paths: list[str] = []
    fence_paths: list[str] = []
    for path, value in iter_json_paths(prd_pack):
        if not isinstance(value, str):
            continue
        if PLACEHOLDER_SENTINEL in value:
            placeholder_paths.append(path)
        if "```" in value:
            fence_paths.append(path)

    failures: list[Failure] = []
    if placeholder_paths:
        failures.append(
            Failure(
                loc="$",
                problem=f"placeholder found: {PLACEHOLDER_SENTINEL} ({len(placeholder_paths)}) at {_examples_summary(placeholder_paths)}",
                expected=f"no {PLACEHOLDER_SENTINEL} placeholders",
                impact="PRD is not ready",
                fix=f"replace all {PLACEHOLDER_SENTINEL} placeholders in docs/prd-pack.json",
            )
        )
    if fence_paths:
        failures.append(
            Failure(
                loc="$",
                problem=f"markdown fence found (```) ({len(fence_paths)}) at {_examples_summary(fence_paths)}",
                expected="no fenced code blocks",
                impact="PRD.md must not contain code fences",
                fix="remove all ``` fences from docs/prd-pack.json",
            )
        )
    return failures
