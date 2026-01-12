from __future__ import annotations

from typing import Any


def build_split_replan_pack(*, index_pack: dict[str, Any]) -> dict[str, Any]:
    oversized: list[dict[str, Any]] = []
    for story in index_pack.get("stories", []):
        if not isinstance(story, dict):
            continue
        metrics = story.get("metrics")
        if not isinstance(metrics, dict):
            continue

        api_refs = metrics.get("api_refs")
        tbl_refs = metrics.get("tbl_refs")
        feature_points = metrics.get("feature_points")
        if not (isinstance(api_refs, int) and isinstance(tbl_refs, int) and isinstance(feature_points, int)):
            continue

        if api_refs >= 6 or tbl_refs >= 11 or feature_points >= 13:
            is_fail = True
        else:
            decision_hits = 0
            if api_refs in (4, 5):
                decision_hits += 1
            if 7 <= tbl_refs <= 10:
                decision_hits += 1
            if feature_points in (9, 10, 11, 12):
                decision_hits += 1
            is_fail = decision_hits >= 2

        if not is_fail:
            continue

        refs = story.get("refs") if isinstance(story.get("refs"), dict) else {}
        oversized.append(
            {
                "story": story.get("story"),
                "story_file": story.get("story_file"),
                "slug": story.get("slug"),
                "modules": story.get("modules"),
                "prereq_stories": story.get("prereq_stories"),
                "metrics": metrics,
                "prd_api_ids": refs.get("prd_api_ids", []),
            }
        )

    return {
        "SPLIT_REPLAN_PACK": "v1",
        "trigger": "oversized_story",
        "oversized_stories": oversized,
        "constraints": [
            "Insert new stories after the oversized one; prerequisites must remain executable (only depend on smaller n).",
            "Renumber to consecutive Story 1..N; update split-plan-pack stories/prereq/api_assignments accordingly.",
            "Each API must be assigned exactly once and kept consistent between split plan and generated stories.",
            "After splitting, every story must pass thresholds; otherwise split again.",
        ],
    }

