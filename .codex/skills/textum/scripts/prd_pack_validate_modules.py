from __future__ import annotations

from typing import Any

from prd_pack_types import Failure
from prd_pack_validate_utils import (
    _build_table_index,
    _get_dict,
    _get_list,
    _require_str,
    _validate_landing_tokens,
)


def validate_data_model_and_modules(prd_pack: dict[str, Any], failures: list[Failure]) -> None:
    data_model = _get_dict(prd_pack.get("data_model"), "$.data_model", failures)
    table_index: dict[str, str] = {}
    if data_model is not None:
        table_index = _build_table_index(data_model, failures)

    modules = _get_list(prd_pack.get("modules"), "$.modules", failures)
    if modules is None:
        return

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

    module_ids: set[str] = set()
    module_names: set[str] = set()
    for module in modules:
        if not isinstance(module, dict):
            continue
        module_id = module.get("id")
        if isinstance(module_id, str) and module_id.strip() != "":
            module_ids.add(module_id.strip())
        module_name = module.get("name")
        if isinstance(module_name, str) and module_name.strip() != "":
            module_names.add(module_name.strip())

    has_p0 = False
    for index, module in enumerate(modules):
        module_loc = f"$.modules[{index}]"
        module_obj = _get_dict(module, module_loc, failures)
        if module_obj is None:
            continue

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

