from __future__ import annotations

from typing import Any

from prd_render_utils import _as_lines, _as_text, _md_table


def render_sections_5_7(ctx: dict[str, Any], labels: dict[str, Any]) -> list[str]:
    sections = labels["sections"]
    tables = labels["tables"]
    blocks = labels["blocks"]
    none_text = labels["text"]["none"]

    modules: list[Any] = ctx["modules"]
    ui_routes: list[Any] = ctx["ui_routes"]
    business_rules: list[Any] = ctx["business_rules"]
    states_enums: dict[str, Any] = ctx["states_enums"]

    lines: list[str] = []

    lines.append(sections["5"])
    lines.append("")
    lines.append(sections["5.1"])
    module_rows: list[list[str]] = []
    for module in modules:
        if not isinstance(module, dict):
            continue
        deps = ", ".join(_as_lines(module.get("dependencies"))) or none_text
        module_rows.append(
            [
                _as_text(module.get("id")),
                _as_text(module.get("name")),
                _as_text(module.get("summary")),
                _as_text(module.get("priority")),
                deps,
            ]
        )
    lines.append(_md_table(tables["modules"], module_rows))
    lines.append("")

    lines.append(sections["5.2"])
    lines.append("")
    module_objects = [m for m in modules if isinstance(m, dict)]
    for index, module in enumerate(module_objects, start=1):
        module_id = _as_text(module.get("id"))
        module_name = _as_text(module.get("name"))
        lines.append(f"#### 5.2.{index} {module_id} {module_name}")
        lines.append(blocks["feature_points"])
        fp_rows: list[list[str]] = []
        fps = module.get("feature_points") if isinstance(module.get("feature_points"), list) else []
        for fp in fps:
            if not isinstance(fp, dict):
                continue
            fp_rows.append([_as_text(fp.get("id")), _as_text(fp.get("desc"))])
        lines.append(_md_table(tables["feature_points"], fp_rows))
        lines.append("")
        lines.append(blocks["scenarios"])
        sc_rows: list[list[str]] = []
        scenarios = module.get("scenarios") if isinstance(module.get("scenarios"), list) else []
        for sc in scenarios:
            if not isinstance(sc, dict):
                continue
            sc_rows.append(
                [
                    _as_text(sc.get("id")),
                    _as_text(sc.get("actor")),
                    _as_text(sc.get("given")),
                    _as_text(sc.get("when")),
                    _as_text(sc.get("then")),
                    _as_text(sc.get("fail_or_edge")),
                    _as_text(sc.get("note")),
                ]
            )
        lines.append(
            _md_table(
                tables["scenarios"],
                sc_rows,
            )
        )
        lines.append("")

    lines.append(sections["5.3"])
    route_rows: list[list[str]] = []
    for route in ui_routes:
        if not isinstance(route, dict):
            continue
        route_rows.append(
            [_as_text(route.get("route")), _as_text(route.get("description")), _as_text(route.get("module_id"))]
        )
    lines.append(_md_table(tables["routes"], route_rows))
    lines.append("")

    lines.append(sections["6"])
    lines.append("")
    rule_rows: list[list[str]] = []
    for rule in business_rules:
        if not isinstance(rule, dict):
            continue
        rule_rows.append(
            [
                _as_text(rule.get("id")),
                _as_text(rule.get("desc")),
                _as_text(rule.get("scope")),
                _as_text(rule.get("exception_or_note")),
            ]
        )
    lines.append(_md_table(tables["business_rules"], rule_rows))
    lines.append("")

    lines.append(sections["7"])
    lines.append("")
    lines.append(sections["7.1"])
    enum_rows: list[list[str]] = []
    enums = states_enums.get("enums") if isinstance(states_enums.get("enums"), list) else []
    for enum in enums:
        if not isinstance(enum, dict):
            continue
        values = ", ".join(_as_lines(enum.get("values"))) or "N/A"
        enum_rows.append(
            [_as_text(enum.get("field")), values, _as_text(enum.get("default")), _as_text(enum.get("note"))]
        )
    lines.append(_md_table(tables["enums"], enum_rows))
    lines.append("")

    lines.append(sections["7.2"])
    sm_rows: list[list[str]] = []
    state_machines = states_enums.get("state_machines") if isinstance(states_enums.get("state_machines"), list) else []
    for machine in state_machines:
        if not isinstance(machine, dict):
            continue
        entity = _as_text(machine.get("entity"))
        transitions = machine.get("transitions") if isinstance(machine.get("transitions"), list) else []
        for transition in transitions:
            if not isinstance(transition, dict):
                continue
            note = _as_text(transition.get("note"))
            note = f"entity={entity}; {note}" if entity != "N/A" else note
            sm_rows.append(
                [
                    _as_text(transition.get("state")),
                    _as_text(transition.get("event")),
                    _as_text(transition.get("next_state")),
                    _as_text(transition.get("permission_or_condition")),
                    note,
                ]
            )
    lines.append(_md_table(tables["state_machines"], sm_rows))
    lines.append("")

    lines.append(sections["7.3"])
    lines.append(_as_text(states_enums.get("naming_conventions")) if states_enums.get("naming_conventions") else "N/A")
    lines.append("")

    return lines
