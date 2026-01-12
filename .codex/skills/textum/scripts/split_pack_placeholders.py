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


def collect_placeholders(value: dict[str, Any]) -> list[Failure]:
    failures: list[Failure] = []
    for path, node in iter_json_paths(value):
        if not isinstance(node, str):
            continue

        if PLACEHOLDER_SENTINEL in node:
            failures.append(
                Failure(
                    loc=path,
                    problem=f"placeholder found: {PLACEHOLDER_SENTINEL}",
                    expected="replace placeholders with final values",
                    impact="split pack is not ready",
                    fix=f"replace {PLACEHOLDER_SENTINEL} at {path}",
                )
            )

        stripped = node.strip()
        if stripped.upper() in ("TBD", "TODO"):
            failures.append(
                Failure(
                    loc=path,
                    problem=f"placeholder found: {stripped}",
                    expected="replace placeholders with final values",
                    impact="split pack is not ready",
                    fix=f"replace {stripped} at {path}",
                )
            )
        if "[...]" in stripped:
            failures.append(
                Failure(
                    loc=path,
                    problem="placeholder found: [...]",
                    expected="replace placeholders with final values",
                    impact="split pack is not ready",
                    fix=f"replace [...] at {path}",
                )
            )
        if "```" in node:
            failures.append(
                Failure(
                    loc=path,
                    problem="markdown fence found (```)",
                    expected="no fenced code blocks",
                    impact="must keep packs tool-friendly",
                    fix=f"remove ``` from {path}",
                )
            )
    return failures

