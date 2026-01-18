from __future__ import annotations

from typing import Any, Iterable

from .prd_pack_types import PLACEHOLDER_SENTINEL, Failure
from .prd_pack_maps import build_prd_maps


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


def scan_story_text(text: str, *, path: str) -> list[Failure]:
    failures: list[Failure] = []
    if "```" in text:
        failures.append(
            Failure(
                loc=path,
                problem="contains fenced code block marker ```",
                expected="no ``` anywhere in the story file",
                impact="would pollute model attention/context",
                fix=f"regenerate {path}",
            )
        )
    if PLACEHOLDER_SENTINEL in text:
        failures.append(
            Failure(
                loc=path,
                problem=f"contains placeholder sentinel {PLACEHOLDER_SENTINEL}",
                expected="no placeholders in generated story",
                impact="ambiguous requirements",
                fix="remove placeholder tokens from docs/prd-pack.json",
            )
        )
    return failures


def scan_story_placeholders(story: dict[str, Any], *, path: str) -> list[Failure]:
    todo_paths: list[str] = []
    ellipsis_paths: list[str] = []
    for loc, value in iter_json_paths(story):
        if not isinstance(value, str):
            continue

        stripped = value.strip()
        if stripped.upper() in ("TBD", "TODO"):
            todo_paths.append(f"{loc}={stripped.upper()}")
        if "[...]" in stripped:
            ellipsis_paths.append(loc)

    def placeholder_fix(paths: list[str], *, placeholder: str) -> str:
        if any(p.startswith("$.details") for p in paths):
            return f"replace all {placeholder} placeholders in docs/prd-pack.json"
        return f"replace all {placeholder} placeholders in {path}"

    failures: list[Failure] = []
    if todo_paths:
        failures.append(
            Failure(
                loc=path,
                problem=f"placeholder found: TBD/TODO ({len(todo_paths)}) at {_examples_summary(todo_paths)}",
                expected="no TBD/TODO placeholders",
                impact="story is not executable",
                fix=placeholder_fix(todo_paths, placeholder="TBD/TODO"),
            )
        )
    if ellipsis_paths:
        failures.append(
            Failure(
                loc=path,
                problem=f"placeholder found: [...] ({len(ellipsis_paths)}) at {_examples_summary(ellipsis_paths)}",
                expected="no [...] placeholders",
                impact="story is not executable",
                fix=placeholder_fix(ellipsis_paths, placeholder="[...]"),
            )
        )
    return failures


def require_dict(value: Any, *, loc: str) -> tuple[dict[str, Any] | None, list[Failure]]:
    if not isinstance(value, dict):
        return None, [
            Failure(
                loc=loc,
                problem=f"expected object, got {type(value).__name__}",
                expected="JSON object",
                impact="cannot validate story",
                fix="regenerate the story source file under docs/stories/",
            )
        ]
    return value, []


def require_list(value: Any, *, loc: str) -> tuple[list[Any] | None, list[Failure]]:
    if not isinstance(value, list):
        return None, [
            Failure(
                loc=loc,
                problem=f"expected array, got {type(value).__name__}",
                expected="JSON array",
                impact="cannot validate story",
                fix="regenerate the story source file under docs/stories/",
            )
        ]
    return value, []


def require_non_empty_str(value: Any, *, loc: str) -> list[Failure]:
    if not isinstance(value, str) or not value.strip():
        return [
            Failure(
                loc=loc,
                problem="expected non-empty string",
                expected="non-empty string",
                impact="story is not actionable",
                fix="regenerate the story source file under docs/stories/",
            )
        ]
    return []


def check_id_list(value: Any, *, loc: str, pattern: Any, label: str) -> tuple[list[str], list[Failure]]:
    items, failures = require_list(value, loc=loc)
    if failures:
        return [], failures
    assert items is not None

    result: list[str] = []
    for idx, item in enumerate(items):
        if not isinstance(item, str):
            failures.append(
                Failure(
                    loc=f"{loc}[{idx}]",
                    problem=f"expected {label} id string, got {type(item).__name__}",
                    expected=f"{label} id string",
                    impact="invalid refs",
                    fix="regenerate the story source file under docs/stories/",
                )
            )
            continue
        if pattern.match(item) is None:
            failures.append(
                Failure(
                    loc=f"{loc}[{idx}]",
                    problem=f"invalid {label} id: {item}",
                    expected=f"match pattern {pattern.pattern}",
                    impact="invalid refs",
                    fix="regenerate the story source file under docs/stories/",
                )
            )
            continue
        result.append(item)
    if len(set(result)) != len(result):
        failures.append(
            Failure(
                loc=loc,
                problem=f"duplicate {label} ids",
                expected=f"unique {label} ids",
                impact="ambiguous ownership/refs",
                fix="regenerate the story source file under docs/stories/",
            )
        )
    return result, failures


def build_scaffold_module_ids(scaffold_pack: dict[str, Any]) -> set[str]:
    extracted = scaffold_pack.get("extracted")
    if not isinstance(extracted, dict):
        return set()
    modules = extracted.get("modules_index")
    if not isinstance(modules, list):
        return set()
    ids: set[str] = set()
    for item in modules:
        if not isinstance(item, dict):
            continue
        item_id = item.get("id")
        if isinstance(item_id, str):
            ids.add(item_id)
    return ids

