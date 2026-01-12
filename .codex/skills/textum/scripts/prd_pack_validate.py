from __future__ import annotations

from typing import Any

from prd_pack_placeholders import collect_placeholders
from prd_pack_types import Failure
from prd_pack_validate_access import validate_roles_and_permission_matrix
from prd_pack_validate_modules import validate_data_model_and_modules
from prd_pack_validate_project import validate_project_and_scope
from prd_pack_validate_rules_api import validate_business_rules_and_api


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

    validate_project_and_scope(prd_pack, failures)
    validate_roles_and_permission_matrix(prd_pack, failures)
    validate_data_model_and_modules(prd_pack, failures)
    validate_business_rules_and_api(prd_pack, failures)

    return failures


def check_prd_pack(prd_pack: dict[str, Any]) -> tuple[bool, list[Failure]]:
    failures = collect_placeholders(prd_pack) + validate_prd_pack(prd_pack)
    return (len(failures) == 0), failures
