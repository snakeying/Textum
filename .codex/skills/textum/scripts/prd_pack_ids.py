from __future__ import annotations

import re
from typing import Any, Iterable

from prd_pack_types import (
    API_ID_RE,
    BR_ID_RE,
    FP_ID_RE,
    MODULE_ID_RE,
    SC_ID_RE,
    TBL_ID_RE,
    Failure,
)


def _extract_id_number(pattern: re.Pattern[str], value: str) -> int | None:
    match = pattern.match(value)
    if not match:
        return None
    return int(match.group(1))


def _format_seq_id(prefix: str, number: int, width: int) -> str:
    return f"{prefix}-{number:0{width}d}"


def _next_id(pattern: re.Pattern[str], existing_ids: Iterable[str], prefix: str, width: int) -> str:
    max_number = 0
    for existing_id in existing_ids:
        number = _extract_id_number(pattern, existing_id)
        if number is not None:
            max_number = max(max_number, number)
    return _format_seq_id(prefix, max_number + 1, width)


def _assign_seq_ids(
    items: list[dict[str, Any]],
    *,
    id_field: str,
    pattern: re.Pattern[str],
    prefix: str,
    width: int,
    loc_prefix: str,
) -> tuple[bool, list[Failure]]:
    failures: list[Failure] = []
    modified = False

    existing_ids: list[str] = []
    seen: set[str] = set()
    for index, item in enumerate(items):
        raw_id = item.get(id_field)
        if raw_id is None or (isinstance(raw_id, str) and raw_id.strip() == ""):
            continue
        if not isinstance(raw_id, str):
            failures.append(
                Failure(
                    loc=f"{loc_prefix}[{index}].{id_field}",
                    problem=f"id must be string or null, got {type(raw_id).__name__}",
                    expected="null or a valid ID string",
                    impact="ID policy broken",
                    fix=f"set {loc_prefix}[{index}].{id_field} to null or a valid ID",
                )
            )
            continue
        if not pattern.match(raw_id):
            failures.append(
                Failure(
                    loc=f"{loc_prefix}[{index}].{id_field}",
                    problem=f"invalid id format: {raw_id}",
                    expected=f"{prefix}-{'0'*width}",
                    impact="stable references become unreliable",
                    fix=f"set {loc_prefix}[{index}].{id_field} to null",
                )
            )
            continue
        if raw_id in seen:
            failures.append(
                Failure(
                    loc=f"{loc_prefix}[{index}].{id_field}",
                    problem=f"duplicate id: {raw_id}",
                    expected="unique IDs",
                    impact="anchors/refs become ambiguous",
                    fix=f"deduplicate {prefix} IDs (keep one, set others to null)",
                )
            )
            continue
        seen.add(raw_id)
        existing_ids.append(raw_id)

    if failures:
        return False, failures

    next_value = _next_id(pattern, existing_ids, prefix, width)
    for item in items:
        raw_id = item.get(id_field)
        if raw_id is None or (isinstance(raw_id, str) and raw_id.strip() == ""):
            item[id_field] = next_value
            modified = True
            existing_ids.append(next_value)
            next_value = _next_id(pattern, existing_ids, prefix, width)

    return modified, []


def normalize_prd_pack(prd_pack: dict[str, Any]) -> tuple[bool, list[Failure]]:
    failures: list[Failure] = []
    modified = False

    modules_value = prd_pack.get("modules")
    if isinstance(modules_value, list):
        modules = [m for m in modules_value if isinstance(m, dict)]
        changed, id_failures = _assign_seq_ids(
            modules, id_field="id", pattern=MODULE_ID_RE, prefix="M", width=2, loc_prefix="$.modules"
        )
        modified = modified or changed
        failures.extend(id_failures)

        feature_points: list[dict[str, Any]] = []
        scenarios: list[dict[str, Any]] = []
        for module in modules:
            fps = module.get("feature_points")
            if isinstance(fps, list):
                feature_points.extend([fp for fp in fps if isinstance(fp, dict)])
            scs = module.get("scenarios")
            if isinstance(scs, list):
                scenarios.extend([sc for sc in scs if isinstance(sc, dict)])

        changed, id_failures = _assign_seq_ids(
            feature_points,
            id_field="id",
            pattern=FP_ID_RE,
            prefix="FP",
            width=3,
            loc_prefix="$.modules[].feature_points",
        )
        modified = modified or changed
        failures.extend(id_failures)

        changed, id_failures = _assign_seq_ids(
            scenarios, id_field="id", pattern=SC_ID_RE, prefix="SC", width=2, loc_prefix="$.modules[].scenarios"
        )
        modified = modified or changed
        failures.extend(id_failures)

    rules_value = prd_pack.get("business_rules")
    if isinstance(rules_value, list):
        rules = [rule for rule in rules_value if isinstance(rule, dict)]
        changed, id_failures = _assign_seq_ids(
            rules, id_field="id", pattern=BR_ID_RE, prefix="BR", width=3, loc_prefix="$.business_rules"
        )
        modified = modified or changed
        failures.extend(id_failures)

    data_model = prd_pack.get("data_model")
    if isinstance(data_model, dict):
        tables_value = data_model.get("tables")
        if isinstance(tables_value, list):
            tables = [table for table in tables_value if isinstance(table, dict)]
            changed, id_failures = _assign_seq_ids(
                tables,
                id_field="id",
                pattern=TBL_ID_RE,
                prefix="TBL",
                width=3,
                loc_prefix="$.data_model.tables",
            )
            modified = modified or changed
            failures.extend(id_failures)

    api = prd_pack.get("api")
    if isinstance(api, dict):
        endpoints_value = api.get("endpoints")
        if isinstance(endpoints_value, list):
            endpoints = [endpoint for endpoint in endpoints_value if isinstance(endpoint, dict)]
            changed, id_failures = _assign_seq_ids(
                endpoints, id_field="id", pattern=API_ID_RE, prefix="API", width=3, loc_prefix="$.api.endpoints"
            )
            modified = modified or changed
            failures.extend(id_failures)

    return modified, failures
