from __future__ import annotations

from typing import Any

from textum.prd.prd_pack_types import Failure
from .split_check_refs_validate_against import validate_refs_against_packs


def validate_split_refs(
    *,
    index_pack: dict[str, Any],
    prd_pack: dict[str, Any],
    scaffold_pack: dict[str, Any],
) -> list[Failure]:
    failures: list[Failure] = []

    if index_pack.get("schema_version") != "split-check-index-pack@v1":
        failures.append(
            Failure(
                loc="$.schema_version",
                problem=f"unexpected schema_version: {index_pack.get('schema_version')!r}",
                expected="'split-check-index-pack@v1'",
                impact="cannot validate split refs",
                fix="regenerate docs/split-check-index-pack.json",
            )
        )
        return failures

    split_plan = index_pack.get("split_plan")
    plan_story_count: int | None = None
    if not isinstance(split_plan, dict):
        failures.append(
            Failure(
                loc="$.split_plan",
                problem=f"expected object, got {type(split_plan).__name__}",
                expected="object",
                impact="cannot validate split completeness",
                fix="regenerate docs/split-check-index-pack.json",
            )
        )
    else:
        story_count = split_plan.get("story_count")
        if not isinstance(story_count, int):
            failures.append(
                Failure(
                    loc="$.split_plan.story_count",
                    problem=f"expected int, got {type(story_count).__name__}",
                    expected="integer",
                    impact="cannot validate story file completeness",
                    fix="regenerate docs/split-check-index-pack.json",
                )
            )
        else:
            plan_story_count = story_count

    stories = index_pack.get("stories")
    actual_story_count: int | None = None
    if not isinstance(stories, list):
        failures.append(
            Failure(
                loc="$.stories",
                problem=f"expected array, got {type(stories).__name__}",
                expected="array",
                impact="cannot validate story file completeness",
                fix="regenerate docs/split-check-index-pack.json",
            )
        )
    else:
        actual_story_count = len(stories)

    if plan_story_count is not None and actual_story_count is not None and plan_story_count != actual_story_count:
        failures.append(
            Failure(
                loc="docs/split-check-index-pack.json",
                problem=(
                    f"story_count mismatch: split_plan.story_count={plan_story_count} but indexed stories={actual_story_count}"
                ),
                expected="split plan story_count matches generated story files count",
                impact="execution plan is incomplete or out of date",
                fix="regenerate docs/stories/",
            )
        )

    summary = index_pack.get("summary")
    if not isinstance(summary, dict):
        failures.append(
            Failure(
                loc="$.summary",
                problem=f"expected object, got {type(summary).__name__}",
                expected="object",
                impact="cannot validate split refs",
                fix="regenerate docs/split-check-index-pack.json",
            )
        )
        return failures

    refs = summary.get("refs")
    if not isinstance(refs, dict):
        failures.append(
            Failure(
                loc="$.summary.refs",
                problem=f"expected object, got {type(refs).__name__}",
                expected="object",
                impact="cannot validate split refs",
                fix="regenerate docs/split-check-index-pack.json",
            )
        )
        return failures

    failures.extend(
        validate_refs_against_packs(refs=refs, summary=summary, prd_pack=prd_pack, scaffold_pack=scaffold_pack)
    )
    return failures

