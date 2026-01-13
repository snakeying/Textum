from __future__ import annotations

from typing import Any


def _extract_project(prd_pack: dict[str, Any]) -> dict[str, Any]:
    project_obj = prd_pack.get("project") if isinstance(prd_pack.get("project"), dict) else {}
    return {
        "name": project_obj.get("name") if isinstance(project_obj.get("name"), str) else None,
        "one_liner": project_obj.get("one_liner") if isinstance(project_obj.get("one_liner"), str) else None,
    }


def _extract_modules_index(prd_pack: dict[str, Any]) -> list[dict[str, Any]]:
    modules_index: list[dict[str, Any]] = []
    modules = prd_pack.get("modules") if isinstance(prd_pack.get("modules"), list) else []
    for module in modules:
        if not isinstance(module, dict):
            continue
        modules_index.append(
            {
                "id": module.get("id") if isinstance(module.get("id"), str) else None,
                "name": module.get("name") if isinstance(module.get("name"), str) else None,
                "summary": module.get("summary") if isinstance(module.get("summary"), str) else None,
                "priority": module.get("priority") if isinstance(module.get("priority"), str) else None,
                "dependencies": (
                    [d for d in module.get("dependencies") if isinstance(d, str)]
                    if isinstance(module.get("dependencies"), list)
                    else []
                ),
            }
        )
    return modules_index


def _extract_states_enums(prd_pack: dict[str, Any]) -> dict[str, Any]:
    states_enums = prd_pack.get("states_enums") if isinstance(prd_pack.get("states_enums"), dict) else {}
    return states_enums


def _extract_naming_conventions(states_enums: dict[str, Any]) -> str | None:
    return (
        states_enums.get("naming_conventions") if isinstance(states_enums.get("naming_conventions"), str) else None
    )


def _extract_enums(states_enums: dict[str, Any]) -> list[dict[str, Any]]:
    enums: list[dict[str, Any]] = []
    enum_items = states_enums.get("enums") if isinstance(states_enums.get("enums"), list) else []
    for enum in enum_items:
        if not isinstance(enum, dict):
            continue
        enums.append(
            {
                "field": enum.get("field") if isinstance(enum.get("field"), str) else None,
                "values": [v for v in enum.get("values") if isinstance(v, str)] if isinstance(enum.get("values"), list) else [],
                "default": enum.get("default") if isinstance(enum.get("default"), str) else None,
                "note": enum.get("note") if isinstance(enum.get("note"), str) else None,
            }
        )
    return enums


def _extract_business_rules(prd_pack: dict[str, Any]) -> list[dict[str, Any]]:
    business_rules: list[dict[str, Any]] = []
    rule_items = prd_pack.get("business_rules") if isinstance(prd_pack.get("business_rules"), list) else []
    for rule in rule_items:
        if not isinstance(rule, dict):
            continue
        business_rules.append(
            {
                "id": rule.get("id") if isinstance(rule.get("id"), str) else None,
                "desc": rule.get("desc") if isinstance(rule.get("desc"), str) else None,
                "scope": rule.get("scope") if isinstance(rule.get("scope"), str) else None,
                "exception_or_note": (
                    rule.get("exception_or_note") if isinstance(rule.get("exception_or_note"), str) else None
                ),
            }
        )
    return business_rules


def _extract_permission_matrix_rows(prd_pack: dict[str, Any]) -> list[dict[str, Any]]:
    permission_rows: list[dict[str, Any]] = []
    permission_matrix = (
        prd_pack.get("permission_matrix") if isinstance(prd_pack.get("permission_matrix"), dict) else {}
    )
    operations = permission_matrix.get("operations") if isinstance(permission_matrix.get("operations"), list) else []
    for op in operations:
        if not isinstance(op, dict):
            continue
        op_name = op.get("op") if isinstance(op.get("op"), str) else None
        note = op.get("note") if isinstance(op.get("note"), str) else None
        per_role = op.get("per_role") if isinstance(op.get("per_role"), dict) else {}
        for role_name, perm in per_role.items():
            if not isinstance(role_name, str):
                continue
            if not isinstance(perm, str):
                continue
            permission_rows.append(
                {
                    "op": op_name,
                    "role": role_name,
                    "permission": perm,
                    "note": note,
                }
            )
    return permission_rows


def _extract_data_model_overview(prd_pack: dict[str, Any]) -> dict[str, Any]:
    data_model = prd_pack.get("data_model") if isinstance(prd_pack.get("data_model"), dict) else {}
    tables = data_model.get("tables") if isinstance(data_model.get("tables"), list) else []
    table_list: list[dict[str, Any]] = []
    for table in tables:
        if not isinstance(table, dict):
            continue
        table_list.append(
            {
                "id": table.get("id") if isinstance(table.get("id"), str) else None,
                "name": table.get("name") if isinstance(table.get("name"), str) else None,
                "purpose": table.get("purpose") if isinstance(table.get("purpose"), str) else None,
                "fields_summary": table.get("fields_summary") if isinstance(table.get("fields_summary"), str) else None,
            }
        )
    relations = data_model.get("relations") if isinstance(data_model.get("relations"), str) else None
    return {"tables": table_list, "relations": relations}


def _extract_api_conventions(prd_pack: dict[str, Any]) -> dict[str, Any]:
    api = prd_pack.get("api") if isinstance(prd_pack.get("api"), dict) else {}
    has_api = api.get("has_api") if isinstance(api.get("has_api"), bool) else None
    api_conventions: dict[str, Any] = {"has_api": has_api}
    if has_api is True:
        api_conventions.update(
            {
                "base_url": api.get("base_url") if isinstance(api.get("base_url"), str) else None,
                "auth": api.get("auth") if isinstance(api.get("auth"), str) else None,
                "pagination_sort_filter": (
                    api.get("pagination_sort_filter") if isinstance(api.get("pagination_sort_filter"), str) else None
                ),
                "response_wrapper": api.get("response_wrapper") if isinstance(api.get("response_wrapper"), str) else None,
                "extra_error_codes": (
                    [c for c in api.get("extra_error_codes") if isinstance(c, str)]
                    if isinstance(api.get("extra_error_codes"), list)
                    else []
                ),
            }
        )
    return api_conventions


def _extract_nfr(prd_pack: dict[str, Any]) -> list[dict[str, Any]]:
    nfr = prd_pack.get("nfr") if isinstance(prd_pack.get("nfr"), list) else []
    nfr_items: list[dict[str, Any]] = []
    for item in nfr:
        if not isinstance(item, dict):
            continue
        nfr_items.append(
            {
                "category": item.get("category") if isinstance(item.get("category"), str) else None,
                "requirement": item.get("requirement") if isinstance(item.get("requirement"), str) else None,
                "acceptance": item.get("acceptance") if isinstance(item.get("acceptance"), str) else None,
            }
        )
    return nfr_items


def extract_from_prd_pack(prd_pack: dict[str, Any]) -> dict[str, Any]:
    project = _extract_project(prd_pack)
    modules_index = _extract_modules_index(prd_pack)

    states_enums = _extract_states_enums(prd_pack)
    naming_conventions = _extract_naming_conventions(states_enums)
    enums = _extract_enums(states_enums)

    business_rules = _extract_business_rules(prd_pack)
    permission_rows = _extract_permission_matrix_rows(prd_pack)
    data_model_overview = _extract_data_model_overview(prd_pack)
    api_conventions = _extract_api_conventions(prd_pack)
    nfr_items = _extract_nfr(prd_pack)

    return {
        "project": project,
        "modules_index": modules_index,
        "enums": enums,
        "business_rules": business_rules,
        "permission_matrix_rows": permission_rows,
        "data_model_overview": data_model_overview,
        "naming_conventions": naming_conventions,
        "api_conventions": api_conventions,
        "nfr": nfr_items,
    }
