from __future__ import annotations

from typing import Any

from .prd_pack_types import API_ID_RE, Failure, FP_ID_RE
from .split_story_prd import sorted_feature_points


def build_api_by_story(
    *, split_plan_pack: dict[str, Any], stories: list[dict[str, Any]], api_by_id: dict[str, dict[str, Any]]
) -> dict[str, list[str]]:
    api_assignments_value = split_plan_pack.get("api_assignments")
    api_assignments = api_assignments_value if isinstance(api_assignments_value, list) else []
    api_by_story: dict[str, list[str]] = {s.get("story"): [] for s in stories if isinstance(s.get("story"), str)}
    for row in api_assignments:
        if not isinstance(row, dict):
            continue
        api_id = row.get("api")
        story_name = row.get("story")
        if not (isinstance(api_id, str) and isinstance(story_name, str)):
            continue
        if API_ID_RE.match(api_id) and api_id in api_by_id and story_name in api_by_story:
            api_by_story[story_name].append(api_id)
    return api_by_story


def distribute_feature_points(
    *, stories: list[dict[str, Any]], modules_by_id: dict[str, dict[str, Any]], failures: list[Failure]
) -> dict[str, list[dict[str, Any]]]:
    story_fps: dict[str, list[dict[str, Any]]] = {s.get("story"): [] for s in stories if isinstance(s.get("story"), str)}
    for module_id, module_obj in modules_by_id.items():
        fp_list = sorted_feature_points(module_obj)
        owners: list[dict[str, Any]] = []
        for story_obj in stories:
            story_modules = story_obj.get("modules")
            if not isinstance(story_modules, list):
                continue
            if module_id in story_modules:
                owners.append(story_obj)
        if len(owners) == 0:
            failures.append(
                Failure(
                    loc="$.stories[].modules",
                    problem=f"module not assigned to any story: {module_id}",
                    expected="every module appears in at least 1 story",
                    impact="cannot assign feature points",
                    fix=f"add {module_id} to some story.modules[] in split-plan-pack.json",
                )
            )
            continue
        owners.sort(key=lambda x: x.get("n", 0) if isinstance(x.get("n"), int) else 0)
        for index, fp in enumerate(fp_list):
            owner = owners[index % len(owners)]
            owner_name = owner.get("story")
            if isinstance(owner_name, str) and owner_name in story_fps:
                story_fps[owner_name].append(fp)
    return story_fps


def validate_feature_point_assignment(
    *,
    modules_by_id: dict[str, dict[str, Any]],
    story_fps: dict[str, list[dict[str, Any]]],
    failures: list[Failure],
) -> bool:
    all_fp_ids: set[str] = set()
    for module_obj in modules_by_id.values():
        for fp in sorted_feature_points(module_obj):
            fid = fp.get("id")
            if isinstance(fid, str) and FP_ID_RE.match(fid):
                all_fp_ids.add(fid)

    assigned_fp_ids: set[str] = set()
    for fps in story_fps.values():
        for fp in fps:
            fid = fp.get("id")
            if isinstance(fid, str) and FP_ID_RE.match(fid):
                assigned_fp_ids.add(fid)

    if all_fp_ids == assigned_fp_ids:
        return True

    missing = sorted(all_fp_ids - assigned_fp_ids)
    extra = sorted(assigned_fp_ids - all_fp_ids)
    if missing:
        failures.append(
            Failure(
                loc="$.stories[].fp_ids",
                problem=f"some feature points are not assigned: {', '.join(missing)}",
                expected="every PRD FP-### assigned to exactly one story",
                impact="requirements have no owning story",
                fix="fix split-plan modules mapping so every module is owned by at least one story",
            )
        )
    if extra:
        failures.append(
            Failure(
                loc="$.stories[].fp_ids",
                problem=f"unknown feature points assigned: {', '.join(extra)}",
                expected="fp ids must come from PRD",
                impact="plan is inconsistent",
                fix="fix docs/prd-pack.json modules[].feature_points[].id to use valid FP-### ids",
            )
        )
    return False

