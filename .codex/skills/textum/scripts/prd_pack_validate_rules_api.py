from __future__ import annotations

from typing import Any

from prd_pack_types import Failure
from prd_pack_validate_utils import _get_dict, _get_list, _require_str


def validate_business_rules_and_api(prd_pack: dict[str, Any], failures: list[Failure]) -> None:
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
    if api is None:
        return

    has_api = api.get("has_api")
    if not isinstance(has_api, bool):
        failures.append(
            Failure(
                loc="$.api.has_api",
                problem=f"has_api must be boolean, got {type(has_api).__name__}",
                expected="true or false",
                impact="API rules cannot be applied",
                fix="set api.has_api to a boolean value",
            )
        )

    endpoints = _get_list(api.get("endpoints"), "$.api.endpoints", failures)
    if not (isinstance(has_api, bool) and endpoints is not None):
        return

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
        return

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
