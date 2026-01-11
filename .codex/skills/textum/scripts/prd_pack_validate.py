from __future__ import annotations

from typing import Any

from prd_pack_placeholders import collect_placeholders
from prd_pack_types import Failure
from prd_pack_validate_utils import (
    _build_table_index,
    _get_dict,
    _get_list,
    _require_str,
    _validate_landing_tokens,
)


def validate_prd_pack(prd_pack: dict[str, Any]) -> list[Failure]:
    failures: list[Failure] = []

    if prd_pack.get("schema_version") != "prd-pack@v1":
        failures.append(
            Failure(
                loc="$.schema_version",
                problem=f"unexpected schema_version: {prd_pack.get('schema_version')!r}",
                expected="'prd-pack@v1'",
                impact="schema mismatch",
                fix="set schema_version to 'prd-pack@v1'",
            )
        )
        return failures

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
    if scope is not None:
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
    if permission_matrix is not None:
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
        if operations is not None:
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
                                fix=f"set {op_loc}.per_role.{role_name} to A, D, or O",
                            )
                        )

    data_model = _get_dict(prd_pack.get("data_model"), "$.data_model", failures)
    table_index: dict[str, str] = {}
    if data_model is not None:
        table_index = _build_table_index(data_model, failures)

    modules = _get_list(prd_pack.get("modules"), "$.modules", failures)
    module_ids: list[str] = []
    module_names: list[str] = []
    has_p0 = False
    if modules is not None:
        if len(modules) == 0:
            failures.append(
                Failure(
                    loc="$.modules",
                    problem="modules is empty",
                    expected="at least 1 module",
                    impact="PRD has no functional scope",
                    fix="add at least one module to modules[]",
                )
            )
        for index, module in enumerate(modules):
            module_loc = f"$.modules[{index}]"
            module_obj = _get_dict(module, module_loc, failures)
            if module_obj is None:
                continue
            module_id = module_obj.get("id")
            if isinstance(module_id, str) and module_id.strip() != "":
                module_ids.append(module_id.strip())
            module_name = module_obj.get("name")
            if isinstance(module_name, str) and module_name.strip() != "":
                module_names.append(module_name.strip())
            _require_str(module_obj.get("name"), f"{module_loc}.name", failures)
            _require_str(module_obj.get("summary"), f"{module_loc}.summary", failures)
            priority = module_obj.get("priority")
            _require_str(priority, f"{module_loc}.priority", failures)
            if isinstance(priority, str) and priority.strip() == "P0":
                has_p0 = True

            dependencies = _get_list(module_obj.get("dependencies"), f"{module_loc}.dependencies", failures)
            if dependencies is not None:
                for dep_index, dependency in enumerate(dependencies):
                    dep_loc = f"{module_loc}.dependencies[{dep_index}]"
                    if not isinstance(dependency, str) or dependency.strip() == "":
                        failures.append(
                            Failure(
                                loc=dep_loc,
                                problem="dependency must be non-empty string",
                                expected="module id or name",
                                impact="dependency graph is invalid",
                                fix=f"set {dep_loc} to a module id or name",
                            )
                        )
                        continue
                    dep = dependency.strip()
                    if dep not in module_ids and dep not in module_names:
                        failures.append(
                            Failure(
                                loc=dep_loc,
                                problem=f"unknown module dependency: {dep}",
                                expected="existing module id or name",
                                impact="dependency graph is invalid",
                                fix="use a valid module id/name from modules[]",
                            )
                        )

            fps = _get_list(module_obj.get("feature_points"), f"{module_loc}.feature_points", failures)
            if fps is not None:
                if len(fps) == 0:
                    failures.append(
                        Failure(
                            loc=f"{module_loc}.feature_points",
                            problem="feature_points is empty",
                            expected="at least 1 feature point",
                            impact="PRD cannot be split later",
                            fix=f"add at least one feature point to {module_loc}.feature_points[]",
                        )
                    )
                for fp_index, fp in enumerate(fps):
                    fp_loc = f"{module_loc}.feature_points[{fp_index}]"
                    fp_obj = _get_dict(fp, fp_loc, failures)
                    if fp_obj is None:
                        continue
                    _require_str(fp_obj.get("desc"), f"{fp_loc}.desc", failures)
                    landing = _get_list(fp_obj.get("landing"), f"{fp_loc}.landing", failures)
                    if landing is not None:
                        _validate_landing_tokens(landing, f"{fp_loc}.landing", failures, table_index)

            scenarios = _get_list(module_obj.get("scenarios"), f"{module_loc}.scenarios", failures)
            if scenarios is not None:
                if len(scenarios) == 0:
                    failures.append(
                        Failure(
                            loc=f"{module_loc}.scenarios",
                            problem="scenarios is empty",
                            expected="at least 1 scenario",
                            impact="acceptance criteria is missing",
                            fix=f"add at least one scenario to {module_loc}.scenarios[]",
                        )
                    )
                for sc_index, scenario in enumerate(scenarios):
                    sc_loc = f"{module_loc}.scenarios[{sc_index}]"
                    sc_obj = _get_dict(scenario, sc_loc, failures)
                    if sc_obj is None:
                        continue
                    _require_str(sc_obj.get("actor"), f"{sc_loc}.actor", failures)
                    _require_str(sc_obj.get("given"), f"{sc_loc}.given", failures)
                    _require_str(sc_obj.get("when"), f"{sc_loc}.when", failures)
                    _require_str(sc_obj.get("then"), f"{sc_loc}.then", failures)

    if modules is not None and not has_p0:
        failures.append(
            Failure(
                loc="$.modules",
                problem="no P0 module found",
                expected="at least one module with priority 'P0'",
                impact="cannot identify minimal deliverable scope",
                fix="set at least one module priority to 'P0'",
            )
        )

    rules = _get_list(prd_pack.get("business_rules"), "$.business_rules", failures)
    if rules is not None and len(rules) == 0:
        failures.append(
            Failure(
                loc="$.business_rules",
                problem="business_rules is empty",
                expected="at least 1 business rule",
                impact="critical constraints are missing",
                fix="add at least one business rule to business_rules[]",
            )
        )

    api = _get_dict(prd_pack.get("api"), "$.api", failures)
    if api is not None:
        has_api = api.get("has_api")
        if not isinstance(has_api, bool):
            failures.append(
                Failure(
                    loc="$.api.has_api",
                    problem=f"has_api must be boolean, got {type(has_api).__name__}",
                    expected="true or false",
                    impact="API rules cannot be applied",
                    fix="set api.has_api to true or false",
                )
            )
        endpoints = _get_list(api.get("endpoints"), "$.api.endpoints", failures)
        if isinstance(has_api, bool) and endpoints is not None:
            if has_api is False:
                if len(endpoints) != 0:
                    failures.append(
                        Failure(
                            loc="$.api.endpoints",
                            problem="has_api is false but endpoints is not empty",
                            expected="[]",
                            impact="API section is contradictory",
                            fix="set api.endpoints to []",
                        )
                    )
            else:
                _require_str(api.get("base_url"), "$.api.base_url", failures, allow_na=False)
                _require_str(api.get("auth"), "$.api.auth", failures, allow_na=False)
                if len(endpoints) == 0:
                    failures.append(
                        Failure(
                            loc="$.api.endpoints",
                            problem="endpoints is empty",
                            expected="at least 1 endpoint when has_api=true",
                            impact="API section is incomplete",
                            fix="add at least one endpoint to api.endpoints[]",
                        )
                    )
                for index, endpoint in enumerate(endpoints):
                    endpoint_loc = f"$.api.endpoints[{index}]"
                    endpoint_obj = _get_dict(endpoint, endpoint_loc, failures)
                    if endpoint_obj is None:
                        continue
                    _require_str(endpoint_obj.get("name"), f"{endpoint_loc}.name", failures)
                    _require_str(endpoint_obj.get("method"), f"{endpoint_loc}.method", failures)
                    _require_str(endpoint_obj.get("path"), f"{endpoint_loc}.path", failures)
                    _require_str(endpoint_obj.get("permission"), f"{endpoint_loc}.permission", failures)

    return failures


def check_prd_pack(prd_pack: dict[str, Any]) -> tuple[bool, list[Failure]]:
    failures = collect_placeholders(prd_pack) + validate_prd_pack(prd_pack)
    return (len(failures) == 0), failures
