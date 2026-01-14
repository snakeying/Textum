from __future__ import annotations

from typing import Any

from prd_pack_types import Failure
from prd_pack_validate_utils import _get_dict, _get_list, _require_str


def validate_roles_and_permission_matrix(prd_pack: dict[str, Any], failures: list[Failure]) -> None:
    roles = _get_list(prd_pack.get("roles"), "$.roles", failures)
    role_names: list[str] = []
    if roles is not None:
        if len(roles) == 0:
            failures.append(
                Failure(
                    loc="$.roles",
                    problem="roles is empty",
                    expected="at least 1 role",
                    impact="permissions and scenarios cannot be validated",
                    fix="add at least one role to roles[]",
                )
            )
        for index, role in enumerate(roles):
            role_loc = f"$.roles[{index}]"
            role_obj = _get_dict(role, role_loc, failures)
            if role_obj is None:
                continue
            role_name = role_obj.get("role")
            _require_str(role_name, f"{role_loc}.role", failures)
            if isinstance(role_name, str) and role_name.strip() != "":
                role_names.append(role_name.strip())
            _require_str(role_obj.get("description"), f"{role_loc}.description", failures)
            typical = _get_list(role_obj.get("typical_scenarios"), f"{role_loc}.typical_scenarios", failures)
            if typical is not None and len(typical) == 0:
                failures.append(
                    Failure(
                        loc=f"{role_loc}.typical_scenarios",
                        problem="typical_scenarios is empty",
                        expected="at least 1 scenario",
                        impact="role definition is incomplete",
                        fix=f"add at least one item to {role_loc}.typical_scenarios[]",
                    )
                )

    permission_matrix = _get_dict(prd_pack.get("permission_matrix"), "$.permission_matrix", failures)
    if permission_matrix is None:
        return

    operations = _get_list(permission_matrix.get("operations"), "$.permission_matrix.operations", failures)
    if operations is not None and len(operations) == 0:
        failures.append(
            Failure(
                loc="$.permission_matrix.operations",
                problem="operations is empty",
                expected="at least 1 operation",
                impact="permissions cannot be validated",
                fix="add at least one operation to permission_matrix.operations[]",
            )
        )
    if operations is None:
        return

    for index, operation in enumerate(operations):
        op_loc = f"$.permission_matrix.operations[{index}]"
        op_obj = _get_dict(operation, op_loc, failures)
        if op_obj is None:
            continue
        _require_str(op_obj.get("op"), f"{op_loc}.op", failures)
        per_role = _get_dict(op_obj.get("per_role"), f"{op_loc}.per_role", failures)
        if per_role is None:
            continue
        if len(per_role) == 0:
            failures.append(
                Failure(
                    loc=f"{op_loc}.per_role",
                    problem="per_role is empty",
                    expected="at least 1 role permission",
                    impact="permission matrix row is incomplete",
                    fix=f"add at least one role key to {op_loc}.per_role",
                )
            )
        for role_name, perm in per_role.items():
            if role_names and role_name not in role_names:
                failures.append(
                    Failure(
                        loc=f"{op_loc}.per_role.{role_name}",
                        problem=f"unknown role: {role_name}",
                        expected="role key must exist in roles[].role",
                        impact="permission matrix is inconsistent",
                        fix="rename role key to match roles[].role",
                    )
                )
            if perm not in ("A", "D", "O"):
                failures.append(
                    Failure(
                        loc=f"{op_loc}.per_role.{role_name}",
                        problem=f"invalid permission: {perm!r}",
                        expected="A/D/O",
                        impact="permission matrix is invalid",
                        fix=f"set {op_loc}.per_role.{role_name} to one of A/D/O",
                    )
                )
