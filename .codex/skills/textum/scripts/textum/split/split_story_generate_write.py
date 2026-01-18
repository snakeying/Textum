from __future__ import annotations

from pathlib import Path
from typing import Any

from textum.prd.prd_pack_types import API_ID_RE, Failure, FP_ID_RE, MODULE_ID_RE
from .split_pack_io import write_json
from .split_pack_types import STORY_SCHEMA_VERSION
from .split_story_landing import parse_landing_tokens
from .split_story_paths import story_filename


def write_story_files_for_stories(
    *,
    stories: list[dict[str, Any]],
    story_fps: dict[str, list[dict[str, Any]]],
    api_by_story: dict[str, list[str]],
    api_by_id: dict[str, dict[str, Any]],
    table_name_to_id: dict[str, str],
    table_by_id: dict[str, dict[str, Any]],
    out_dir: Path,
    failures: list[Failure],
) -> list[Path]:
    written: list[Path] = []

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

    return written
