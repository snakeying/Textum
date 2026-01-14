from __future__ import annotations

from typing import Any

from prd_pack_types import Failure
from prd_pack_validate_utils import _get_list


def _collect_module_ids(prd_pack: dict[str, Any]) -> set[str]:
    modules_value = prd_pack.get("modules")
    if not isinstance(modules_value, list):
        return set()
    module_ids: set[str] = set()
    for module in modules_value:
        if not isinstance(module, dict):
            continue
        module_id = module.get("id")
        if isinstance(module_id, str) and module_id.strip() != "":
            module_ids.add(module_id.strip())
    return module_ids


def _examples_summary(examples: list[str], *, limit: int = 8) -> str:
    if len(examples) <= limit:
        return ", ".join(examples)
    shown = examples[:limit]
    remaining = len(examples) - limit
    return ", ".join(shown) + f", ... (+{remaining} more)"


def validate_internal_refs(prd_pack: dict[str, Any], failures: list[Failure]) -> None:
    module_ids = _collect_module_ids(prd_pack)
    if not module_ids:
        return

    ui_routes = _get_list(prd_pack.get("ui_routes"), "$.ui_routes", failures)
    if ui_routes is not None:
        bad: list[str] = []
        for idx, item in enumerate(ui_routes):
            if not isinstance(item, dict):
                continue
            module_id_value = item.get("module_id")
            if module_id_value is None:
                continue
            loc = f"$.ui_routes[{idx}].module_id"
            if not isinstance(module_id_value, str):
                bad.append(f"{loc}={module_id_value!r}")
                continue
            module_id = module_id_value.strip()
            if module_id == "":
                continue
            if module_id not in module_ids:
                bad.append(f"{loc}={module_id_value!r}")
        if bad:
            failures.append(
                Failure(
                    loc="$.ui_routes[].module_id",
                    problem=f"invalid module_id refs ({len(bad)}): {_examples_summary(bad)}",
                    expected="null or an existing module id in $.modules[].id",
                    impact="ui_routes cannot be mapped to modules",
                    fix="set invalid ui_routes[].module_id to null",
                )
            )

    api = prd_pack.get("api")
    if not isinstance(api, dict):
        return
    if api.get("has_api") is not True:
        return
    endpoints_value = api.get("endpoints")
    if not isinstance(endpoints_value, list):
        return

    bad_endpoints: list[str] = []
    for idx, item in enumerate(endpoints_value):
        if not isinstance(item, dict):
            continue
        module_id_value = item.get("module_id")
        if module_id_value is None:
            continue
        loc = f"$.api.endpoints[{idx}].module_id"
        if not isinstance(module_id_value, str):
            bad_endpoints.append(f"{loc}={module_id_value!r}")
            continue
        module_id = module_id_value.strip()
        if module_id == "":
            continue
        if module_id not in module_ids:
            bad_endpoints.append(f"{loc}={module_id_value!r}")
    if bad_endpoints:
        failures.append(
            Failure(
                loc="$.api.endpoints[].module_id",
                problem=f"invalid module_id refs ({len(bad_endpoints)}): {_examples_summary(bad_endpoints)}",
                expected="null or an existing module id in $.modules[].id",
                impact="api endpoints cannot be mapped to modules",
                fix="set invalid api.endpoints[].module_id to null",
            )
        )
