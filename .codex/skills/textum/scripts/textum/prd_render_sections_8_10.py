from __future__ import annotations

from typing import Any

from .prd_pack import PLACEHOLDER_SENTINEL
from .prd_render_utils import _as_lines, _as_text, _landing_to_prd_token, _md_table


def render_sections_8_10(ctx: dict[str, Any], labels: dict[str, Any]) -> list[str]:
    sections = labels["sections"]
    tables_h = labels["tables"]
    blocks = labels["blocks"]
    api_labels = labels["api"]
    table_labels = labels["table"]

    modules: list[Any] = ctx["modules"]
    data_model: dict[str, Any] = ctx["data_model"]
    tables: list[Any] = ctx["tables"]
    table_name_to_id: dict[str, str] = ctx["table_name_to_id"]

    api: dict[str, Any] = ctx["api"]
    has_api: bool | None = ctx["has_api"]
    endpoints: list[Any] = ctx["endpoints"]

    nfr: list[Any] = ctx["nfr"]

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

    lines.append(sections["9"])
    lines.append("")
    if has_api is False:
        lines.append(sections["9.1"])
        lines.append("N/A")
        lines.append("")
        lines.append(sections["9.2"])
        lines.append("N/A")
        lines.append("")
        lines.append(sections["9.3"])
        lines.append("N/A")
        lines.append("")
    else:
        lines.append(sections["9.1"])
        lines.append(f"- Base URL: {_as_text(api.get('base_url'))}")
        lines.append(f"- {api_labels['auth']}: {_as_text(api.get('auth'))}")
        lines.append(f"- {api_labels['authorization']}: {api_labels['authorization_note']}")
        lines.append(f"- {api_labels['pagination']}: {_as_text(api.get('pagination_sort_filter'))}")
        lines.append(f"- {api_labels['response_wrapper']}: {_as_text(api.get('response_wrapper'))}")
        extra_error_codes = api.get("extra_error_codes") if isinstance(api.get("extra_error_codes"), list) else []
        lines.append(f"- {api_labels['error_codes']}: {', '.join(_as_lines(extra_error_codes)) or 'N/A'}")
        lines.append("")

        lines.append(sections["9.2"])
        endpoint_rows: list[list[str]] = []
        for endpoint in endpoints:
            if not isinstance(endpoint, dict):
                continue
            endpoint_rows.append(
                [
                    _as_text(endpoint.get("id")),
                    _as_text(endpoint.get("name")),
                    _as_text(endpoint.get("method")),
                    _as_text(endpoint.get("path")),
                    _as_text(endpoint.get("module_id")),
                    _as_text(endpoint.get("permission")),
                    _as_text(endpoint.get("summary")),
                ]
            )
        lines.append(_md_table(tables_h["endpoints"], endpoint_rows))
        lines.append("")

        lines.append(sections["9.3"])
        if not endpoint_rows:
            lines.append("N/A")
            lines.append("")
        else:
            endpoint_objects = [e for e in endpoints if isinstance(e, dict)]
            for index, endpoint in enumerate(endpoint_objects, start=1):
                api_id = _as_text(endpoint.get("id"))
                name = _as_text(endpoint.get("name"))
                anchor = f" <!-- PRD#{api_id} -->" if api_id != "N/A" else ""
                lines.append(f"#### 9.3.{index} {api_id} {name}{anchor}")
                lines.append(f"- {api_labels['method']}: {_as_text(endpoint.get('method'))}")
                lines.append(f"- {api_labels['path']}: {_as_text(endpoint.get('path'))}")
                lines.append(f"- {api_labels['module']}: {_as_text(endpoint.get('module_id'))}")
                lines.append(f"- {api_labels['permission']}: {_as_text(endpoint.get('permission'))}")
                lines.append("")

                lines.append(blocks["request"])
                req_rows: list[list[str]] = []
                request_fields = endpoint.get("request_fields") if isinstance(endpoint.get("request_fields"), list) else []
                for req in request_fields:
                    if not isinstance(req, dict):
                        continue
                    req_rows.append(
                        [
                            _as_text(req.get("location")),
                            _as_text(req.get("field")),
                            _as_text(req.get("type")),
                            "Y" if req.get("required") is True else "N",
                            _as_text(req.get("constraints")),
                            _as_text(req.get("note")),
                        ]
                    )
                lines.append(_md_table(tables_h["request_fields"], req_rows))
                lines.append("")

                lines.append(blocks["response"])
                resp_rows: list[list[str]] = []
                response_fields = (
                    endpoint.get("response_fields") if isinstance(endpoint.get("response_fields"), list) else []
                )
                for resp in response_fields:
                    if not isinstance(resp, dict):
                        continue
                    resp_rows.append([_as_text(resp.get("field")), _as_text(resp.get("type")), _as_text(resp.get("note"))])
                lines.append(_md_table(tables_h["response_fields"], resp_rows))
                lines.append("")

                lines.append(blocks["failure"])
                fail_rows: list[list[str]] = []
                failure_cases = endpoint.get("failure_cases") if isinstance(endpoint.get("failure_cases"), list) else []
                for failure in failure_cases:
                    if not isinstance(failure, dict):
                        continue
                    fail_rows.append(
                        [
                            _as_text(failure.get("status_code")),
                            _as_text(failure.get("condition")),
                            _as_text(failure.get("user_message")),
                        ]
                    )
                lines.append(_md_table(tables_h["failure_cases"], fail_rows))
                lines.append("")

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

