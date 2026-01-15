from __future__ import annotations

from pathlib import Path
from typing import Any

from prd_pack_types import API_ID_RE, Failure, FP_ID_RE, MODULE_ID_RE
from split_pack_io import ensure_dir, write_json
from split_pack_types import STORY_SCHEMA_VERSION
from split_story_landing import parse_landing_tokens
from split_story_paths import story_filename
from split_story_prd import build_table_indices, extract_api_endpoints_by_id, extract_modules_by_id, sorted_feature_points


def generate_story_files(
    *,
    split_plan_pack: dict[str, Any],
    prd_pack: dict[str, Any],
    out_dir: Path,
    clean: bool,
) -> tuple[list[Path], list[Failure]]:
    failures: list[Failure] = []
    written: list[Path] = []

    if clean and out_dir.exists():
        for path in out_dir.glob("story-*.json"):
            path.unlink(missing_ok=True)

    ensure_dir(out_dir)

    modules_by_id = extract_modules_by_id(prd_pack)
    table_name_to_id, table_by_id = build_table_indices(prd_pack)
    api_by_id = extract_api_endpoints_by_id(prd_pack)

    stories_value = split_plan_pack.get("stories")
    if not isinstance(stories_value, list):
        return [], [
            Failure(
                loc="$.stories",
                problem="expected array",
                expected="array",
                impact="cannot generate stories",
                fix="fix split-plan-pack.json stories[]",
            )
        ]

    stories: list[dict[str, Any]] = []
    for item in stories_value:
        if isinstance(item, dict):
            stories.append(item)

    stories.sort(key=lambda x: x.get("n", 0) if isinstance(x.get("n"), int) else 0)

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

    if all_fp_ids != assigned_fp_ids:
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
        return [], failures

    for story_obj in stories:
        story_name = story_obj.get("story")
        n = story_obj.get("n")
        slug = story_obj.get("slug")
        goal = story_obj.get("goal")
        if not (isinstance(story_name, str) and isinstance(n, int) and n > 0 and isinstance(slug, str) and slug):
            continue

        modules = story_obj.get("modules") if isinstance(story_obj.get("modules"), list) else []
        prereq = story_obj.get("prereq_stories") if isinstance(story_obj.get("prereq_stories"), list) else []

        fps = story_fps.get(story_name, [])
        fp_ids = sorted([fp["id"] for fp in fps if isinstance(fp.get("id"), str) and FP_ID_RE.match(fp["id"])])

        tbl_ids: set[str] = set()
        art_file: set[str] = set()
        art_cfg: set[str] = set()
        art_ext: set[str] = set()
        fp_details: list[dict[str, Any]] = []

        for fp in fps:
            fid = fp.get("id")
            desc = fp.get("desc")
            landing = fp.get("landing")
            if not (isinstance(fid, str) and FP_ID_RE.match(fid) and isinstance(desc, str)):
                continue
            landing_list = landing if isinstance(landing, list) else []
            fp_details.append({"id": fid, "desc": desc, "landing": landing_list})
            derived_tbl, derived_file, derived_cfg, derived_ext = parse_landing_tokens(
                landing_list,
                table_name_to_id=table_name_to_id,
                failures=failures,
                loc_prefix=f"$.modules[*].feature_points[{fid}].landing",
            )
            tbl_ids |= derived_tbl
            art_file |= derived_file
            art_cfg |= derived_cfg
            art_ext |= derived_ext

        api_ids = sorted({a for a in api_by_story.get(story_name, []) if API_ID_RE.match(a)})
        api_details: list[dict[str, Any]] = []
        for aid in api_ids:
            endpoint = api_by_id.get(aid)
            if endpoint is None:
                failures.append(
                    Failure(
                        loc="$.api_assignments",
                        problem=f"API endpoint not found in PRD: {aid}",
                        expected="api id exists in prd-pack api.endpoints[].id",
                        impact="cannot generate story API details",
                        fix="fix split-plan api_assignments to reference existing PRD APIs",
                    )
                )
                continue
            api_details.append(endpoint)

        tables_overview: list[dict[str, Any]] = []
        for tid in sorted(tbl_ids):
            table = table_by_id.get(tid)
            if table is None:
                failures.append(
                    Failure(
                        loc="$.refs.prd_tbl",
                        problem=f"table id not found in PRD: {tid}",
                        expected="TBL-### exists in data_model.tables[].id",
                        impact="cannot generate table overview",
                        fix=f"add docs/prd-pack.json data_model.tables[] entry with id={tid}",
                    )
                )
                continue
            tables_overview.append(
                {
                    "id": table.get("id"),
                    "name": table.get("name"),
                    "purpose": table.get("purpose"),
                    "fields_summary": table.get("fields_summary"),
                }
            )

        title = goal if isinstance(goal, str) and goal.strip() else f"{story_name}: {', '.join(modules)}"

        story_pack = {
            "schema_version": STORY_SCHEMA_VERSION,
            "story": story_name,
            "n": n,
            "slug": slug,
            "title": title,
            "goal": goal if isinstance(goal, str) else None,
            "modules": [m for m in modules if isinstance(m, str) and MODULE_ID_RE.match(m)],
            "prereq_stories": [p for p in prereq if isinstance(p, str) and p.strip()],
            "fp_ids": fp_ids,
            "refs": {
                "prd_api": api_ids,
                "prd_tbl": sorted(tbl_ids),
                "prd_br": [],
                "gc_br": [],
            },
            "artifacts": {
                "file": sorted(art_file),
                "cfg": sorted(art_cfg),
                "ext": sorted(art_ext),
            },
            "details": {
                "feature_points": fp_details,
                "api_endpoints": api_details,
                "tables_overview": tables_overview,
            },
        }

        out_path = out_dir / story_filename(n, slug)
        write_json(out_path, story_pack)
        written.append(out_path)

    return written, failures
