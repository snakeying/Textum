from __future__ import annotations

from pathlib import Path
from typing import Any

from prd_pack_types import Failure
from prd_slices_types import SliceBudget
from prd_slices_utils import measure_json, rel_posix, sha256_file, write_json
from story_exec_types import (
    STORY_EXEC_CONTEXT_BASE_FILENAME,
    STORY_EXEC_CONTEXT_BASE_SCHEMA_VERSION,
    STORY_EXEC_INDEX_FILENAME,
    STORY_EXEC_INDEX_SCHEMA_VERSION,
)


def build_story_exec_source(
    *,
    workspace_root: Path,
    story_source_path: Path,
    prd_pack_path: Path,
    prd_pack: dict[str, Any],
    scaffold_pack_path: Path,
    scaffold_pack: dict[str, Any],
) -> dict[str, Any]:
    return {
        "story_source_path": rel_posix(story_source_path, workspace_root),
        "story_source_sha256": sha256_file(story_source_path),
        "prd_pack_path": rel_posix(prd_pack_path, workspace_root),
        "prd_pack_schema_version": prd_pack.get("schema_version"),
        "prd_pack_sha256": sha256_file(prd_pack_path) if prd_pack_path.exists() else None,
        "scaffold_pack_path": rel_posix(scaffold_pack_path, workspace_root),
        "scaffold_pack_schema_version": scaffold_pack.get("schema_version"),
        "scaffold_pack_sha256": sha256_file(scaffold_pack_path) if scaffold_pack_path.exists() else None,
    }


def write_story_exec_context_base(
    *,
    out_dir: Path,
    workspace_root: Path,
    budget: SliceBudget,
    source: dict[str, Any],
    extracted_project: Any,
    modules_rows: list[dict[str, Any]],
    decisions: dict[str, Any],
    api_meta: dict[str, Any],
) -> tuple[Path | None, int, int, list[Failure]]:
    base_obj: dict[str, Any] = {
        "schema_version": STORY_EXEC_CONTEXT_BASE_SCHEMA_VERSION,
        "source": source,
        "budget": {"max_lines": budget.max_lines, "max_chars": budget.max_chars},
        "project": extracted_project,
        "modules": modules_rows,
        "tech_stack": decisions.get("tech_stack"),
        "repo_structure": decisions.get("repo_structure"),
        "coding_conventions": decisions.get("coding_conventions"),
        "validation_commands": decisions.get("validation_commands"),
        "api_meta": api_meta,
    }
    base_path = out_dir / STORY_EXEC_CONTEXT_BASE_FILENAME
    base_lines, base_chars = write_json(base_path, base_obj)
    if base_lines <= budget.max_lines and base_chars <= budget.max_chars:
        return base_path, base_lines, base_chars, []

    base_candidates = {k: v for k, v in base_obj.items() if k not in {"schema_version", "source", "budget"}}
    largest_key: str | None = None
    largest_chars: int = -1
    for key, value in base_candidates.items():
        _, chars = measure_json({key: value})
        if chars > largest_chars:
            largest_key = key
            largest_chars = chars
    key_loc = (
        f"{rel_posix(base_path, workspace_root)}:$.{largest_key}"
        if isinstance(largest_key, str) and largest_key
        else rel_posix(base_path, workspace_root)
    )
    key_fix_map: dict[str, str] = {
        "tech_stack": "reduce docs/scaffold-pack.json:$.decisions.tech_stack",
        "repo_structure": "reduce docs/scaffold-pack.json:$.decisions.repo_structure",
        "coding_conventions": "reduce docs/scaffold-pack.json:$.decisions.coding_conventions",
        "validation_commands": "reduce docs/scaffold-pack.json:$.decisions.validation_commands",
        "modules": "reduce this story's modules in docs/split-plan-pack.json",
    }
    key_hint = f" (largest field: {largest_key})" if isinstance(largest_key, str) and largest_key else ""
    fix = key_fix_map.get(str(largest_key), "reduce scaffold/prd context included in the exec pack")
    return (
        None,
        base_lines,
        base_chars,
        [
            Failure(
                loc=key_loc,
                problem=f"context base exceeds budget: {base_lines} lines, {base_chars} chars{key_hint}",
                expected=f"<= {budget.max_lines} lines and <= {budget.max_chars} chars",
                impact="cannot produce low-noise story exec pack",
                fix=fix,
            )
        ],
    )


def write_story_exec_context_parts(
    *,
    out_dir: Path,
    workspace_root: Path,
    budget: SliceBudget,
    parts: list[dict[str, Any]],
    single_filename: str,
    part_filename_fmt: str,
    kind: str,
    list_key: str,
    budget_label: str,
    budget_fix: str,
) -> tuple[list[Path], list[dict[str, Any]], list[Failure]]:
    paths: list[Path] = []
    files: list[dict[str, Any]] = []
    for idx, part_obj in enumerate(parts, start=1):
        if len(parts) == 1:
            filename = single_filename
        else:
            filename = part_filename_fmt.format(idx=idx)
        path = out_dir / filename
        lines, chars = write_json(path, part_obj)
        if lines > budget.max_lines or chars > budget.max_chars:
            return (
                [],
                [],
                [
                    Failure(
                        loc=rel_posix(path, workspace_root),
                        problem=f"{budget_label} exceeds budget: {lines} lines, {chars} chars",
                        expected=f"<= {budget.max_lines} lines and <= {budget.max_chars} chars",
                        impact="cannot produce low-noise story exec pack",
                        fix=budget_fix,
                    )
                ],
            )
        paths.append(path)

        items = part_obj.get(list_key, []) if isinstance(part_obj.get(list_key), list) else []
        ids = [r.get("id") for r in items if isinstance(r, dict)]
        files.append(
            {
                "kind": kind,
                "path": rel_posix(path, workspace_root),
                "lines": lines,
                "chars": chars,
                "count": len(ids),
                "ids": [r for r in ids if isinstance(r, str)],
            }
        )
    return paths, files, []


def write_story_exec_index(
    *,
    out_dir: Path,
    workspace_root: Path,
    budget: SliceBudget,
    source: dict[str, Any],
    story: dict[str, Any],
    story_snapshot_path: Path,
    base_path: Path,
    business_rules_paths: list[Path],
    table_paths: list[Path],
    files: list[dict[str, Any]],
) -> tuple[Path | None, int, int, list[Failure]]:
    index_obj = {
        "schema_version": STORY_EXEC_INDEX_SCHEMA_VERSION,
        "source": source,
        "budget": {"max_lines": budget.max_lines, "max_chars": budget.max_chars},
        "story": {
            "n": story.get("n"),
            "slug": story.get("slug"),
            "title": story.get("title"),
        },
        "read": [rel_posix(story_snapshot_path, workspace_root), rel_posix(base_path, workspace_root)]
        + [rel_posix(p, workspace_root) for p in business_rules_paths]
        + [rel_posix(p, workspace_root) for p in table_paths],
        "files": files,
    }
    index_path = out_dir / STORY_EXEC_INDEX_FILENAME
    index_lines, index_chars = write_json(index_path, index_obj)
    if index_lines <= budget.max_lines and index_chars <= budget.max_chars:
        return index_path, index_lines, index_chars, []

    return (
        None,
        index_lines,
        index_chars,
        [
            Failure(
                loc=rel_posix(index_path, workspace_root),
                problem=f"index exceeds budget: {index_lines} lines, {index_chars} chars",
                expected=f"<= {budget.max_lines} lines and <= {budget.max_chars} chars",
                impact="cannot produce low-noise story exec pack",
                fix="reduce metadata in index.json",
            )
        ],
    )

