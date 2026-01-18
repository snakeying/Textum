from __future__ import annotations

from typing import Any

from textum.prd.prd_pack_types import Failure
from .story_check_validate_details import validate_story_details
from .story_check_validate_meta import validate_story_meta
from .story_check_validate_refs import validate_story_refs


def validate_story_internal(*, story: dict[str, Any], n: int) -> tuple[dict[str, Any], list[Failure]]:
    failures: list[Failure] = []
    ctx: dict[str, Any] = {
        "modules": [],
        "fp_ids": [],
        "prd_api": [],
        "prd_tbl": [],
        "prd_br": [],
        "api_endpoints": [],
        "tbl_name_by_id": {},
    }

    regenerate_story_fix = f"regenerate docs/stories/story-{n:03d}-*.json"

    modules, fp_ids, meta_failures = validate_story_meta(story=story, n=n, regenerate_story_fix=regenerate_story_fix)
    failures += meta_failures
    ctx["modules"] = modules
    ctx["fp_ids"] = fp_ids

    prd_api, prd_tbl, prd_br, refs_failures = validate_story_refs(story=story)
    failures += refs_failures
    ctx["prd_api"] = prd_api
    ctx["prd_tbl"] = prd_tbl
    ctx["prd_br"] = prd_br

    api_endpoints, tbl_name_by_id, details_failures = validate_story_details(
        story=story,
        regenerate_story_fix=regenerate_story_fix,
        fp_ids=fp_ids,
        prd_api=prd_api,
        prd_tbl=prd_tbl,
    )
    failures += details_failures
    ctx["api_endpoints"] = api_endpoints
    ctx["tbl_name_by_id"] = tbl_name_by_id

    return ctx, failures


