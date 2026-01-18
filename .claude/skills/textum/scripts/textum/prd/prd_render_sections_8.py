from __future__ import annotations

from typing import Any

from .prd_pack import PLACEHOLDER_SENTINEL
from .prd_render_utils import _as_text, _landing_to_prd_token, _md_table


def render_section_8(ctx: dict[str, Any], labels: dict[str, Any]) -> list[str]:
    sections = labels["sections"]
    tables_h = labels["tables"]
    blocks = labels["blocks"]
    table_labels = labels["table"]

    modules: list[Any] = ctx["modules"]
    data_model: dict[str, Any] = ctx["data_model"]
    tables: list[Any] = ctx["tables"]
    table_name_to_id: dict[str, str] = ctx["table_name_to_id"]

    lines: list[str] = []

    lines.append(sections["8"])
    lines.append("")
    lines.append(sections["8.0"])
    mapping_rows: list[list[str]] = []
    module_objects = [m for m in modules if isinstance(m, dict)]
    for module in module_objects:
        fps = module.get("feature_points") if isinstance(module.get("feature_points"), list) else []
        for fp in fps:
            if not isinstance(fp, dict):
                continue
            landing_tokens = fp.get("landing") if isinstance(fp.get("landing"), list) else []
            landing_text = ", ".join(
                [
                    _landing_to_prd_token(t, table_name_to_id)
                    for t in landing_tokens
                    if isinstance(t, str) and t.strip() and PLACEHOLDER_SENTINEL not in t
                ]
            ) or "N/A"
            mapping_rows.append([_as_text(fp.get("id")), landing_text, "N/A"])
    lines.append(_md_table(tables_h["fp_landing"], mapping_rows))
    lines.append("")

    lines.append(sections["8.1"])
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
    lines.append(_md_table(tables_h["table_list"], table_rows))
    lines.append("")

    lines.append(sections["8.2"])
    if not table_rows:
        lines.append("N/A")
        lines.append("")
    else:
        table_objects = [t for t in tables if isinstance(t, dict)]
        for index, table in enumerate(table_objects, start=1):
            table_id = _as_text(table.get("id"))
            name = _as_text(table.get("name"))
            anchor = f" <!-- PRD#{table_id} -->" if table_id != "N/A" else ""
            lines.append(f"#### 8.2.{index} {table_id} {name}{anchor}")
            lines.append(f"{table_labels['purpose_one_liner']}: {_as_text(table.get('purpose'))}")
            lines.append("")
            col_rows: list[list[str]] = []
            columns = table.get("columns") if isinstance(table.get("columns"), list) else []
            for column in columns:
                if not isinstance(column, dict):
                    continue
                col_rows.append(
                    [
                        _as_text(column.get("name")),
                        _as_text(column.get("type")),
                        "Y" if column.get("nullable") is True else "N",
                        _as_text(column.get("default")),
                        _as_text(column.get("constraints_or_indexes")),
                        _as_text(column.get("note")),
                    ]
                )
            lines.append(_md_table(tables_h["table_columns"], col_rows))
            lines.append("")

            lines.append(blocks["table_constraints"])
            constraints = table.get("constraints") if isinstance(table.get("constraints"), list) else []
            cons_rows: list[list[str]] = []
            for c_index, constraint in enumerate(constraints, start=1):
                if not isinstance(constraint, dict):
                    continue
                cid = _as_text(constraint.get("id")) if constraint.get("id") else f"CON-{c_index:02d}"
                cons_rows.append([cid, _as_text(constraint.get("constraint")), _as_text(constraint.get("note"))])
            lines.append(_md_table(tables_h["table_constraints"], cons_rows))
            lines.append("")

            lines.append(blocks["table_indexes"])
            indexes = table.get("indexes") if isinstance(table.get("indexes"), list) else []
            idx_rows: list[list[str]] = []
            for i_index, idx in enumerate(indexes, start=1):
                if not isinstance(idx, dict):
                    continue
                iid = _as_text(idx.get("id")) if idx.get("id") else f"IDX-{i_index:02d}"
                idx_rows.append([iid, _as_text(idx.get("index")), _as_text(idx.get("purpose"))])
            lines.append(_md_table(tables_h["table_indexes"], idx_rows))
            lines.append("")

    lines.append(sections["8.3"])
    lines.append(_as_text(data_model.get("relations")) if data_model.get("relations") else "N/A")
    lines.append("")

    return lines

