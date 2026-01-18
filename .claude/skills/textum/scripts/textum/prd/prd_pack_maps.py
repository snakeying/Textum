from __future__ import annotations

from typing import Any


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

