from __future__ import annotations

from typing import Any

from textum.prd.prd_render_utils import _as_lines, _as_text, _md_table


def _as_list_of_str(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [v.strip() for v in value if isinstance(v, str) and v.strip()]


def extract_global_context_parts(scaffold_pack: dict[str, Any]) -> dict[str, Any]:
    decisions = scaffold_pack.get("decisions") if isinstance(scaffold_pack.get("decisions"), dict) else {}
    extracted = scaffold_pack.get("extracted") if isinstance(scaffold_pack.get("extracted"), dict) else {}

    project = extracted.get("project") if isinstance(extracted.get("project"), dict) else {}
    project_name = _as_text(project.get("name"))
    project_one_liner = _as_text(project.get("one_liner"))
    project_line: str | None = None
    if project_name != "N/A" and project_one_liner != "N/A":
        project_line = f"Project: {project_name} бк {project_one_liner}"
    elif project_name != "N/A":
        project_line = f"Project: {project_name}"
    elif project_one_liner != "N/A":
        project_line = f"Project: {project_one_liner}"

    tech_stack = decisions.get("tech_stack") if isinstance(decisions.get("tech_stack"), dict) else {}
    backend = _as_text(tech_stack.get("backend"))
    frontend = _as_text(tech_stack.get("frontend"))
    database = _as_text(tech_stack.get("database"))
    other = ", ".join(_as_list_of_str(tech_stack.get("other"))) or "N/A"

    repo_structure = decisions.get("repo_structure") if isinstance(decisions.get("repo_structure"), list) else []
    repo_rows: list[list[str]] = []
    for item in repo_structure:
        if not isinstance(item, dict):
            continue
        repo_rows.append([_as_text(item.get("path")), _as_text(item.get("purpose"))])

    commands = decisions.get("validation_commands") if isinstance(decisions.get("validation_commands"), list) else []
    cmd_rows_raw: list[list[str]] = []
    for item in commands:
        if not isinstance(item, dict):
            continue
        cmd_rows_raw.append([_as_text(item.get("type")), _as_text(item.get("command")), _as_text(item.get("note"))])

    gate_cmd_rows: list[list[str]] = []
    opt_cmd_rows: list[list[str]] = []
    other_cmd_rows: list[list[str]] = []
    na_cmd_rows: list[list[str]] = []
    for row in cmd_rows_raw:
        typ = row[0]
        if typ.startswith("gate:"):
            gate_cmd_rows.append(row)
        elif typ.startswith("opt:"):
            opt_cmd_rows.append(row)
        elif typ.upper() == "N/A":
            na_cmd_rows.append(row)
        else:
            other_cmd_rows.append(row)
    cmd_rows = gate_cmd_rows + opt_cmd_rows + other_cmd_rows + na_cmd_rows
    cmd_table = "N/A"
    if cmd_rows:
        is_single_all_na = len(cmd_rows) == 1 and all(cell.upper() == "N/A" for cell in cmd_rows[0])
        if not is_single_all_na:
            cmd_table = _md_table(["Type", "Command", "Note"], cmd_rows)

    coding_conventions_text = _as_text(decisions.get("coding_conventions"))

    enums = extracted.get("enums") if isinstance(extracted.get("enums"), list) else []
    enum_rows: list[list[str]] = []
    for enum in enums:
        if not isinstance(enum, dict):
            continue
        values = ", ".join(_as_lines(enum.get("values"))) or "N/A"
        enum_rows.append([_as_text(enum.get("field")), values, _as_text(enum.get("default")), _as_text(enum.get("note"))])

    business_rules = extracted.get("business_rules") if isinstance(extracted.get("business_rules"), list) else []
    rule_rows: list[list[str]] = []
    for rule in business_rules:
        if not isinstance(rule, dict):
            continue
        rule_rows.append([_as_text(rule.get("id")), _as_text(rule.get("desc"))])

    perm_rows = extracted.get("permission_matrix_rows") if isinstance(extracted.get("permission_matrix_rows"), list) else []
    perm_ops: dict[str, dict[str, Any]] = {}
    perm_op_order: list[str] = []
    for row in perm_rows:
        if not isinstance(row, dict):
            continue

        op = _as_text(row.get("op"))
        if op not in perm_ops:
            perm_ops[op] = {"A": [], "D": [], "O": [], "notes": []}
            perm_op_order.append(op)

        entry = perm_ops[op]
        role = _as_text(row.get("role"))
        permission = _as_text(row.get("permission")).upper()
        if permission in ("A", "D", "O") and role != "N/A":
            entry[permission].append(role)

        note = _as_text(row.get("note"))
        if note != "N/A" and note not in entry["notes"]:
            entry["notes"].append(note)

    perm_table: list[list[str]] = []
    for op in perm_op_order:
        entry = perm_ops[op]
        parts: list[str] = []
        for code in ("A", "D", "O"):
            roles = entry[code]
            if roles:
                parts.append(f"{code}: {', '.join(roles)}")
        roles_cell = "<br>".join(parts) or "N/A"
        note_cell = "<br>".join(entry["notes"]) if entry["notes"] else "N/A"
        perm_table.append([op, roles_cell, note_cell])

    data_model_overview = extracted.get("data_model_overview") if isinstance(extracted.get("data_model_overview"), dict) else {}
    tables = data_model_overview.get("tables") if isinstance(data_model_overview.get("tables"), list) else []
    table_rows: list[list[str]] = []
    for table in tables:
        if not isinstance(table, dict):
            continue
        table_rows.append(
            [
                _as_text(table.get("id")),
                _as_text(table.get("name")),
                _as_text(table.get("purpose")),
                _as_text(table.get("fields_summary")),
            ]
        )
    relations = _as_text(data_model_overview.get("relations")) if data_model_overview.get("relations") else "N/A"

    naming_conventions = extracted.get("naming_conventions")
    naming_text = _as_text(naming_conventions) if naming_conventions else "N/A"

    api_conventions = extracted.get("api_conventions") if isinstance(extracted.get("api_conventions"), dict) else {}
    has_api = api_conventions.get("has_api") if isinstance(api_conventions.get("has_api"), bool) else None

    nfr = extracted.get("nfr") if isinstance(extracted.get("nfr"), list) else []
    nfr_rows: list[list[str]] = []
    for item in nfr:
        if not isinstance(item, dict):
            continue
        nfr_rows.append([_as_text(item.get("category")), _as_text(item.get("requirement")), _as_text(item.get("acceptance"))])

    return {
        "project_line": project_line,
        "backend": backend,
        "frontend": frontend,
        "database": database,
        "other": other,
        "repo_rows": repo_rows,
        "cmd_table": cmd_table,
        "coding_conventions_text": coding_conventions_text,
        "enum_rows": enum_rows,
        "rule_rows": rule_rows,
        "perm_table": perm_table,
        "table_rows": table_rows,
        "relations": relations,
        "naming_text": naming_text,
        "api_conventions": api_conventions,
        "has_api": has_api,
        "nfr_rows": nfr_rows,
    }
