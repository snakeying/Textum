from __future__ import annotations

from typing import Any

from textum.prd.prd_pack_types import Failure, MODULE_ID_RE


def validate_extracted(scaffold_pack: dict[str, Any], failures: list[Failure]) -> None:
    extracted = scaffold_pack.get("extracted")
    if not isinstance(extracted, dict):
        failures.append(
            Failure(
                loc="$.extracted",
                problem=f"expected object, got {type(extracted).__name__}",
                expected="object",
                impact="extracted PRD context is missing",
                fix="populate docs/scaffold-pack.json:$.extracted",
            )
        )
        return

    modules_index = extracted.get("modules_index")
    if not isinstance(modules_index, list):
        failures.append(
            Failure(
                loc="$.extracted.modules_index",
                problem=f"expected array, got {type(modules_index).__name__}",
                expected="array of PRD modules with ids like M-01",
                impact="cannot validate story modules against scaffold",
                fix="refresh docs/scaffold-pack.json:$.extracted.modules_index",
            )
        )
        return

    has_valid_id = False
    for index, module in enumerate(modules_index):
        if not isinstance(module, dict):
            continue
        mid = module.get("id")
        if isinstance(mid, str) and MODULE_ID_RE.match(mid):
            has_valid_id = True
        elif isinstance(mid, str) and mid.strip():
            failures.append(
                Failure(
                    loc=f"$.extracted.modules_index[{index}].id",
                    problem=f"invalid module id: {mid!r}",
                    expected="M-01",
                    impact="stories cannot reference modules reliably",
                    fix="refresh docs/scaffold-pack.json:$.extracted.modules_index",
                )
            )

    if not has_valid_id:
        failures.append(
            Failure(
                loc="$.extracted.modules_index",
                problem="modules_index is empty/unusable",
                expected="at least 1 module with id like M-01",
                impact="cannot validate story modules against scaffold",
                fix="refresh docs/scaffold-pack.json:$.extracted.modules_index",
            )
        )

