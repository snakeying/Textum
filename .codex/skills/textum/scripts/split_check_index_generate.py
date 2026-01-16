from __future__ import annotations

from pathlib import Path
from typing import Any

from prd_pack_types import Failure
from split_check_index_io import count_lines_chars, read_story
from split_check_index_story import collect_story_index_row
from split_check_index_thresholds import evaluate_story_thresholds
from split_pack_io import write_json
from split_story_paths import iter_story_files


def generate_split_check_index_pack(
    *,
    split_plan_pack_path: Path,
    split_plan_pack: dict[str, Any],
    stories_dir: Path,
    out_path: Path,
    max_story_lines: int,
    max_story_chars: int,
) -> tuple[dict[str, Any] | None, list[Failure], list[dict[str, Any]]]:
    failures: list[Failure] = []
    decisions: list[dict[str, Any]] = []

    stories_plan = split_plan_pack.get("stories") if isinstance(split_plan_pack.get("stories"), list) else []
    plan_by_story: dict[str, dict[str, Any]] = {}
    for item in stories_plan:
        if not isinstance(item, dict):
            continue
        name = item.get("story")
        if isinstance(name, str):
            plan_by_story[name] = item

    story_files = iter_story_files(stories_dir)
    if len(story_files) == 0:
        failures.append(
            Failure(
                loc=str(stories_dir),
                problem="no story files found",
                expected="at least 1 story-###-<slug>.json",
                impact="cannot validate split output",
                fix="generate docs/stories/story-###-<slug>.json",
            )
        )
        return None, failures, decisions

    stories_index: list[dict[str, Any]] = []

    fp_union: set[str] = set()
    api_union: set[str] = set()
    tbl_union: set[str] = set()
    module_union: set[str] = set()

    seen_story_names: set[str] = set()
    seen_n: set[int] = set()

    for path in story_files:
        data, read_failures = read_story(path)
        if read_failures:
            failures.extend(read_failures)
            continue
        assert data is not None

        index_row, meta = collect_story_index_row(
            path=path,
            data=data,
            plan_by_story=plan_by_story,
            seen_story_names=seen_story_names,
            seen_n=seen_n,
            failures=failures,
        )
        if index_row is None:
            continue

        story_name = meta.get("story_name")
        api_set = meta.get("api_set")
        tbl_set = meta.get("tbl_set")
        fp_set = meta.get("fp_set")
        modules_set = meta.get("modules_set")
        api_refs = meta.get("api_refs")
        tbl_refs = meta.get("tbl_refs")
        feature_points = meta.get("feature_points")
        if not (
            isinstance(story_name, str)
            and isinstance(api_set, set)
            and isinstance(tbl_set, set)
            and isinstance(fp_set, set)
            and isinstance(modules_set, set)
            and isinstance(api_refs, int)
            and isinstance(tbl_refs, int)
            and isinstance(feature_points, int)
        ):
            failures.append(
                Failure(
                    loc=str(path),
                    problem="internal error: invalid split check story meta",
                    expected="valid meta dict",
                    impact="cannot validate split output",
                    fix="fix split_check_index_story.collect_story_index_row return type",
                )
            )
            continue

        fp_union |= fp_set
        api_union |= api_set
        tbl_union |= tbl_set
        module_union |= modules_set

        evaluate_story_thresholds(
            story_file=path,
            story_name=story_name,
            api_refs=api_refs,
            tbl_refs=tbl_refs,
            feature_points=feature_points,
            failures=failures,
            decisions=decisions,
        )

        lines, chars = count_lines_chars(path)
        if lines > max_story_lines or chars > max_story_chars:
            failures.append(
                Failure(
                    loc=str(path),
                    problem=f"story file too large: lines={lines}, chars={chars}",
                    expected=f"lines<={max_story_lines} and chars<={max_story_chars}",
                    impact="noise budget exceeded",
                    fix="split this story into smaller stories in docs/split-plan-pack.json",
                )
            )

        stories_index.append(index_row)

    api_assignment_count = len(split_plan_pack.get("api_assignments") or []) if isinstance(split_plan_pack, dict) else 0

    index_pack: dict[str, Any] = {
        "schema_version": "split-check-index-pack@v1",
        "source": {
            "split_plan_pack_path": str(split_plan_pack_path.as_posix()),
            "stories_dir": str(stories_dir.as_posix()),
        },
        "split_plan": {
            "story_count": len(stories_plan),
            "api_assignment_count": api_assignment_count,
        },
        "stories": sorted(stories_index, key=lambda s: s["n"]),
        "summary": {
            "story_count": len(stories_index),
            "refs": {
                "fp_ids": sorted(fp_union),
                "prd_api_ids": sorted(api_union),
                "prd_tbl_ids": sorted(tbl_union),
                "prd_br_ids": [],
                "gc_br_ids": [],
            },
            "modules": sorted(module_union),
        },
    }

    if failures:
        return index_pack, failures, decisions

    write_json(out_path, index_pack)
    return index_pack, [], decisions

