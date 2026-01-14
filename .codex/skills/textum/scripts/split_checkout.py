from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from prd_pack_types import Failure
from split_pack_types import STORY_NAME_RE, STORY_SCHEMA_VERSION
from split_story_paths import iter_story_files, parse_story_filename


def _read_story_json(path: Path) -> tuple[dict[str, Any] | None, str | None, list[Failure]]:
    if not path.exists():
        return None, None, [
            Failure(
                loc=path.as_posix(),
                problem="file not found",
                expected="file exists",
                impact="cannot build dependency graph",
                fix="generate docs/stories/story-###-<slug>.json",
            )
        ]
    text = path.read_text(encoding="utf-8")
    try:
        obj = json.loads(text)
    except json.JSONDecodeError as error:
        return None, None, [
            Failure(
                loc=path.as_posix(),
                problem=f"invalid JSON: {error.msg} at line {error.lineno} col {error.colno}",
                expected="valid JSON document",
                impact="cannot build dependency graph",
                fix=f"fix JSON syntax in {path.as_posix()}",
            )
        ]
    if not isinstance(obj, dict):
        return None, None, [
            Failure(
                loc=path.as_posix(),
                problem=f"root must be object, got {type(obj).__name__}",
                expected="JSON object at root",
                impact="cannot build dependency graph",
                fix=f"rewrite {path.as_posix()} root as an object",
            )
        ]
    return obj, text, []


def write_story_dependency_mermaid(*, stories_dir: Path, out_path: Path) -> list[Failure]:
    story_files = iter_story_files(stories_dir)
    if not story_files:
        return [
            Failure(
                loc=stories_dir.as_posix(),
                problem="no story files found",
                expected="at least one docs/stories/story-###-<slug>.json",
                impact="cannot build dependency graph",
                fix="generate docs/stories/story-###-<slug>.json",
            )
        ]

    failures: list[Failure] = []
    story_by_n: dict[int, dict[str, Any]] = {}
    prereq_by_n: dict[int, list[int]] = {}

    for path in story_files:
        parsed = parse_story_filename(path.name)
        if parsed is None:
            continue
        file_n, file_slug = parsed
        story, _, read_failures = _read_story_json(path)
        if read_failures:
            failures += read_failures
            continue
        assert story is not None

        if story.get("schema_version") != STORY_SCHEMA_VERSION:
            failures.append(
                Failure(
                    loc=f"{path.as_posix()}:$.schema_version",
                    problem=f"schema_version must be {STORY_SCHEMA_VERSION}",
                    expected=STORY_SCHEMA_VERSION,
                    impact="cannot trust story format",
                    fix="regenerate docs/stories/",
                )
            )
            continue

        n = story.get("n")
        if not isinstance(n, int):
            failures.append(
                Failure(
                    loc=f"{path.as_posix()}:$.n",
                    problem=f"n must be integer, got {type(n).__name__}",
                    expected="integer",
                    impact="cannot build dependency graph",
                    fix="regenerate docs/stories/",
                )
            )
            continue
        if n != file_n:
            failures.append(
                Failure(
                    loc=f"{path.as_posix()}:$.n",
                    problem=f"n mismatch: file={file_n}, json={n}",
                    expected=f"{file_n}",
                    impact="cannot build dependency graph",
                    fix="regenerate docs/stories/",
                )
            )
            continue

        slug = story.get("slug")
        if not isinstance(slug, str) or slug != file_slug:
            failures.append(
                Failure(
                    loc=f"{path.as_posix()}:$.slug",
                    problem=f"slug mismatch: file={file_slug!r}, json={slug!r}",
                    expected=str(file_slug),
                    impact="cannot build dependency graph",
                    fix="regenerate docs/stories/",
                )
            )
            continue

        story_name = story.get("story")
        expected_story_name = f"Story {n}"
        if story_name != expected_story_name:
            failures.append(
                Failure(
                    loc=f"{path.as_posix()}:$.story",
                    problem=f"story must equal {expected_story_name}, got {story_name!r}",
                    expected=expected_story_name,
                    impact="cannot build dependency graph",
                    fix="regenerate docs/stories/",
                )
            )
            continue

        if n in story_by_n:
            failures.append(
                Failure(
                    loc=stories_dir.as_posix(),
                    problem=f"duplicate story number: {n}",
                    expected="unique story numbers",
                    impact="dependency graph ambiguous",
                    fix="regenerate docs/stories/",
                )
            )
            continue

        prereq_raw = story.get("prereq_stories")
        if not isinstance(prereq_raw, list):
            failures.append(
                Failure(
                    loc=f"{path.as_posix()}:$.prereq_stories",
                    problem=f"prereq_stories must be array, got {type(prereq_raw).__name__}",
                    expected="array of 'Story <number>' strings",
                    impact="cannot build dependency graph",
                    fix="regenerate docs/stories/",
                )
            )
            continue

        prereq_numbers: list[int] = []
        for idx, item in enumerate(prereq_raw):
            if not isinstance(item, str) or STORY_NAME_RE.match(item) is None:
                failures.append(
                    Failure(
                        loc=f"{path.as_posix()}:$.prereq_stories[{idx}]",
                        problem=f"invalid prereq story ref: {item!r}",
                        expected="Story <number>",
                        impact="cannot build dependency graph",
                        fix="regenerate docs/stories/",
                    )
                )
                continue
            prereq_numbers.append(int(STORY_NAME_RE.match(item).group(1)))

        if len(set(prereq_numbers)) != len(prereq_numbers):
            failures.append(
                Failure(
                    loc=f"{path.as_posix()}:$.prereq_stories",
                    problem="duplicate prereq stories",
                    expected="unique prereq story refs",
                    impact="dependency graph ambiguous",
                    fix="regenerate docs/stories/",
                )
            )
            continue

        story_by_n[n] = {"n": n, "story": expected_story_name}
        prereq_by_n[n] = prereq_numbers

    if failures:
        return failures

    all_numbers = sorted(story_by_n.keys())
    all_set = set(all_numbers)

    edges: list[tuple[int, int]] = []
    for n in all_numbers:
        prereqs = prereq_by_n.get(n, [])
        for prereq_n in prereqs:
            if prereq_n not in all_set:
                failures.append(
                    Failure(
                        loc=f"docs/stories/story-{n:03d}-*.json:$.prereq_stories",
                        problem=f"missing prereq story: Story {prereq_n}",
                        expected="every prereq story exists as a story file",
                        impact="dependency graph invalid",
                        fix="regenerate docs/stories/",
                    )
                )
                continue
            if prereq_n >= n:
                failures.append(
                    Failure(
                        loc=f"docs/stories/story-{n:03d}-*.json:$.prereq_stories",
                        problem=f"prereq story must be < {n}, got Story {prereq_n}",
                        expected="only earlier stories",
                        impact="dependency graph invalid",
                        fix="regenerate docs/stories/",
                    )
                )
                continue
            edges.append((prereq_n, n))

    if failures:
        return failures

    edges.sort(key=lambda e: (e[0], e[1]))

    lines: list[str] = []
    lines.append("# Story 依赖图")
    lines.append("")
    lines.append("```mermaid")
    lines.append("flowchart TD")
    for n in all_numbers:
        lines.append(f'Story_{n}["Story {n}"]')
    for prereq_n, n in edges:
        lines.append(f"Story_{prereq_n} --> Story_{n}")
    lines.append("```")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return []
