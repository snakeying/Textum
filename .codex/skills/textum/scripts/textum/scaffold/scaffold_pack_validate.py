from __future__ import annotations

from typing import Any

from .prd_pack_types import Failure
from .scaffold_pack_placeholders import collect_placeholders
from .scaffold_pack_validate_decisions import validate_decisions
from .scaffold_pack_validate_extracted import validate_extracted


def validate_scaffold_pack(scaffold_pack: dict[str, Any]) -> list[Failure]:
    failures: list[Failure] = []

    if scaffold_pack.get("schema_version") != "scaffold-pack@v1":
        failures.append(
            Failure(
                loc="$.schema_version",
                problem=f"unexpected schema_version: {scaffold_pack.get('schema_version')!r}",
                expected="'scaffold-pack@v1'",
                impact="schema mismatch",
                fix="set schema_version to 'scaffold-pack@v1'",
            )
        )
        return failures

    failures.extend(collect_placeholders(scaffold_pack))

    decisions = scaffold_pack.get("decisions")
    if not isinstance(decisions, dict):
        failures.append(
            Failure(
                loc="$.decisions",
                problem=f"expected object, got {type(decisions).__name__}",
                expected="object",
                impact="scaffold decisions are missing",
                fix="set decisions to an object",
            )
        )
        return failures

    validate_decisions(decisions, failures)
    validate_extracted(scaffold_pack, failures)

    return failures


def check_scaffold_pack(scaffold_pack: dict[str, Any]) -> tuple[bool, list[Failure]]:
    failures = validate_scaffold_pack(scaffold_pack)
    return (len(failures) == 0), failures

