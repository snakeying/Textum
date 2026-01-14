from __future__ import annotations

from typing import Any

from prd_pack_types import API_ID_RE, Failure
from split_plan_pack_validate_utils import get_dict, get_list, require_str


def validate_api_assignments(
    split_plan_pack: dict[str, Any],
    *,
    prd_pack: dict[str, Any],
    seen_story_names: set[str],
    expected_ns: set[int],
    failures: list[Failure],
) -> None:
    api = prd_pack.get("api") if isinstance(prd_pack.get("api"), dict) else {}
    prd_has_api = api.get("has_api") is True
    endpoints = api.get("endpoints") if isinstance(api.get("endpoints"), list) else []
    prd_api_ids: list[str] = []
    for endpoint in endpoints:
        if isinstance(endpoint, dict) and isinstance(endpoint.get("id"), str):
            prd_api_ids.append(endpoint["id"])
    prd_api_set = {a for a in prd_api_ids if API_ID_RE.match(a)}

    api_assignments = get_list(split_plan_pack.get("api_assignments"), "$.api_assignments", failures)
    if api_assignments is None:
        return

    if prd_has_api is False:
        if len(api_assignments) != 0:
            failures.append(
                Failure(
                    loc="$.api_assignments",
                    problem="PRD has_api=false but api_assignments is not empty",
                    expected="[]",
                    impact="contradictory API planning",
                    fix="set api_assignments to []",
                )
            )
        return

    if len(prd_api_set) == 0:
        failures.append(
            Failure(
                loc="$.api",
                problem="PRD has_api=true but no valid endpoint ids found",
                expected="api.endpoints[].id like API-001",
                impact="cannot plan API coverage",
                fix="fill docs/prd-pack.json api.endpoints[].id with valid API-### ids",
            )
        )
        return

    assigned_by_api: dict[str, str] = {}
    assigned_count_by_story: dict[str, int] = {f"Story {n}": 0 for n in expected_ns}
    for index, row in enumerate(api_assignments):
        loc = f"$.api_assignments[{index}]"
        row_obj = get_dict(row, loc, failures)
        if row_obj is None:
            continue
        api_id = require_str(row_obj.get("api"), f"{loc}.api", failures)
        story_name = require_str(row_obj.get("story"), f"{loc}.story", failures)
        if api_id is None or story_name is None:
            continue
        if not API_ID_RE.match(api_id):
            failures.append(
                Failure(
                    loc=f"{loc}.api",
                    problem=f"invalid api id: {api_id!r}",
                    expected="API-001",
                    impact="cannot validate API coverage",
                    fix=f"rewrite {loc}.api as 'API-###'",
                )
            )
            continue
        if api_id not in prd_api_set:
            failures.append(
                Failure(
                    loc=f"{loc}.api",
                    problem=f"API id not found in PRD: {api_id}",
                    expected="api exists in prd-pack api.endpoints[].id",
                    impact="cannot validate API coverage",
                    fix="fix api_assignments[].api to use PRD API ids",
                )
            )
            continue
        if story_name not in seen_story_names:
            failures.append(
                Failure(
                    loc=f"{loc}.story",
                    problem=f"story not found: {story_name}",
                    expected="story exists in stories[].story",
                    impact="API assignment is dangling",
                    fix="fix api_assignments[].story to reference an existing story",
                )
            )
            continue
        if api_id in assigned_by_api:
            failures.append(
                Failure(
                    loc=f"{loc}.api",
                    problem=f"duplicate API assignment: {api_id}",
                    expected="each API assigned exactly once",
                    impact="API ownership is ambiguous",
                    fix="deduplicate api_assignments so each API appears once",
                )
            )
            continue
        assigned_by_api[api_id] = story_name
        assigned_count_by_story[story_name] = assigned_count_by_story.get(story_name, 0) + 1

    missing_api = sorted(prd_api_set - set(assigned_by_api.keys()))
    extra_api = sorted(set(assigned_by_api.keys()) - prd_api_set)
    if missing_api:
        failures.append(
            Failure(
                loc="$.api_assignments",
                problem=f"missing API assignments: {', '.join(missing_api)}",
                expected="every PRD API is assigned to exactly 1 story",
                impact="API work has no owning story",
                fix="add api_assignments rows for the missing APIs",
            )
        )
    if extra_api:
        failures.append(
            Failure(
                loc="$.api_assignments",
                problem=f"unknown API ids assigned: {', '.join(extra_api)}",
                expected="api ids must be from PRD",
                impact="API plan contains invalid ids",
                fix="remove invalid api_assignments rows",
            )
        )

    for story_name, count in sorted(assigned_count_by_story.items(), key=lambda x: x[0]):
        if count >= 6:
            failures.append(
                Failure(
                    loc="$.api_assignments",
                    problem=f"API assigned too many for {story_name}: {count}",
                    expected="<= 5 APIs per story (prefer <= 3)",
                    impact="story likely oversized",
                    fix="split the story or redistribute API assignments to reduce per-story API count",
                )
            )
