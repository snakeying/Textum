from __future__ import annotations

from typing import Any

from textum.prd.prd_pack_types import Failure
from .split_plan_pack_validate_story_row import validate_story_row


def validate_stories_and_module_coverage(
    stories: list[Any],
    *,
    all_modules: set[str],
    p0_modules: set[str],
    failures: list[Failure],
) -> tuple[set[str], set[int]]:
    seen_slugs: set[str] = set()
    seen_story_names: set[str] = set()
    covered_modules: set[str] = set()
    story_name_by_n: dict[int, str] = {}
    duplicate_ns: set[int] = set()

    for index, item in enumerate(stories):
        validate_story_row(
            item=item,
            index=index,
            all_modules=all_modules,
            failures=failures,
            seen_slugs=seen_slugs,
            seen_story_names=seen_story_names,
            covered_modules=covered_modules,
            story_name_by_n=story_name_by_n,
            duplicate_ns=duplicate_ns,
        )

    expected_ns = set(range(1, len(stories) + 1))
    actual_ns = {n for n in story_name_by_n.keys() if isinstance(n, int)}
    if actual_ns != expected_ns:
        failures.append(
            Failure(
                loc="$.stories[].n",
                problem=f"non-consecutive story numbers: got {sorted(actual_ns)}",
                expected=f"consecutive 1..{len(stories)}",
                impact="references become ambiguous",
                fix="rewrite stories[].n to consecutive 1..N (including references)",
            )
        )
    if duplicate_ns:
        failures.append(
            Failure(
                loc="$.stories[].n",
                problem=f"duplicate story numbers found: {', '.join(str(x) for x in sorted(duplicate_ns))}",
                expected=f"unique consecutive 1..{len(stories)}",
                impact="references become ambiguous",
                fix="rewrite stories[].n to unique consecutive 1..N",
            )
        )

    missing_modules = sorted(all_modules - covered_modules)
    if missing_modules:
        failures.append(
            Failure(
                loc="$.stories[].modules",
                problem=f"modules not covered by any story: {', '.join(missing_modules)}",
                expected="every PRD module appears in at least 1 story",
                impact="some requirements have no owning story",
                fix="add missing modules into some story.modules[]",
            )
        )

    missing_p0 = sorted(p0_modules - covered_modules)
    if missing_p0:
        failures.append(
            Failure(
                loc="$.stories[].modules",
                problem=f"P0 modules not covered: {', '.join(missing_p0)}",
                expected="every P0 module appears in at least 1 story",
                impact="critical scope is uncovered",
                fix="add missing P0 modules into some story.modules[]",
            )
        )

    return seen_story_names, expected_ns

