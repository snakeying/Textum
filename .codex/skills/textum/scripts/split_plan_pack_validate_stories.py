from __future__ import annotations

from typing import Any

from prd_pack_types import Failure, MODULE_ID_RE
from split_pack_types import KEBAB_SLUG_RE, STORY_NAME_RE
from split_plan_pack_validate_utils import get_dict, get_list, require_str


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
        loc = f"$.stories[{index}]"
        story_obj = get_dict(item, loc, failures)
        if story_obj is None:
            continue

        story = require_str(story_obj.get("story"), f"{loc}.story", failures)
        n = story_obj.get("n")
        if not isinstance(n, int) or n <= 0:
            failures.append(
                Failure(
                    loc=f"{loc}.n",
                    problem=f"n must be positive int, got {n!r}",
                    expected="positive integer",
                    impact="cannot proceed",
                    fix=f"set {loc}.n to a positive integer",
                )
            )
        else:
            if n in story_name_by_n:
                duplicate_ns.add(n)
            story_name_by_n[n] = f"Story {n}"
            expected_story = f"Story {n}"
            if story is not None and story != expected_story:
                failures.append(
                    Failure(
                        loc=f"{loc}.story",
                        problem=f"story name mismatch: {story!r}",
                        expected=expected_story,
                        impact="references become ambiguous",
                        fix=f"set {loc}.story to {expected_story!r}",
                    )
                )

        if story is not None:
            if story in seen_story_names:
                failures.append(
                    Failure(
                        loc=f"{loc}.story",
                        problem=f"duplicate story: {story}",
                        expected="unique story names",
                        impact="references become ambiguous",
                        fix="deduplicate stories[].story",
                    )
                )
            seen_story_names.add(story)

        slug = require_str(story_obj.get("slug"), f"{loc}.slug", failures)
        if slug is not None:
            if not KEBAB_SLUG_RE.match(slug):
                failures.append(
                    Failure(
                        loc=f"{loc}.slug",
                        problem=f"invalid slug: {slug!r}",
                        expected="kebab-case (a-z0-9-)",
                        impact="file naming is unstable",
                        fix=f"rewrite {loc}.slug as kebab-case",
                    )
                )
            if slug in seen_slugs:
                failures.append(
                    Failure(
                        loc=f"{loc}.slug",
                        problem=f"duplicate slug: {slug}",
                        expected="unique slugs",
                        impact="file names collide",
                        fix="make all stories[].slug unique",
                    )
                )
            seen_slugs.add(slug)

        goal = require_str(story_obj.get("goal"), f"{loc}.goal", failures)
        if goal is not None and goal.strip().upper() == "N/A":
            failures.append(
                Failure(
                    loc=f"{loc}.goal",
                    problem="goal cannot be N/A",
                    expected="a concrete goal",
                    impact="story is not executable",
                    fix=f"fill {loc}.goal with a concrete goal",
                )
            )

        modules = get_list(story_obj.get("modules"), f"{loc}.modules", failures)
        if modules is not None:
            if len(modules) == 0:
                failures.append(
                    Failure(
                        loc=f"{loc}.modules",
                        problem="modules is empty",
                        expected="at least 1 module id like M-01",
                        impact="cannot map feature points",
                        fix=f"add at least one module id to {loc}.modules[]",
                    )
                )
            for mi, module_id in enumerate(modules):
                if not isinstance(module_id, str):
                    failures.append(
                        Failure(
                            loc=f"{loc}.modules[{mi}]",
                            problem=f"module id must be string, got {type(module_id).__name__}",
                            expected="M-01",
                            impact="cannot validate module coverage",
                            fix=f"rewrite {loc}.modules[{mi}] as a string module id",
                        )
                    )
                    continue
                if not MODULE_ID_RE.match(module_id):
                    failures.append(
                        Failure(
                            loc=f"{loc}.modules[{mi}]",
                            problem=f"invalid module id: {module_id!r}",
                            expected="M-01",
                            impact="cannot validate module coverage",
                            fix=f"set {loc}.modules[{mi}] to a valid module id like 'M-01'",
                        )
                    )
                    continue
                if module_id not in all_modules:
                    failures.append(
                        Failure(
                            loc=f"{loc}.modules[{mi}]",
                            problem=f"unknown module id: {module_id}",
                            expected="module exists in PRD modules[].id",
                            impact="module coverage check fails",
                            fix="fix modules[] to use PRD module ids",
                        )
                    )
                    continue
                covered_modules.add(module_id)

        prereq = get_list(story_obj.get("prereq_stories"), f"{loc}.prereq_stories", failures)
        if prereq is not None:
            for pi, p in enumerate(prereq):
                if not isinstance(p, str):
                    failures.append(
                        Failure(
                            loc=f"{loc}.prereq_stories[{pi}]",
                            problem=f"prereq must be string, got {type(p).__name__}",
                            expected="Story N",
                            impact="cannot validate dependencies",
                            fix=f"rewrite {loc}.prereq_stories[{pi}] as 'Story N'",
                        )
                    )
                    continue
                match = STORY_NAME_RE.match(p.strip())
                if match is None:
                    failures.append(
                        Failure(
                            loc=f"{loc}.prereq_stories[{pi}]",
                            problem=f"invalid prereq: {p!r}",
                            expected="Story N",
                            impact="cannot validate dependencies",
                            fix=f"rewrite {loc}.prereq_stories[{pi}] as 'Story N'",
                        )
                    )
                else:
                    prereq_n = int(match.group(1))
                    if isinstance(n, int) and prereq_n >= n:
                        failures.append(
                            Failure(
                                loc=f"{loc}.prereq_stories[{pi}]",
                                problem=f"prereq must be a smaller story number: {p!r}",
                                expected=f"Story {prereq_n} where {prereq_n} < {n}",
                                impact="dependency graph is not executable",
                                fix=f"remove or fix {loc}.prereq_stories[{pi}] to reference an earlier story",
                            )
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
                fix="renumber stories to be consecutive 1..N and update story/prereq/api references",
            )
        )
    if duplicate_ns:
        failures.append(
            Failure(
                loc="$.stories[].n",
                problem=f"duplicate story numbers found: {', '.join(str(x) for x in sorted(duplicate_ns))}",
                expected=f"unique consecutive 1..{len(stories)}",
                impact="references become ambiguous",
                fix="deduplicate stories[].n and renumber to be consecutive",
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

