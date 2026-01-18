from __future__ import annotations

from typing import Any

from .prd_render_utils import _as_lines, _as_text, _md_table


def render_section_9(ctx: dict[str, Any], labels: dict[str, Any]) -> list[str]:
    sections = labels["sections"]
    tables_h = labels["tables"]
    blocks = labels["blocks"]
    api_labels = labels["api"]

    api: dict[str, Any] = ctx["api"]
    has_api: bool | None = ctx["has_api"]
    endpoints: list[Any] = ctx["endpoints"]

    lines: list[str] = []
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
        return lines

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
        return lines

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
        response_fields = endpoint.get("response_fields") if isinstance(endpoint.get("response_fields"), list) else []
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

    return lines

