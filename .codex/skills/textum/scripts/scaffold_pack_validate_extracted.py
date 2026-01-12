from __future__ import annotations

from typing import Any

from prd_pack_types import Failure


def validate_extracted(scaffold_pack: dict[str, Any], failures: list[Failure]) -> None:
    extracted = scaffold_pack.get("extracted")
    if not isinstance(extracted, dict):
        failures.append(
            Failure(
                loc="$.extracted",
                problem=f"expected object, got {type(extracted).__name__}",
                expected="object",
                impact="extracted PRD context is missing",
                fix="run: textum scaffold check (it auto-populates extracted)",
            )
        )

