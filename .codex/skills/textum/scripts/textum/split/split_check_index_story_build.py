from __future__ import annotations

from pathlib import Path
from typing import Any


def build_story_index_row_and_meta(
    *,
    path: Path,
    story_name: str,
    n: int,
    slug: str,
    modules_set: set[str],
    prereq_set: set[str],
    fp_set: set[str],
    api_set: set[str],
    tbl_set: set[str],
) -> tuple[dict[str, Any], dict[str, Any]]:
    api_refs = len(api_set)
    tbl_refs = len(tbl_set)
    feature_points = len(fp_set)

    index_row = {
        "story": story_name,
        "n": n,
        "slug": slug,
        "story_file": str(path.as_posix()),
        "modules": sorted(modules_set),
        "prereq_stories": sorted(prereq_set),
        "metrics": {
            "api_refs": api_refs,
            "tbl_refs": tbl_refs,
            "feature_points": feature_points,
        },
        "refs": {
            "fp_ids": sorted(fp_set),
            "prd_api_ids": sorted(api_set),
            "prd_tbl_ids": sorted(tbl_set),
            "prd_br_ids": [],
            "gc_br_ids": [],
        },
    }
    meta = {
        "story_name": story_name,
        "api_refs": api_refs,
        "tbl_refs": tbl_refs,
        "feature_points": feature_points,
        "fp_set": fp_set,
        "api_set": api_set,
        "tbl_set": tbl_set,
        "modules_set": modules_set,
    }
    return index_row, meta

