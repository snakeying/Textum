from __future__ import annotations

from typing import Any

from .prd_pack import PLACEHOLDER_SENTINEL, TBL_ID_RE


def _as_text(value: Any) -> str:
    if not isinstance(value, str):
        return "N/A"
    stripped = value.strip()
    if stripped == "" or PLACEHOLDER_SENTINEL in stripped:
        return "N/A"
    return stripped


def _as_lines(values: Any) -> list[str]:
    if not isinstance(values, list):
        return []
    lines: list[str] = []
    for value in values:
        if not isinstance(value, str):
            continue
        stripped = value.strip()
        if stripped and PLACEHOLDER_SENTINEL not in stripped:
            lines.append(stripped)
    return lines


def _md_table(headers: list[str], rows: list[list[str]]) -> str:
    if not rows:
        return "N/A"
    header_line = "| " + " | ".join(headers) + " |"
    sep_line = "| " + " | ".join(["---"] * len(headers)) + " |"
    lines = [header_line, sep_line]
    for row in rows:
        padded = row + ["N/A"] * (len(headers) - len(row))
        lines.append("| " + " | ".join([cell if cell.strip() else "N/A" for cell in padded]) + " |")
    return "\n".join(lines)


def _landing_to_prd_token(token: str, table_name_to_id: dict[str, str]) -> str:
    stripped = token.strip()
    if stripped.upper() == "N/A":
        return "N/A"
    if not stripped.startswith("DB:"):
        return stripped
    table_ref = stripped.removeprefix("DB:").strip()
    if table_ref == "":
        return stripped
    if TBL_ID_RE.match(table_ref):
        return f"DB:{table_ref}"
    mapped = table_name_to_id.get(table_ref)
    return f"DB:{mapped}" if mapped else stripped

