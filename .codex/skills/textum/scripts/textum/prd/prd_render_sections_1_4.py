from __future__ import annotations

from typing import Any

from .prd_render_utils import _as_lines, _as_text, _md_table


def render_sections_1_4(ctx: dict[str, Any], labels: dict[str, Any]) -> list[str]:
    sections = labels["sections"]
    tables = labels["tables"]

    one_liner: str = ctx["one_liner"]
    goals: list[str] = ctx["goals"]
    non_goals: list[str] = ctx["non_goals"]

    scope_in: list[str] = ctx["scope_in"]
    scope_out: list[str] = ctx["scope_out"]

    assumptions_constraints: list[Any] = ctx["assumptions_constraints"]
    roles: list[Any] = ctx["roles"]
    permission_ops: list[Any] = ctx["permission_ops"]

    lines: list[str] = []

    lines.append(sections["1"])
    lines.append("")
    lines.append(sections["1.1"])
    lines.append(one_liner)
    lines.append("")
    lines.append(sections["1.2"])
    if goals:
        for index, goal in enumerate(goals, start=1):
            lines.append(f"- G-{index:02d}: {goal}")
    else:
        lines.append("N/A")
    lines.append("")
    lines.append(sections["1.3"])
    if non_goals:
        for index, non_goal in enumerate(non_goals, start=1):
            lines.append(f"- NG-{index:02d}: {non_goal}")
    else:
        lines.append("N/A")
    lines.append("")

    lines.append(sections["2"])
    lines.append("")
    lines.append(sections["2.1"])
    if scope_in:
        for index, item in enumerate(scope_in, start=1):
            lines.append(f"- S-{index:02d}: {item}")
    else:
        lines.append("N/A")
    lines.append("")
    lines.append(sections["2.2"])
    if scope_out:
        for index, item in enumerate(scope_out, start=1):
            lines.append(f"- OS-{index:02d}: {item}")
    else:
        lines.append("N/A")
    lines.append("")
    lines.append(sections["2.3"])
    assumption_rows: list[list[str]] = []
    for index, item in enumerate(assumptions_constraints, start=1):
        if not isinstance(item, dict):
            continue
        assumption_rows.append(
            [f"A-{index:02d}", _as_text(item.get("assumption_or_constraint")), _as_text(item.get("impact"))]
        )
    lines.append(_md_table(tables["assumptions"], assumption_rows))
    lines.append("")

    lines.append(sections["3"])
    lines.append("")
    lines.append(sections["3.1"])
    role_rows: list[list[str]] = []
    for role in roles:
        if not isinstance(role, dict):
            continue
        typical = "<br>".join(_as_lines(role.get("typical_scenarios"))) or "N/A"
        role_rows.append([_as_text(role.get("role")), _as_text(role.get("description")), typical])
    lines.append(_md_table(tables["roles"], role_rows))
    lines.append("")

    lines.append(sections["4"])
    lines.append("")
    perm_rows: list[list[str]] = []

    role_names: list[str] = []
    role_name_set: set[str] = set()
    for role in roles:
        if not isinstance(role, dict):
            continue
        role_value = role.get("role")
        if not isinstance(role_value, str) or not role_value.strip():
            continue
        role_name = _as_text(role_value)
        if role_name == "N/A" or role_name in role_name_set:
            continue
        role_names.append(role_name)
        role_name_set.add(role_name)

    for op in permission_ops:
        if not isinstance(op, dict):
            continue
        op_name = _as_text(op.get("op"))
        note = _as_text(op.get("note"))
        per_role = op.get("per_role") if isinstance(op.get("per_role"), dict) else {}

        pairs: list[str] = []
        if role_names:
            for role_name in role_names:
                perm_value = per_role.get(role_name)
                perm = perm_value.strip() if isinstance(perm_value, str) and perm_value.strip() else "N/A"
                pairs.append(f"{role_name}={perm}")

            for role_name, perm_value in per_role.items():
                if not isinstance(role_name, str) or role_name in role_name_set:
                    continue
                perm = perm_value.strip() if isinstance(perm_value, str) and perm_value.strip() else "N/A"
                pairs.append(f"{role_name}={perm}")
        else:
            for role_name, perm_value in per_role.items():
                if not isinstance(role_name, str):
                    continue
                perm = perm_value.strip() if isinstance(perm_value, str) and perm_value.strip() else "N/A"
                pairs.append(f"{role_name}={perm}")

        perm_text = "<br>".join(pairs) if pairs else "N/A"
        perm_rows.append([op_name, perm_text, note])
    lines.append(_md_table(tables["permission_matrix"], perm_rows))
    lines.append("")

    return lines

