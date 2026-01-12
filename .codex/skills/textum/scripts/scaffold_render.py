from __future__ import annotations

from typing import Any

from prd_render_utils import _as_lines, _as_text, _md_table


def _as_list_of_str(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [v.strip() for v in value if isinstance(v, str) and v.strip()]


def render_global_context_markdown(scaffold_pack: dict[str, Any]) -> str:
    decisions = scaffold_pack.get("decisions") if isinstance(scaffold_pack.get("decisions"), dict) else {}
    extracted = scaffold_pack.get("extracted") if isinstance(scaffold_pack.get("extracted"), dict) else {}

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

    commands = (
        decisions.get("validation_commands") if isinstance(decisions.get("validation_commands"), list) else []
    )
    cmd_rows: list[list[str]] = []
    for item in commands:
        if not isinstance(item, dict):
            continue
        cmd_rows.append([_as_text(item.get("type")), _as_text(item.get("command")), _as_text(item.get("note"))])

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
    perm_table: list[list[str]] = []
    for row in perm_rows:
        if not isinstance(row, dict):
            continue
        perm_table.append(
            [_as_text(row.get("op")), _as_text(row.get("role")), _as_text(row.get("permission")), _as_text(row.get("note"))]
        )

    data_model_overview = (
        extracted.get("data_model_overview") if isinstance(extracted.get("data_model_overview"), dict) else {}
    )
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

    lines: list[str] = []
    lines.append("# GLOBAL CONTEXT")
    lines.append("")

    lines.append("## 1. Tech Stack (Required)")
    lines.append("")
    lines.append(_md_table(["Layer", "Choice"], [["Backend", backend], ["Frontend", frontend], ["Database", database], ["Other", other]]))
    lines.append("")

    lines.append("## 2. Repository Structure (Required)")
    lines.append("")
    lines.append(_md_table(["Path", "Purpose"], repo_rows))
    lines.append("")
    lines.append("### Verification Commands (Optional; otherwise N/A)")
    lines.append("")
    lines.append(_md_table(["Type", "Command", "Note"], cmd_rows))
    lines.append("")

    lines.append("## 3. Enums (Optional; otherwise N/A)")
    lines.append("")
    lines.append(_md_table(["Field", "Values", "Default", "Note"], enum_rows))
    lines.append("")

    lines.append("## 4. Business Rules (Required)")
    lines.append("")
    lines.append(_md_table(["ID", "Rule"], rule_rows))
    lines.append("")

    lines.append("## 5. Permission Matrix (Required)")
    lines.append("")
    lines.append(_md_table(["Operation", "Role", "Permission", "Note"], perm_table))
    lines.append("")

    lines.append("## 6. Data Model Overview (Required; N/A if no DB)")
    lines.append("")
    lines.append(_md_table(["Table ID", "Table", "Purpose", "Key Fields"], table_rows))
    lines.append("")
    lines.append(f"Relations: {relations}")
    lines.append("")

    lines.append("## 7. Naming Conventions (Optional; otherwise N/A)")
    lines.append("")
    lines.append(naming_text)
    lines.append("")

    lines.append("## 8. API Conventions (Required)")
    lines.append("")
    if has_api is False:
        lines.append("N/A")
        lines.append("")
    elif has_api is True:
        lines.append(f"- Base URL: {_as_text(api_conventions.get('base_url'))}")
        lines.append(f"- Authentication: {_as_text(api_conventions.get('auth'))}")
        lines.append(f"- Pagination/Sort/Filter: {_as_text(api_conventions.get('pagination_sort_filter'))}")
        lines.append(f"- Response Wrapper: {_as_text(api_conventions.get('response_wrapper'))}")
        extra_error_codes = api_conventions.get("extra_error_codes")
        lines.append(f"- Error Codes: {', '.join(_as_lines(extra_error_codes)) or 'N/A'}")
        lines.append("")
    else:
        lines.append("N/A")
        lines.append("")

    lines.append("## 9. Non-functional Requirements (Optional; otherwise N/A)")
    lines.append("")
    lines.append(_md_table(["Category", "Requirement", "Acceptance"], nfr_rows))
    lines.append("")

    return "\n".join(lines)

