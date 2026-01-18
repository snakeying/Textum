from __future__ import annotations

from pathlib import Path
from typing import Any

from .prd_pack_types import Failure
from .split_thresholds import is_threshold_hard_fail, threshold_decision_hits


def evaluate_story_thresholds(
    *,
    story_file: Path,
    story_name: str,
    api_refs: int,
    tbl_refs: int,
    feature_points: int,
    failures: list[Failure],
    warnings: list[Failure],
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
            suggested_action = "move 1 FP (and its DB landings) out of this story in docs/split-plan-pack.json (aim tbl_refs<=6)"
        elif hit.startswith("feature_points="):
            suggested_action = "move 1 FP out of this story in docs/split-plan-pack.json (aim feature_points<=8)"
        warnings.append(
            Failure(
                loc=str(story_file),
                problem=f"threshold warning: {hit}",
                expected="stay under threshold warnings (prefer smaller stories)",
                impact="may increase iteration cost",
                fix=suggested_action,
            )
        )

