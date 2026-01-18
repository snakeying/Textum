from __future__ import annotations

from pathlib import Path

from textum.prd.prd_pack_types import Failure


def validate_and_write_story_dependency_graph(
    *, story_numbers: list[int], prereq_by_n: dict[int, list[int]], out_path: Path
) -> list[Failure]:
    failures: list[Failure] = []
    all_set = set(story_numbers)

    edges: list[tuple[int, int]] = []
    for n in story_numbers:
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
    for n in story_numbers:
        lines.append(f'Story_{n}["Story {n}"]')
    for prereq_n, n in edges:
        lines.append(f"Story_{prereq_n} --> Story_{n}")
    lines.append("```")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return []
