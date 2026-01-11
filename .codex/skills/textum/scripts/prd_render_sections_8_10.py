from __future__ import annotations

from typing import Any

from prd_pack import PLACEHOLDER_SENTINEL
from prd_render_utils import _as_lines, _as_text, _landing_to_prd_token, _md_table


def render_sections_8_10(ctx: dict[str, Any]) -> list[str]:
    modules: list[Any] = ctx["modules"]
    data_model: dict[str, Any] = ctx["data_model"]
    tables: list[Any] = ctx["tables"]
    table_name_to_id: dict[str, str] = ctx["table_name_to_id"]

    api: dict[str, Any] = ctx["api"]
    has_api: bool | None = ctx["has_api"]
    endpoints: list[Any] = ctx["endpoints"]

    nfr: list[Any] = ctx["nfr"]

    lines: list[str] = []

    lines.append("## 8. 数据模型（必填）")
    lines.append("")
    lines.append("### 8.0 功能点→落点映射（必填）")
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
    lines.append(_md_table(["FP", "落点", "说明"], mapping_rows))
    lines.append("")

    lines.append("### 8.1 表清单（可选）")
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
    lines.append(_md_table(["表ID", "表名", "用途", "主要字段（摘要）"], table_rows))
    lines.append("")

    lines.append("### 8.2 表定义（逐表填写，便于按 `TBL-###` 定位；无则写 N/A）")
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
            lines.append(f"**用途（必填，一句话）**: {_as_text(table.get('purpose'))}")
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
            lines.append(_md_table(["字段", "类型", "可空", "默认值", "约束/索引", "说明"], col_rows))
            lines.append("")

            lines.append("**关键约束（必填；无则写 N/A）**")
            constraints = table.get("constraints") if isinstance(table.get("constraints"), list) else []
            cons_rows: list[list[str]] = []
            for c_index, constraint in enumerate(constraints, start=1):
                if not isinstance(constraint, dict):
                    continue
                cid = _as_text(constraint.get("id")) if constraint.get("id") else f"CON-{c_index:02d}"
                cons_rows.append([cid, _as_text(constraint.get("constraint")), _as_text(constraint.get("note"))])
            lines.append(_md_table(["ID", "约束", "说明"], cons_rows))
            lines.append("")

            lines.append("**关键索引（必填；无则写 N/A）**")
            indexes = table.get("indexes") if isinstance(table.get("indexes"), list) else []
            idx_rows: list[list[str]] = []
            for i_index, idx in enumerate(indexes, start=1):
                if not isinstance(idx, dict):
                    continue
                iid = _as_text(idx.get("id")) if idx.get("id") else f"IDX-{i_index:02d}"
                idx_rows.append([iid, _as_text(idx.get("index")), _as_text(idx.get("purpose"))])
            lines.append(_md_table(["ID", "索引", "用途"], idx_rows))
            lines.append("")

    lines.append("### 8.3 表关系（可选；无则写 N/A）")
    lines.append(_as_text(data_model.get("relations")) if data_model.get("relations") else "N/A")
    lines.append("")

    lines.append("## 9. 接口设计（必填）")
    lines.append("")
    if has_api is False:
        lines.append("### 9.1 通用约定（必填）")
        lines.append("N/A")
        lines.append("")
        lines.append("### 9.2 接口清单（必填）")
        lines.append("N/A")
        lines.append("")
        lines.append("### 9.3 接口详情（逐个填写，便于按 `API-###` 定位）")
        lines.append("N/A")
        lines.append("")
    else:
        lines.append("### 9.1 通用约定（必填）")
        lines.append(f"- Base URL: {_as_text(api.get('base_url'))}")
        lines.append(f"- 认证方式: {_as_text(api.get('auth'))}")
        lines.append("- 权限校验: 按第 4 节权限矩阵执行")
        lines.append(f"- 分页/排序/筛选: {_as_text(api.get('pagination_sort_filter'))}")
        lines.append(f"- 响应包装: {_as_text(api.get('response_wrapper'))}")
        extra_error_codes = api.get("extra_error_codes") if isinstance(api.get("extra_error_codes"), list) else []
        lines.append(f"- 错误码: {', '.join(_as_lines(extra_error_codes)) or 'N/A'}")
        lines.append("")

        lines.append("### 9.2 接口清单（必填）")
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
        lines.append(_md_table(["接口ID", "名称", "方法", "路径", "模块", "权限", "说明"], endpoint_rows))
        lines.append("")

        lines.append("### 9.3 接口详情（逐个填写，便于按 `API-###` 定位）")
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
                lines.append(f"- 方法: {_as_text(endpoint.get('method'))}")
                lines.append(f"- 路径: {_as_text(endpoint.get('path'))}")
                lines.append(f"- 模块: {_as_text(endpoint.get('module_id'))}")
                lines.append(f"- 权限: {_as_text(endpoint.get('permission'))}")
                lines.append("")

                lines.append("**请求（必填；无则写 N/A）**")
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
                lines.append(_md_table(["位置", "字段", "类型", "必填", "约束", "说明"], req_rows))
                lines.append("")

                lines.append("**响应（必填；无则写 N/A）**")
                resp_rows: list[list[str]] = []
                response_fields = (
                    endpoint.get("response_fields") if isinstance(endpoint.get("response_fields"), list) else []
                )
                for resp in response_fields:
                    if not isinstance(resp, dict):
                        continue
                    resp_rows.append([_as_text(resp.get("field")), _as_text(resp.get("type")), _as_text(resp.get("note"))])
                lines.append(_md_table(["字段", "类型", "说明"], resp_rows))
                lines.append("")

                lines.append("**失败/边界（必填）**")
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
                lines.append(_md_table(["状态码", "触发条件", "对用户的提示（如有）"], fail_rows))
                lines.append("")

    lines.append("## 10. 非功能需求（必填，可写 N/A）")
    nfr_rows: list[list[str]] = []
    for item in nfr:
        if not isinstance(item, dict):
            continue
        nfr_rows.append(
            [_as_text(item.get("category")), _as_text(item.get("requirement")), _as_text(item.get("acceptance"))]
        )
    if nfr_rows:
        lines.append(_md_table(["类别", "需求", "验收口径"], nfr_rows))
    else:
        lines.append("N/A")
    lines.append("")

    return lines
