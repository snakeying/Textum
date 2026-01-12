from __future__ import annotations

from typing import Any


def build_prd_maps(prd_pack: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
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

    br_items = prd_pack.get("business_rules", [])
    br_by_id: dict[str, Any] = {}
    if isinstance(br_items, list):
        for item in br_items:
            if not isinstance(item, dict):
                continue
            item_id = item.get("id")
            if isinstance(item_id, str):
                br_by_id[item_id] = item

    return api_by_id, tbl_by_id, br_by_id


def scaffold_module_rows(scaffold_pack: dict[str, Any], *, module_ids: list[str]) -> list[dict[str, Any]]:
    extracted = scaffold_pack.get("extracted")
    if not isinstance(extracted, dict):
        return []
    modules = extracted.get("modules_index")
    if not isinstance(modules, list):
        return []

    wanted = set(module_ids)
    rows: list[dict[str, Any]] = []
    for item in modules:
        if not isinstance(item, dict):
            continue
        item_id = item.get("id")
        if not isinstance(item_id, str) or item_id not in wanted:
            continue
        rows.append(item)
    return rows

