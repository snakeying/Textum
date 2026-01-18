from __future__ import annotations

from typing import Any

from .prd_render_utils import _as_lines, _as_text, _md_table


def render_global_context_markdown_from_parts(parts: dict[str, Any]) -> str:
    project_line: str | None = parts.get("project_line")
    backend = parts.get("backend")
    frontend = parts.get("frontend")
    database = parts.get("database")
    other = parts.get("other")
    repo_rows = parts.get("repo_rows") or []
    cmd_table = parts.get("cmd_table")
    coding_conventions_text = parts.get("coding_conventions_text")
    enum_rows = parts.get("enum_rows") or []
    rule_rows = parts.get("rule_rows") or []
    perm_table = parts.get("perm_table") or []
    table_rows = parts.get("table_rows") or []
    relations = parts.get("relations")
    naming_text = parts.get("naming_text")
    api_conventions = parts.get("api_conventions") if isinstance(parts.get("api_conventions"), dict) else {}
    has_api = parts.get("has_api")
    nfr_rows = parts.get("nfr_rows") or []

    lines: list[str] = []
    lines.append("# GLOBAL CONTEXT")
    lines.append("")
    if project_line is not None:
        lines.append(project_line)
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
    lines.append(cmd_table)
    lines.append("")
    lines.append("### Coding Conventions (Optional; otherwise N/A)")
    lines.append("")
    lines.append(coding_conventions_text)
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
    lines.append(_md_table(["Operation", "Roles (A/D/O)", "Note"], perm_table))
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

