from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .prd_pack_types import API_ID_RE, BR_ID_RE, FP_ID_RE, MODULE_ID_RE, TBL_ID_RE


@dataclass
class PrdRefSets:
    p0_modules: set[str]
    fp_ids: set[str]
    tbl_ids: set[str]
    br_ids: set[str]
    api_ids: set[str]
    has_api: bool


def extract_prd_ref_sets(prd_pack: dict[str, Any]) -> PrdRefSets:
    prd_modules = prd_pack.get("modules") if isinstance(prd_pack.get("modules"), list) else []
    p0_modules: set[str] = set()
    fp_ids: set[str] = set()

    for module in prd_modules:
        if not isinstance(module, dict):
            continue
        mid = module.get("id")
        if isinstance(mid, str) and MODULE_ID_RE.match(mid):
            if module.get("priority") == "P0":
                p0_modules.add(mid)
        fps = module.get("feature_points") if isinstance(module.get("feature_points"), list) else []
        for fp in fps:
            if not isinstance(fp, dict):
                continue
            fid = fp.get("id")
            if isinstance(fid, str) and FP_ID_RE.match(fid):
                fp_ids.add(fid)

    tbl_ids: set[str] = set()
    data_model = prd_pack.get("data_model") if isinstance(prd_pack.get("data_model"), dict) else {}
    tables = data_model.get("tables") if isinstance(data_model.get("tables"), list) else []
    for table in tables:
        if not isinstance(table, dict):
            continue
        tid = table.get("id")
        if isinstance(tid, str) and TBL_ID_RE.match(tid):
            tbl_ids.add(tid)

    br_ids: set[str] = set()
    rules = prd_pack.get("business_rules") if isinstance(prd_pack.get("business_rules"), list) else []
    for rule in rules:
        if not isinstance(rule, dict):
            continue
        rid = rule.get("id")
        if isinstance(rid, str) and BR_ID_RE.match(rid):
            br_ids.add(rid)

    api_ids: set[str] = set()
    api = prd_pack.get("api") if isinstance(prd_pack.get("api"), dict) else {}
    has_api = api.get("has_api") is True
    endpoints = api.get("endpoints") if isinstance(api.get("endpoints"), list) else []
    for endpoint in endpoints:
        if not isinstance(endpoint, dict):
            continue
        eid = endpoint.get("id")
        if isinstance(eid, str) and API_ID_RE.match(eid):
            api_ids.add(eid)

    return PrdRefSets(
        p0_modules=p0_modules,
        fp_ids=fp_ids,
        tbl_ids=tbl_ids,
        br_ids=br_ids,
        api_ids=api_ids,
        has_api=has_api,
    )


