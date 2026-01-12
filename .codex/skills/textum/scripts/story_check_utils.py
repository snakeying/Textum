from __future__ import annotations

from typing import Any

from prd_pack_types import PLACEHOLDER_SENTINEL, Failure


def scan_story_text(text: str, *, path: str) -> list[Failure]:
    failures: list[Failure] = []
    if "```" in text:
        failures.append(
            Failure(
                loc=path,
                problem="contains fenced code block marker ```",
                expected="no ``` anywhere in the story file",
                impact="would pollute model attention/context",
                fix=f"remove ``` from {path}",
            )
        )
    if PLACEHOLDER_SENTINEL in text:
        failures.append(
            Failure(
                loc=path,
                problem=f"contains placeholder sentinel {PLACEHOLDER_SENTINEL}",
                expected="no placeholders in generated story",
                impact="ambiguous requirements",
                fix=f"fix the upstream source and regenerate {path}",
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
                fix="rewrite this value as a JSON object",
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
                fix="rewrite this value as a JSON array",
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
                fix="fill this field with a non-empty string",
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
                    fix="rewrite this item as a string id",
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
                    fix=f"fix the id at {loc}[{idx}]",
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
                fix=f"dedupe {loc}",
            )
        )
    return result, failures


def build_prd_maps(
    prd_pack: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Any], set[str], dict[str, Any]]:
    api_endpoints = prd_pack.get("api", {}).get("endpoints", [])
    api_by_id: dict[str, Any] = {}
    if isinstance(api_endpoints, list):
        for item in api_endpoints:
            if not isinstance(item, dict):
                continue
            item_id = item.get("id")
            if isinstance(item_id, str):
                api_by_id[item_id] = item

    tables = prd_pack.get("data_model", {}).get("tables", [])
    tbl_by_id: dict[str, Any] = {}
    if isinstance(tables, list):
        for item in tables:
            if not isinstance(item, dict):
                continue
            item_id = item.get("id")
            if isinstance(item_id, str):
                tbl_by_id[item_id] = item

    fp_ids: set[str] = set()
    modules = prd_pack.get("modules", [])
    if isinstance(modules, list):
        for mod in modules:
            if not isinstance(mod, dict):
                continue
            fps = mod.get("feature_points", [])
            if not isinstance(fps, list):
                continue
            for fp in fps:
                if not isinstance(fp, dict):
                    continue
                fp_id = fp.get("id")
                if isinstance(fp_id, str):
                    fp_ids.add(fp_id)

    br_items = prd_pack.get("business_rules", [])
    br_by_id: dict[str, Any] = {}
    if isinstance(br_items, list):
        for item in br_items:
            if not isinstance(item, dict):
                continue
            item_id = item.get("id")
            if isinstance(item_id, str):
                br_by_id[item_id] = item

    return api_by_id, tbl_by_id, fp_ids, br_by_id


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

