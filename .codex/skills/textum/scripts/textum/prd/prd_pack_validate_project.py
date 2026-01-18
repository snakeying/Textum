from __future__ import annotations

from typing import Any

from .prd_pack_types import Failure
from .prd_pack_validate_utils import _get_dict, _get_list, _require_str


def validate_project_and_scope(prd_pack: dict[str, Any], failures: list[Failure]) -> None:
    project = _get_dict(prd_pack.get("project"), "$.project", failures)
    if project is not None:
        _require_str(project.get("name"), "$.project.name", failures)
        _require_str(project.get("one_liner"), "$.project.one_liner", failures)

    goals = _get_list(prd_pack.get("goals"), "$.goals", failures)
    if goals is not None and len(goals) == 0:
        failures.append(
            Failure(
                loc="$.goals",
                problem="goals is empty",
                expected="at least 1 goal",
                impact="PRD lacks goals",
                fix="add at least one item to goals[]",
            )
        )

    non_goals = _get_list(prd_pack.get("non_goals"), "$.non_goals", failures)
    if non_goals is not None and len(non_goals) == 0:
        failures.append(
            Failure(
                loc="$.non_goals",
                problem="non_goals is empty",
                expected="at least 1 non-goal",
                impact="PRD lacks boundaries",
                fix="add at least one item to non_goals[]",
            )
        )

    scope = _get_dict(prd_pack.get("scope"), "$.scope", failures)
    if scope is None:
        return

    in_scope = _get_list(scope.get("in"), "$.scope.in", failures)
    out_scope = _get_list(scope.get("out"), "$.scope.out", failures)
    if in_scope is not None and len(in_scope) == 0:
        failures.append(
            Failure(
                loc="$.scope.in",
                problem="scope.in is empty",
                expected="at least 1 in-scope item",
                impact="PRD scope is unclear",
                fix="add at least one item to scope.in[]",
            )
        )
    if out_scope is not None and len(out_scope) == 0:
        failures.append(
            Failure(
                loc="$.scope.out",
                problem="scope.out is empty",
                expected="at least 1 out-of-scope item",
                impact="PRD scope is unclear",
                fix="add at least one item to scope.out[]",
            )
        )


