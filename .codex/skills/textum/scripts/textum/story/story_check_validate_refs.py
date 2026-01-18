from __future__ import annotations

from typing import Any

from .prd_pack_types import API_ID_RE, BR_ID_RE, TBL_ID_RE, Failure
from .story_check_utils import check_id_list, require_dict, require_list


def validate_story_refs(
    *,
    story: dict[str, Any],
) -> tuple[list[str], list[str], list[str], list[Failure]]:
    failures: list[Failure] = []

    refs, refs_failures = require_dict(story.get("refs"), loc="$.refs")
    failures += refs_failures

    prd_api: list[str] = []
    prd_tbl: list[str] = []
    prd_br: list[str] = []

    if refs is not None:
        prd_api, failures_api = check_id_list(refs.get("prd_api"), loc="$.refs.prd_api", pattern=API_ID_RE, label="api")
        prd_tbl, failures_tbl = check_id_list(refs.get("prd_tbl"), loc="$.refs.prd_tbl", pattern=TBL_ID_RE, label="tbl")
        prd_br, failures_br = check_id_list(refs.get("prd_br"), loc="$.refs.prd_br", pattern=BR_ID_RE, label="br")
        failures += failures_api + failures_tbl + failures_br
        _, failures_gc = require_list(refs.get("gc_br"), loc="$.refs.gc_br")
        failures += failures_gc

    return prd_api, prd_tbl, prd_br, failures


