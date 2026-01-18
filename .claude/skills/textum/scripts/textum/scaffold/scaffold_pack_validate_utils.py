from __future__ import annotations

from typing import Any

from textum.prd.prd_pack_types import Failure


def require_str(value: Any, loc: str, failures: list[Failure], *, allow_na: bool = False) -> str | None:
    if not isinstance(value, str):
        failures.append(
            Failure(
                loc=loc,
                problem=f"expected string, got {type(value).__name__}",
                expected="non-empty string",
                impact="scaffold pack is incomplete",
                fix=f"set {loc} to a non-empty string",
            )
        )
        return None
    stripped = value.strip()
    if stripped == "":
        failures.append(
            Failure(
                loc=loc,
                problem="empty string",
                expected="non-empty string",
                impact="scaffold pack is incomplete",
                fix=f"fill {loc}",
            )
        )
        return None
    if not allow_na and stripped.upper() == "N/A":
        failures.append(
            Failure(
                loc=loc,
                problem="N/A not allowed here",
                expected="a concrete value",
                impact="scaffold pack is incomplete",
                fix=f"replace N/A at {loc}",
            )
        )
        return None
    return stripped

