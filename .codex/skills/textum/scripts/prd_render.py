from __future__ import annotations

from typing import Any

from prd_render_sections_1_4 import render_sections_1_4
from prd_render_sections_5_7 import render_sections_5_7
from prd_render_sections_8_10 import render_sections_8_10
from prd_render_i18n import prd_render_labels, resolve_render_lang
from prd_render_utils import _as_lines, _as_text


def _extract_context(prd_pack: dict[str, Any]) -> dict[str, Any]:
    project = prd_pack.get("project") if isinstance(prd_pack.get("project"), dict) else {}
    one_liner = _as_text(project.get("one_liner"))

    goals = _as_lines(prd_pack.get("goals"))
    non_goals = _as_lines(prd_pack.get("non_goals"))

    scope = prd_pack.get("scope") if isinstance(prd_pack.get("scope"), dict) else {}
    scope_in = _as_lines(scope.get("in"))
    scope_out = _as_lines(scope.get("out"))

    assumptions_constraints = (
        prd_pack.get("assumptions_constraints") if isinstance(prd_pack.get("assumptions_constraints"), list) else []
    )
    roles = prd_pack.get("roles") if isinstance(prd_pack.get("roles"), list) else []
    permission_matrix = (
        prd_pack.get("permission_matrix") if isinstance(prd_pack.get("permission_matrix"), dict) else {}
    )
    permission_ops = (
        permission_matrix.get("operations") if isinstance(permission_matrix.get("operations"), list) else []
    )
    modules = prd_pack.get("modules") if isinstance(prd_pack.get("modules"), list) else []
    ui_routes = prd_pack.get("ui_routes") if isinstance(prd_pack.get("ui_routes"), list) else []
    business_rules = prd_pack.get("business_rules") if isinstance(prd_pack.get("business_rules"), list) else []
    states_enums = prd_pack.get("states_enums") if isinstance(prd_pack.get("states_enums"), dict) else {}

    data_model = prd_pack.get("data_model") if isinstance(prd_pack.get("data_model"), dict) else {}
    tables = data_model.get("tables") if isinstance(data_model.get("tables"), list) else []

    table_name_to_id: dict[str, str] = {}
    for table in tables:
        if not isinstance(table, dict):
            continue
        name = table.get("name")
        table_id = table.get("id")
        if isinstance(name, str) and isinstance(table_id, str) and name.strip() and table_id.strip():
            table_name_to_id[name.strip()] = table_id.strip()

    api = prd_pack.get("api") if isinstance(prd_pack.get("api"), dict) else {}
    has_api = api.get("has_api") if isinstance(api.get("has_api"), bool) else None
    endpoints = api.get("endpoints") if isinstance(api.get("endpoints"), list) else []

    nfr = prd_pack.get("nfr") if isinstance(prd_pack.get("nfr"), list) else []

    return {
        "one_liner": one_liner,
        "goals": goals,
        "non_goals": non_goals,
        "scope_in": scope_in,
        "scope_out": scope_out,
        "assumptions_constraints": assumptions_constraints,
        "roles": roles,
        "permission_ops": permission_ops,
        "modules": modules,
        "ui_routes": ui_routes,
        "business_rules": business_rules,
        "states_enums": states_enums,
        "data_model": data_model,
        "tables": tables,
        "table_name_to_id": table_name_to_id,
        "api": api,
        "has_api": has_api,
        "endpoints": endpoints,
        "nfr": nfr,
    }


def render_prd_markdown(prd_pack: dict[str, Any], *, lang: str = "auto") -> str:
    resolved_lang = resolve_render_lang(lang, prd_pack)
    labels = prd_render_labels(resolved_lang)
    ctx = _extract_context(prd_pack)

    lines: list[str] = []
    lines.append("# PRD")
    lines.append("")
    lines.extend(render_sections_1_4(ctx, labels))
    lines.extend(render_sections_5_7(ctx, labels))
    lines.extend(render_sections_8_10(ctx, labels))
    return "\n".join(lines)
