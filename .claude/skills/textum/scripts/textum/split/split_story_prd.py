from __future__ import annotations

from typing import Any

from textum.prd.prd_pack_types import API_ID_RE, FP_ID_RE, MODULE_ID_RE, TBL_ID_RE


def build_table_indices(prd_pack: dict[str, Any]) -> tuple[dict[str, str], dict[str, dict[str, Any]]]:
    name_to_id: dict[str, str] = {}
    by_id: dict[str, dict[str, Any]] = {}
    data_model = prd_pack.get("data_model") if isinstance(prd_pack.get("data_model"), dict) else {}
    tables = data_model.get("tables") if isinstance(data_model.get("tables"), list) else []
    for table in tables:
        if not isinstance(table, dict):
            continue
        table_id = table.get("id")
        name = table.get("name")
        if not (isinstance(table_id, str) and TBL_ID_RE.match(table_id)):
            continue
        if not (isinstance(name, str) and name.strip() != ""):
            continue
        name_to_id[name] = table_id
        by_id[table_id] = table
    return name_to_id, by_id


def extract_modules_by_id(prd_pack: dict[str, Any]) -> dict[str, dict[str, Any]]:
    modules_by_id: dict[str, dict[str, Any]] = {}
    modules = prd_pack.get("modules") if isinstance(prd_pack.get("modules"), list) else []
    for module in modules:
        if not isinstance(module, dict):
            continue
        module_id = module.get("id")
        if isinstance(module_id, str) and MODULE_ID_RE.match(module_id):
            modules_by_id[module_id] = module
    return modules_by_id


def extract_api_endpoints_by_id(prd_pack: dict[str, Any]) -> dict[str, dict[str, Any]]:
    api = prd_pack.get("api") if isinstance(prd_pack.get("api"), dict) else {}
    endpoints = api.get("endpoints") if isinstance(api.get("endpoints"), list) else []
    by_id: dict[str, dict[str, Any]] = {}
    for endpoint in endpoints:
        if not isinstance(endpoint, dict):
            continue
        endpoint_id = endpoint.get("id")
        if isinstance(endpoint_id, str) and API_ID_RE.match(endpoint_id):
            by_id[endpoint_id] = endpoint
    return by_id


def sorted_feature_points(module_obj: dict[str, Any]) -> list[dict[str, Any]]:
    fps = module_obj.get("feature_points") if isinstance(module_obj.get("feature_points"), list) else []
    result: list[dict[str, Any]] = []
    for fp in fps:
        if not isinstance(fp, dict):
            continue
        fid = fp.get("id")
        if isinstance(fid, str) and FP_ID_RE.match(fid):
            result.append(fp)
    result.sort(key=lambda x: x.get("id", ""))
    return result


