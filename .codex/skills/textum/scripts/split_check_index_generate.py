from __future__ import annotations

from pathlib import Path
from typing import Any

from prd_pack_types import API_ID_RE, Failure, FP_ID_RE, MODULE_ID_RE, TBL_ID_RE
from split_check_index_io import count_lines_chars, read_story
from split_check_index_thresholds import evaluate_story_thresholds
from split_pack_io import write_json
from split_pack_types import STORY_NAME_RE, STORY_SCHEMA_VERSION
from split_story_paths import iter_story_files, parse_story_filename, story_filename


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

        if data.get("schema_version") != STORY_SCHEMA_VERSION:
            failures.append(
                Failure(
                    loc=str(path),
                    problem=f"unexpected schema_version: {data.get('schema_version')!r}",
                    expected=STORY_SCHEMA_VERSION,
                    impact="cannot validate story",
                    fix=f"regenerate the story file {path.as_posix()}",
                )
            )
            continue

        story_name = data.get("story")
        n = data.get("n")
        slug = data.get("slug")
        if not isinstance(story_name, str) or STORY_NAME_RE.match(story_name) is None:
            failures.append(
                Failure(
                    loc=str(path),
                    problem=f"invalid story name: {story_name!r}",
                    expected="Story N",
                    impact="cannot validate story",
                    fix=f"regenerate the story file {path.as_posix()}",
                )
            )
            continue
        if not isinstance(n, int) or n <= 0:
            failures.append(
                Failure(
                    loc=str(path),
                    problem=f"invalid n: {n!r}",
                    expected="positive integer",
                    impact="cannot validate story",
                    fix=f"regenerate the story file {path.as_posix()}",
                )
            )
            continue
        if not isinstance(slug, str) or slug.strip() == "":
            failures.append(
                Failure(
                    loc=str(path),
                    problem=f"invalid slug: {slug!r}",
                    expected="non-empty kebab-case slug",
                    impact="cannot validate story",
                    fix=f"regenerate the story file {path.as_posix()}",
                )
            )
            continue

        parsed = parse_story_filename(path.name)
        if parsed is None or parsed[0] != n or parsed[1] != slug:
            failures.append(
                Failure(
                    loc=str(path),
                    problem=f"file name mismatch: {path.name}",
                    expected=story_filename(n, slug),
                    impact="cannot validate split output",
                    fix="regenerate docs/stories/",
                )
            )
            continue

        if story_name in seen_story_names:
            failures.append(
                Failure(
                    loc=str(path),
                    problem=f"duplicate story: {story_name}",
                    expected="unique story files",
                    impact="cannot validate split output",
                    fix="regenerate docs/stories/",
                )
            )
        seen_story_names.add(story_name)
        if n in seen_n:
            failures.append(
                Failure(
                    loc=str(path),
                    problem=f"duplicate story number: {n}",
                    expected="unique story numbers",
                    impact="cannot validate split output",
                    fix="regenerate docs/stories/",
                )
            )
        seen_n.add(n)

        if story_name not in plan_by_story:
            failures.append(
                Failure(
                    loc=str(path),
                    problem=f"story not found in split plan: {story_name}",
                    expected="story exists in split-plan-pack.json stories[]",
                    impact="stale story file",
                    fix="regenerate docs/stories/",
                )
            )
            continue

        plan = plan_by_story[story_name]
        plan_modules = plan.get("modules") if isinstance(plan.get("modules"), list) else []
        plan_prereq = plan.get("prereq_stories") if isinstance(plan.get("prereq_stories"), list) else []

        modules = data.get("modules") if isinstance(data.get("modules"), list) else []
        prereq = data.get("prereq_stories") if isinstance(data.get("prereq_stories"), list) else []

        modules_set = {m for m in modules if isinstance(m, str) and MODULE_ID_RE.match(m)}
        prereq_set = {p for p in prereq if isinstance(p, str) and p.strip()}
        if set(plan_modules) != modules_set:
            failures.append(
                Failure(
                    loc=str(path),
                    problem="modules mismatch vs split plan",
                    expected=f"modules == {sorted(set(plan_modules))}",
                    impact="split output diverges from plan",
                    fix="regenerate docs/stories/",
                )
            )
        if set(plan_prereq) != prereq_set:
            failures.append(
                Failure(
                    loc=str(path),
                    problem="prereq_stories mismatch vs split plan",
                    expected=f"prereq_stories == {sorted(set(plan_prereq))}",
                    impact="dependency graph diverges from plan",
                    fix="regenerate docs/stories/",
                )
            )

        fp_ids = data.get("fp_ids") if isinstance(data.get("fp_ids"), list) else []
        fp_set = {fp for fp in fp_ids if isinstance(fp, str) and FP_ID_RE.match(fp)}
        if len(fp_set) == 0:
            failures.append(
                Failure(
                    loc=str(path),
                    problem="fp_ids is empty",
                    expected="at least 1 FP-###",
                    impact="story has no scope",
                    fix="fix docs/split-plan-pack.json stories[].modules mapping",
                )
            )

        refs = data.get("refs") if isinstance(data.get("refs"), dict) else {}
        api_ids = refs.get("prd_api") if isinstance(refs.get("prd_api"), list) else []
        tbl_ids = refs.get("prd_tbl") if isinstance(refs.get("prd_tbl"), list) else []
        api_set = {a for a in api_ids if isinstance(a, str) and API_ID_RE.match(a)}
        tbl_set = {t for t in tbl_ids if isinstance(t, str) and TBL_ID_RE.match(t)}

        fp_union |= fp_set
        api_union |= api_set
        tbl_union |= tbl_set
        module_union |= modules_set

        api_refs = len(api_set)
        tbl_refs = len(tbl_set)
        feature_points = len(fp_set)

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
                    fix="revise docs/split-plan-pack.json to split/redistribute scope",
                )
            )

        stories_index.append(
            {
                "story": story_name,
                "n": n,
                "slug": slug,
                "story_file": str(path.as_posix()),
                "modules": sorted(modules_set),
                "prereq_stories": sorted(prereq_set),
                "metrics": {
                    "api_refs": api_refs,
                    "tbl_refs": tbl_refs,
                    "feature_points": feature_points,
                },
                "refs": {
                    "fp_ids": sorted(fp_set),
                    "prd_api_ids": sorted(api_set),
                    "prd_tbl_ids": sorted(tbl_set),
                    "prd_br_ids": [],
                    "gc_br_ids": [],
                },
            }
        )

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
