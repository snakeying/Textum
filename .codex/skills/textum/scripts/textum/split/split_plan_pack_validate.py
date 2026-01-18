from __future__ import annotations

from typing import Any

from textum.prd.prd_pack_types import Failure, MODULE_ID_RE
from .split_pack_placeholders import collect_placeholders
from .split_plan_pack_normalize import normalize_split_plan_pack
from .split_plan_pack_validate_api import validate_api_assignments
from .split_plan_pack_validate_stories import validate_stories_and_module_coverage
from .split_plan_pack_validate_utils import get_list


def validate_split_plan_pack(
    split_plan_pack: dict[str, Any], *, prd_pack: dict[str, Any], strict: bool
) -> tuple[list[Failure], list[Failure]]:
    failures: list[Failure] = []
    warnings: list[Failure] = []

    if split_plan_pack.get("schema_version") != "split-plan-pack@v1":
        failures.append(
            Failure(
                loc="$.schema_version",
                problem=f"unexpected schema_version: {split_plan_pack.get('schema_version')!r}",
                expected="'split-plan-pack@v1'",
                impact="schema mismatch",
                fix="set schema_version to 'split-plan-pack@v1'",
            )
        )
        return failures, warnings

    failures.extend(collect_placeholders(split_plan_pack))

    stories = get_list(split_plan_pack.get("stories"), "$.stories", failures)
    if stories is None:
        return failures, warnings
    if len(stories) == 0:
        failures.append(
            Failure(
                loc="$.stories",
                problem="stories is empty",
                expected="at least 1 story",
                impact="cannot proceed",
                fix="add at least one story to stories[]",
            )
        )
        return failures, warnings

    prd_modules_value = prd_pack.get("modules")
    prd_modules: list[str] = []
    if isinstance(prd_modules_value, list):
        for module in prd_modules_value:
            if isinstance(module, dict) and isinstance(module.get("id"), str):
                prd_modules.append(module["id"])
    all_modules = {m for m in prd_modules if MODULE_ID_RE.match(m)}

    p0_modules: set[str] = set()
    if isinstance(prd_modules_value, list):
        for module in prd_modules_value:
            if not isinstance(module, dict):
                continue
            mid = module.get("id")
            if not (isinstance(mid, str) and MODULE_ID_RE.match(mid)):
                continue
            if module.get("priority") == "P0":
                p0_modules.add(mid)

    if len(all_modules) == 0:
        failures.append(
            Failure(
                loc="$.modules",
                problem="PRD modules missing or invalid",
                expected="docs/prd-pack.json has modules[].id like M-01",
                impact="cannot validate module coverage",
                fix="run PRD Check to normalize/assign docs/prd-pack.json modules[].id",
            )
        )
        return failures, warnings

    seen_story_names, expected_ns = validate_stories_and_module_coverage(
        stories,
        all_modules=all_modules,
        p0_modules=p0_modules,
        failures=failures,
    )
    validate_api_assignments(
        split_plan_pack,
        prd_pack=prd_pack,
        seen_story_names=seen_story_names,
        expected_ns=expected_ns,
        failures=failures,
        warnings=warnings,
        strict=strict,
    )

    return failures, warnings


def check_split_plan_pack(
    split_plan_pack: dict[str, Any], *, prd_pack: dict[str, Any], strict: bool = False
) -> tuple[bool, list[Failure], list[Failure]]:
    failures, warnings = validate_split_plan_pack(split_plan_pack, prd_pack=prd_pack, strict=strict)
    ready = len(failures) == 0 and (len(warnings) == 0 if strict else True)
    return ready, failures, warnings

