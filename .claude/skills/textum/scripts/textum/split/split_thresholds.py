from __future__ import annotations

FAIL_MAX_API_REFS = 5
FAIL_MAX_TBL_REFS = 10
FAIL_MAX_FEATURE_POINTS = 12

DECISION_API_REFS = {4, 5}
DECISION_TBL_REFS_MIN = 7
DECISION_TBL_REFS_MAX = 10
DECISION_FEATURE_POINTS = {9, 10, 11, 12}


def is_threshold_hard_fail(*, api_refs: int, tbl_refs: int, feature_points: int) -> bool:
    return api_refs > FAIL_MAX_API_REFS or tbl_refs > FAIL_MAX_TBL_REFS or feature_points > FAIL_MAX_FEATURE_POINTS


def threshold_decision_hits(*, api_refs: int, tbl_refs: int, feature_points: int) -> list[str]:
    hits: list[str] = []
    if api_refs in DECISION_API_REFS:
        hits.append(f"api_refs={api_refs} (4-5)")
    if DECISION_TBL_REFS_MIN <= tbl_refs <= DECISION_TBL_REFS_MAX:
        hits.append(f"tbl_refs={tbl_refs} (7-10)")
    if feature_points in DECISION_FEATURE_POINTS:
        hits.append(f"feature_points={feature_points} (9-12)")
    return hits


def is_threshold_fail(*, api_refs: int, tbl_refs: int, feature_points: int) -> bool:
    if is_threshold_hard_fail(api_refs=api_refs, tbl_refs=tbl_refs, feature_points=feature_points):
        return True
    return len(threshold_decision_hits(api_refs=api_refs, tbl_refs=tbl_refs, feature_points=feature_points)) >= 2

