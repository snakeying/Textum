from __future__ import annotations

from typing import Any

from prd_pack_types import Failure


def get_list(value: Any, loc: str, failures: list[Failure]) -> list[Any] | None:
    if isinstance(value, list):
        return value
    failures.append(
        Failure(
            loc=loc,
            problem=f"expected array, got {type(value).__name__}",
            expected="array",
            impact="cannot proceed",
            fix=f"rewrite {loc} as an array",
        )
    )
    return None


def get_dict(value: Any, loc: str, failures: list[Failure]) -> dict[str, Any] | None:
    if isinstance(value, dict):
        return value
    failures.append(
        Failure(
            loc=loc,
            problem=f"expected object, got {type(value).__name__}",
            expected="object",
            impact="cannot proceed",
            fix=f"rewrite {loc} as an object",
        )
    )
    return None


def require_str(value: Any, loc: str, failures: list[Failure]) -> str | None:
    if not isinstance(value, str):
        failures.append(
            Failure(
                loc=loc,
                problem=f"expected string, got {type(value).__name__}",
                expected="non-empty string",
                impact="cannot proceed",
                fix=f"set {loc} to a non-empty string",
            )
        )
        return None
    if value.strip() == "":
        failures.append(
            Failure(
                loc=loc,
                problem="empty string",
                expected="non-empty string",
                impact="cannot proceed",
                fix=f"fill {loc}",
            )
        )
        return None
    return value.strip()

