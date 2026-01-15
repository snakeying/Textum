from __future__ import annotations

from pathlib import Path
from typing import Any

from prd_pack_types import Failure
from split_thresholds import is_threshold_hard_fail, threshold_decision_hits


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
    if is_threshold_hard_fail(api_refs=api_refs, tbl_refs=tbl_refs, feature_points=feature_points):
        failures.append(
            Failure(
                loc=str(story_file),
                problem=f"oversized story: api_refs={api_refs}, tbl_refs={tbl_refs}, feature_points={feature_points}",
                expected="api_refs<=5, tbl_refs<=10, feature_points<=12 (prefer smaller)",
                impact="fails Split Check1 thresholds",
                fix="split this story into smaller stories in docs/split-plan-pack.json",
            )
        )
        return

    decision_hits = threshold_decision_hits(api_refs=api_refs, tbl_refs=tbl_refs, feature_points=feature_points)

    if len(decision_hits) >= 2:
        failures.append(
            Failure(
                loc=str(story_file),
                problem=f"oversized story (DECISION escalation): {', '.join(decision_hits)}",
                expected="at most 1 DECISION-range hit per story",
                impact="fails Split Check1 thresholds",
                fix="split this story into smaller stories in docs/split-plan-pack.json",
            )
        )
        return

    if len(decision_hits) == 1:
        decisions.append(
            {
                "story": story_name,
                "story_file": str(story_file.as_posix()),
                "decision": decision_hits[0],
                "suggested_action": "consider reducing scope in this story",
            }
        )
