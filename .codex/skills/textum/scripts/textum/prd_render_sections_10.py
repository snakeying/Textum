from __future__ import annotations

from typing import Any

from .prd_render_utils import _as_text, _md_table


def render_section_10(ctx: dict[str, Any], labels: dict[str, Any]) -> list[str]:
    sections = labels["sections"]
    tables_h = labels["tables"]

    nfr: list[Any] = ctx["nfr"]

    lines: list[str] = []
    lines.append(sections["10"])
    nfr_rows: list[list[str]] = []
    for item in nfr:
        if not isinstance(item, dict):
            continue
        nfr_rows.append(
            [_as_text(item.get("category")), _as_text(item.get("requirement")), _as_text(item.get("acceptance"))]
        )
    if nfr_rows:
        lines.append(_md_table(tables_h["nfr"], nfr_rows))
    else:
        lines.append("N/A")
    lines.append("")
    return lines

