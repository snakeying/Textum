from __future__ import annotations

from pathlib import Path
from typing import Any

from prd_pack_maps import build_prd_maps
from prd_pack_types import Failure
from prd_slices_utils import rel_posix


def collect_story_prd_context(
    *,
    story: dict[str, Any],
    prd_pack: dict[str, Any],
    story_source_path: Path,
    workspace_root: Path,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[Failure]]:
    story_refs = story.get("refs") if isinstance(story.get("refs"), dict) else {}
    prd_tbl_ids = story_refs.get("prd_tbl") if isinstance(story_refs.get("prd_tbl"), list) else []
    prd_br_ids = story_refs.get("prd_br") if isinstance(story_refs.get("prd_br"), list) else []

    _, tbl_by_id, _, br_by_id = build_prd_maps(prd_pack)

    tables: list[dict[str, Any]] = []
    for idx, tbl_id in enumerate(prd_tbl_ids):
        if not isinstance(tbl_id, str):
            continue
        row = tbl_by_id.get(tbl_id)
        if not isinstance(row, dict):
            return (
                [],
                [],
                [
                    Failure(
                        loc=f"$.refs.prd_tbl[{idx}]",
                        problem=f"unknown table id in PRD: {tbl_id}",
                        expected="table id exists in docs/prd-pack.json data_model.tables[]",
                        impact="cannot build exec context",
                        fix=f"regenerate {rel_posix(story_source_path, workspace_root)}",
                    )
                ],
            )
        tables.append(row)

    business_rules: list[dict[str, Any]] = []
    for idx, br_id in enumerate(prd_br_ids):
        if not isinstance(br_id, str):
            continue
        row = br_by_id.get(br_id)
        if not isinstance(row, dict):
            return (
                [],
                [],
                [
                    Failure(
                        loc=f"$.refs.prd_br[{idx}]",
                        problem=f"unknown BR id in PRD: {br_id}",
                        expected="BR id exists in docs/prd-pack.json business_rules[]",
                        impact="cannot build exec context",
                        fix=f"regenerate {rel_posix(story_source_path, workspace_root)}",
                    )
                ],
            )
        business_rules.append(row)

    return tables, business_rules, []

