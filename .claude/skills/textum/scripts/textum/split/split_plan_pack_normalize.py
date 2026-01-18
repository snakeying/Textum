from __future__ import annotations

from pathlib import Path
from typing import Any

from textum.prd.prd_pack_types import Failure


def normalize_split_plan_pack(
    split_plan_pack: dict[str, Any],
    *,
    workspace_root: Path,
    prd_pack_path: Path,
    scaffold_pack_path: Path,
) -> tuple[bool, list[Failure]]:
    updated = False
    failures: list[Failure] = []

    if split_plan_pack.get("schema_version") != "split-plan-pack@v1":
        split_plan_pack["schema_version"] = "split-plan-pack@v1"
        updated = True

    def _rel(path: Path) -> str:
        try:
            return path.resolve().relative_to(workspace_root.resolve()).as_posix()
        except Exception:
            return path.as_posix()

    source = split_plan_pack.get("source")
    if not isinstance(source, dict):
        source = {}
        split_plan_pack["source"] = source
        updated = True

    desired_source = {
        "prd_pack_path": _rel(prd_pack_path),
        "scaffold_pack_path": _rel(scaffold_pack_path),
    }
    if source != desired_source:
        split_plan_pack["source"] = desired_source
        updated = True

    stories = split_plan_pack.get("stories")
    if isinstance(stories, list):
        for story_obj in stories:
            if not isinstance(story_obj, dict):
                continue
            n = story_obj.get("n")
            if isinstance(n, int) and n > 0:
                desired_story = f"Story {n}"
                if story_obj.get("story") != desired_story:
                    story_obj["story"] = desired_story
                    updated = True
            for key in ("slug", "goal"):
                value = story_obj.get(key)
                if isinstance(value, str) and value != value.strip():
                    story_obj[key] = value.strip()
                    updated = True
            prereq = story_obj.get("prereq_stories")
            if isinstance(prereq, list):
                trimmed: list[str] = []
                for item in prereq:
                    if not isinstance(item, str):
                        continue
                    trimmed.append(item.strip())
                if prereq != trimmed:
                    story_obj["prereq_stories"] = trimmed
                    updated = True

    api_assignments = split_plan_pack.get("api_assignments")
    if isinstance(api_assignments, list):
        for row in api_assignments:
            if not isinstance(row, dict):
                continue
            for key in ("api", "story"):
                value = row.get(key)
                if isinstance(value, str) and value != value.strip():
                    row[key] = value.strip()
                    updated = True

    return updated, failures


