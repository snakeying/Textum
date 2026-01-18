from __future__ import annotations

from typing import Any

from textum.prd.prd_pack_types import FP_ID_RE, MODULE_ID_RE, Failure
from textum.split.split_pack_types import KEBAB_SLUG_RE, STORY_NAME_RE, STORY_SCHEMA_VERSION
from .story_check_utils import check_id_list, require_list, require_non_empty_str


def validate_story_meta(
    *,
    story: dict[str, Any],
    n: int,
    regenerate_story_fix: str,
) -> tuple[list[str], list[str], list[Failure]]:
    failures: list[Failure] = []

    if story.get("schema_version") != STORY_SCHEMA_VERSION:
        failures.append(
            Failure(
                loc="$.schema_version",
                problem=f"schema_version must be {STORY_SCHEMA_VERSION}",
                expected=STORY_SCHEMA_VERSION,
                impact="cannot trust story format",
                fix=regenerate_story_fix,
            )
        )

    failures += require_non_empty_str(story.get("story"), loc="$.story")
    expected_story_name = f"Story {n}"
    if story.get("story") != expected_story_name:
        failures.append(
            Failure(
                loc="$.story",
                problem=f"story must equal {expected_story_name}",
                expected=expected_story_name,
                impact="ambiguous story identity",
                fix=regenerate_story_fix,
            )
        )
    if story.get("n") != n:
        failures.append(
            Failure(
                loc="$.n",
                problem=f"n must equal {n}",
                expected=str(n),
                impact="ambiguous story identity",
                fix=regenerate_story_fix,
            )
        )

    slug = story.get("slug")
    if not isinstance(slug, str) or KEBAB_SLUG_RE.match(slug) is None:
        failures.append(
            Failure(
                loc="$.slug",
                problem=f"invalid slug: {slug!r}",
                expected="kebab-case string",
                impact="file naming and routing break",
                fix=regenerate_story_fix,
            )
        )

    failures += require_non_empty_str(story.get("title"), loc="$.title")
    failures += require_non_empty_str(story.get("goal"), loc="$.goal")

    modules, module_failures = check_id_list(
        story.get("modules"), loc="$.modules", pattern=MODULE_ID_RE, label="module"
    )
    failures += module_failures

    prereq, prereq_failures = require_list(story.get("prereq_stories"), loc="$.prereq_stories")
    failures += prereq_failures
    prereq_numbers: list[int] = []
    if prereq is not None:
        for idx, item in enumerate(prereq):
            if not isinstance(item, str) or STORY_NAME_RE.match(item) is None:
                failures.append(
                    Failure(
                        loc=f"$.prereq_stories[{idx}]",
                        problem=f"invalid prereq story ref: {item!r}",
                        expected="Story <number>",
                        impact="dependency graph invalid",
                        fix=regenerate_story_fix,
                    )
                )
                continue
            num = int(STORY_NAME_RE.match(item).group(1))
            prereq_numbers.append(num)
            if num >= n:
                failures.append(
                    Failure(
                        loc=f"$.prereq_stories[{idx}]",
                        problem=f"prereq story must be < {n}, got {item}",
                        expected="only earlier stories",
                        impact="cannot execute in order",
                        fix=regenerate_story_fix,
                    )
                )
    if len(set(prereq_numbers)) != len(prereq_numbers):
        failures.append(
            Failure(
                loc="$.prereq_stories",
                problem="duplicate prereq stories",
                expected="unique prereq story refs",
                impact="dependency graph ambiguous",
                fix=regenerate_story_fix,
            )
        )

    fp_ids, fp_id_failures = check_id_list(story.get("fp_ids"), loc="$.fp_ids", pattern=FP_ID_RE, label="fp")
    failures += fp_id_failures

    return modules, fp_ids, failures


