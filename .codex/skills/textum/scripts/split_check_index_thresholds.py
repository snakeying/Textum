from __future__ import annotations

from pathlib import Path
from typing import Any

from prd_pack_types import Failure


def evaluate_story_thresholds(
    *,
    story_file: Path,
    story_name: str,
    api_refs: int,
    tbl_refs: int,
    feature_points: int,
    failures: list[Failure],
    decisions: list[dict[str, Any]],
) -> None:
    if api_refs >= 6 or tbl_refs >= 11 or feature_points >= 13:
        failures.append(
            Failure(
                loc=str(story_file),
                problem=f"oversized story: api_refs={api_refs}, tbl_refs={tbl_refs}, feature_points={feature_points}",
                expected="api_refs<=5, tbl_refs<=10, feature_points<=12 (prefer smaller)",
                impact="split stage likely to fail downstream",
                fix="revise split plan to split/redistribute, then rerun split generate",
            )
        )
        return

    decision_hits: list[str] = []
    if api_refs in (4, 5):
        decision_hits.append(f"api_refs={api_refs} (4-5)")
    if 7 <= tbl_refs <= 10:
        decision_hits.append(f"tbl_refs={tbl_refs} (7-10)")
    if feature_points in (9, 10, 11, 12):
        decision_hits.append(f"feature_points={feature_points} (9-12)")

    if len(decision_hits) >= 2:
        failures.append(
            Failure(
                loc=str(story_file),
                problem=f"oversized story (DECISION escalation): {', '.join(decision_hits)}",
                expected="at most 1 DECISION-range hit per story",
                impact="split stage likely to fail downstream",
                fix="revise split plan to split/redistribute, then rerun split generate",
            )
        )
        return

    if len(decision_hits) == 1:
        decisions.append(
            {
                "story": story_name,
                "story_file": str(story_file.as_posix()),
                "decision": decision_hits[0],
                "suggested_action": "consider splitting or redistributing scope to reduce risk",
            }
        )

