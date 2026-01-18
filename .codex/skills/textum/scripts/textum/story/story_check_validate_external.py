from __future__ import annotations

from typing import Any

from textum.prd.prd_pack_types import Failure
from .story_check_utils import build_prd_maps, build_scaffold_module_ids


def validate_story_against_prd(
    *,
    story_n: int,
    fp_ids: list[str],
    prd_api: list[str],
    prd_tbl: list[str],
    prd_br: list[str],
    api_endpoints: list[Any],
    tbl_name_by_id: dict[str, str],
    prd_pack: dict[str, Any],
) -> list[Failure]:
    failures: list[Failure] = []
    api_by_id, tbl_by_id, prd_fp_ids, br_by_id = build_prd_maps(prd_pack)

    for idx, fp_id in enumerate(fp_ids):
        if fp_id not in prd_fp_ids:
            failures.append(
                Failure(
                    loc=f"$.fp_ids[{idx}]",
                    problem=f"unknown FP id in PRD: {fp_id}",
                    expected="fp id exists in docs/prd-pack.json modules[].feature_points[]",
                    impact="story references missing requirement",
                    fix=f"regenerate docs/stories/story-{story_n:03d}-*.json",
                )
            )

    for idx, api_id in enumerate(prd_api):
        prd_api_obj = api_by_id.get(api_id)
        if prd_api_obj is None:
            failures.append(
                Failure(
                    loc=f"$.refs.prd_api[{idx}]",
                    problem=f"unknown API id in PRD: {api_id}",
                    expected="api id exists in docs/prd-pack.json api.endpoints[]",
                    impact="story references missing API requirement",
                    fix=f"regenerate docs/stories/story-{story_n:03d}-*.json",
                )
            )
            continue
        prd_method = prd_api_obj.get("method")
        prd_path = prd_api_obj.get("path")
        for ep in api_endpoints:
            if not isinstance(ep, dict) or ep.get("id") != api_id:
                continue
            if prd_method and ep.get("method") != prd_method:
                failures.append(
                    Failure(
                        loc=f"$.details.api_endpoints[?(@.id=='{api_id}')].method",
                        problem=f"method mismatch for {api_id}: story={ep.get('method')}, prd={prd_method}",
                        expected=str(prd_method),
                        impact="API contract mismatch",
                        fix=f"regenerate docs/stories/story-{story_n:03d}-*.json",
                    )
                )
            if prd_path and ep.get("path") != prd_path:
                failures.append(
                    Failure(
                        loc=f"$.details.api_endpoints[?(@.id=='{api_id}')].path",
                        problem=f"path mismatch for {api_id}: story={ep.get('path')}, prd={prd_path}",
                        expected=str(prd_path),
                        impact="API contract mismatch",
                        fix=f"regenerate docs/stories/story-{story_n:03d}-*.json",
                    )
                )

    for idx, tbl_id in enumerate(prd_tbl):
        prd_tbl_obj = tbl_by_id.get(tbl_id)
        if prd_tbl_obj is None:
            failures.append(
                Failure(
                    loc=f"$.refs.prd_tbl[{idx}]",
                    problem=f"unknown table id in PRD: {tbl_id}",
                    expected="table id exists in docs/prd-pack.json data_model.tables[]",
                    impact="story references missing data model",
                    fix=f"regenerate docs/stories/story-{story_n:03d}-*.json",
                )
            )
            continue
        prd_name = prd_tbl_obj.get("name")
        story_name = tbl_name_by_id.get(tbl_id)
        if isinstance(prd_name, str) and isinstance(story_name, str) and prd_name != story_name:
            failures.append(
                Failure(
                    loc=f"$.details.tables_overview[?(@.id=='{tbl_id}')].name",
                    problem=f"table name mismatch for {tbl_id}: story={story_name}, prd={prd_name}",
                    expected=str(prd_name),
                    impact="data model mismatch",
                    fix=f"regenerate docs/stories/story-{story_n:03d}-*.json",
                )
            )

    for idx, br_id in enumerate(prd_br):
        if br_id not in br_by_id:
            failures.append(
                Failure(
                    loc=f"$.refs.prd_br[{idx}]",
                    problem=f"unknown BR id in PRD: {br_id}",
                    expected="BR id exists in docs/prd-pack.json business_rules[]",
                    impact="story references missing business rule",
                    fix=f"regenerate docs/stories/story-{story_n:03d}-*.json",
                )
            )

    return failures


def validate_story_against_scaffold(
    *, story_n: int, modules: list[str], scaffold_pack: dict[str, Any]
) -> list[Failure]:
    failures: list[Failure] = []
    scaffold_module_ids = build_scaffold_module_ids(scaffold_pack)
    for idx, module_id in enumerate(modules):
        if module_id not in scaffold_module_ids:
            failures.append(
                Failure(
                    loc=f"$.modules[{idx}]",
                    problem=f"unknown module id in scaffold extracted.modules_index: {module_id}",
                    expected="module id exists in docs/scaffold-pack.json extracted.modules_index[]",
                    impact="story module cannot be grounded",
                    fix="populate docs/scaffold-pack.json:$.extracted.modules_index",
                )
            )
    return failures

