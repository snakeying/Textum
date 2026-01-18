from __future__ import annotations

from pathlib import Path
from typing import Any

from textum.prd.prd_pack_types import Failure, FP_ID_RE, TBL_ID_RE
from .split_thresholds import is_threshold_hard_fail, threshold_decision_hits


def suggest_fp_to_move_for_threshold(*, story_data: dict[str, Any]) -> str | None:
    fp_ids = story_data.get("fp_ids") if isinstance(story_data.get("fp_ids"), list) else []
    fp_ids_norm = sorted({fp for fp in fp_ids if isinstance(fp, str) and FP_ID_RE.match(fp)})
    if not fp_ids_norm:
        return None

    details = story_data.get("details")
    if not isinstance(details, dict):
        return fp_ids_norm[0]

    # Map DB table names to PRD table ids (TBL-###) via tables_overview (if available),
    # then pick the FP that "owns" the most unique tables in this story.
    name_to_tbl: dict[str, str] = {}
    tables_overview = details.get("tables_overview")
    if isinstance(tables_overview, list):
        for row in tables_overview:
            if not isinstance(row, dict):
                continue
            tid = row.get("id")
            name = row.get("name")
            if isinstance(tid, str) and TBL_ID_RE.match(tid) and isinstance(name, str) and name.strip():
                name_to_tbl[name.strip()] = tid

    fp_to_tbls: dict[str, set[str]] = {}
    feature_points = details.get("feature_points")
    if isinstance(feature_points, list) and name_to_tbl:
        for row in feature_points:
            if not isinstance(row, dict):
                continue
            fid = row.get("id")
            if not (isinstance(fid, str) and FP_ID_RE.match(fid) and fid in fp_ids_norm):
                continue
            landing = row.get("landing")
            if not isinstance(landing, list):
                continue
            tbls: set[str] = set()
            for item in landing:
                if not (isinstance(item, str) and item.startswith("DB:")):
                    continue
                name = item.removeprefix("DB:").strip()
                tid = name_to_tbl.get(name)
                if tid:
                    tbls.add(tid)
            if tbls:
                fp_to_tbls[fid] = tbls

    if not fp_to_tbls:
        return fp_ids_norm[0]

    tbl_counts: dict[str, int] = {}
    for tbls in fp_to_tbls.values():
        for t in tbls:
            tbl_counts[t] = tbl_counts.get(t, 0) + 1

    best_fp: str | None = None
    best_score: tuple[int, int] = (-1, -1)  # (unique_tbls, total_tbls)
    for fid in sorted(fp_to_tbls.keys()):
        tbls = fp_to_tbls[fid]
        unique_tbls = sum(1 for t in tbls if tbl_counts.get(t, 0) == 1)
        score = (unique_tbls, len(tbls))
        if score > best_score:
            best_score = score
            best_fp = fid

    return best_fp or fp_ids_norm[0]


def evaluate_story_thresholds(
    *,
    story_file: Path,
    story_name: str,
    api_refs: int,
    tbl_refs: int,
    feature_points: int,
    failures: list[Failure],
    warnings: list[Failure],
    suggested_fp_to_move: str | None,
    strict: bool,
) -> None:
    if is_threshold_hard_fail(api_refs=api_refs, tbl_refs=tbl_refs, feature_points=feature_points):
        item = Failure(
            loc=str(story_file),
            problem=f"oversized story: api_refs={api_refs}, tbl_refs={tbl_refs}, feature_points={feature_points}",
            expected="api_refs<=5, tbl_refs<=10, feature_points<=12 (prefer smaller)",
            impact="story scope may exceed low-noise budget",
            fix="split this story into smaller stories in docs/split-plan-pack.json",
        )
        if strict:
            failures.append(item)
        else:
            warnings.append(item)
        return

    decision_hits = threshold_decision_hits(api_refs=api_refs, tbl_refs=tbl_refs, feature_points=feature_points)

    if len(decision_hits) >= 2:
        item = Failure(
            loc=str(story_file),
            problem=f"oversized story (warn escalation): {', '.join(decision_hits)}",
            expected="at most 1 warn-range hit per story",
            impact="story scope may exceed low-noise budget",
            fix="split this story into smaller stories in docs/split-plan-pack.json",
        )
        if strict:
            failures.append(item)
        else:
            warnings.append(item)
        return

    if len(decision_hits) == 1:
        hit = decision_hits[0]
        suggested_action = "consider reducing scope in this story"
        if hit.startswith("api_refs="):
            suggested_action = "move 1 API (and related FP) out of this story in docs/split-plan-pack.json (aim api_refs<=3)"
        elif hit.startswith("tbl_refs="):
            hint = f" (suggested: {suggested_fp_to_move})" if suggested_fp_to_move else ""
            suggested_action = (
                f"move 1 FP{hint} (and its DB landings) out of this story in docs/split-plan-pack.json (aim tbl_refs<=6)"
            )
        elif hit.startswith("feature_points="):
            hint = f" (suggested: {suggested_fp_to_move})" if suggested_fp_to_move else ""
            suggested_action = f"move 1 FP{hint} out of this story in docs/split-plan-pack.json (aim feature_points<=8)"
        warnings.append(
            Failure(
                loc=str(story_file),
                problem=f"threshold warning: {hit}",
                expected="stay under threshold warnings (prefer smaller stories)",
                impact="may increase iteration cost",
                fix=suggested_action,
            )
        )

