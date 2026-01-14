from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any

from prd_pack_types import Failure
from prd_slices_types import SliceBudget
from prd_slices_utils import chunk_list, measure_json, rel_posix, sha256_file, write_json
from story_exec_types import (
    STORY_EXEC_CONTEXT_BASE_FILENAME,
    STORY_EXEC_CONTEXT_BASE_SCHEMA_VERSION,
    STORY_EXEC_CONTEXT_BUSINESS_RULES_FILENAME,
    STORY_EXEC_CONTEXT_BUSINESS_RULES_SCHEMA_VERSION,
    STORY_EXEC_CONTEXT_TABLES_FILENAME,
    STORY_EXEC_CONTEXT_TABLES_SCHEMA_VERSION,
    STORY_EXEC_INDEX_FILENAME,
    STORY_EXEC_INDEX_SCHEMA_VERSION,
    STORY_EXEC_STORY_SNAPSHOT_FILENAME,
)
from prd_pack_maps import build_prd_maps
from story_exec_pack_utils import scaffold_module_rows

def write_story_exec_pack(
    *,
    workspace_root: Path,
    story_source_path: Path,
    story_text: str,
    story: dict[str, Any],
    prd_pack_path: Path,
    prd_pack: dict[str, Any],
    scaffold_pack_path: Path,
    scaffold_pack: dict[str, Any],
    out_dir: Path,
    budget: SliceBudget,
    clean: bool,
) -> tuple[Path | None, list[Path], list[Failure]]:
    if clean and out_dir.exists():
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    story_snapshot_path = out_dir / STORY_EXEC_STORY_SNAPSHOT_FILENAME
    story_snapshot_path.write_text(story_text, encoding="utf-8")
    story_lines = story_text.count("\n")
    story_chars = len(story_text)
    if story_lines > budget.max_lines or story_chars > budget.max_chars:
        return (
            None,
            [],
            [
                Failure(
                    loc=rel_posix(story_snapshot_path, workspace_root),
                    problem=f"story snapshot exceeds budget: {story_lines} lines, {story_chars} chars",
                    expected=f"<= {budget.max_lines} lines and <= {budget.max_chars} chars",
                    impact="cannot produce low-noise story exec pack",
                    fix="split this story into smaller stories in docs/split-plan-pack.json",
                )
            ],
        )

    story_refs = story.get("refs") if isinstance(story.get("refs"), dict) else {}
    prd_tbl_ids = story_refs.get("prd_tbl") if isinstance(story_refs.get("prd_tbl"), list) else []
    prd_br_ids = story_refs.get("prd_br") if isinstance(story_refs.get("prd_br"), list) else []

    _, tbl_by_id, _, br_by_id = build_prd_maps(prd_pack)

    tables: list[dict[str, Any]] = []
    for idx, tbl_id in enumerate(prd_tbl_ids):
        if not isinstance(tbl_id, str):
            continue
        row = tbl_by_id.get(tbl_id)
        if not isinstance(row, dict):
            return (
                None,
                [],
                [
                    Failure(
                        loc=f"$.refs.prd_tbl[{idx}]",
                        problem=f"unknown table id in PRD: {tbl_id}",
                        expected="table id exists in docs/prd-pack.json data_model.tables[]",
                        impact="cannot build exec context",
                        fix=f"regenerate {rel_posix(story_source_path, workspace_root)}",
                    )
                ],
            )
        tables.append(row)

    business_rules: list[dict[str, Any]] = []
    for idx, br_id in enumerate(prd_br_ids):
        if not isinstance(br_id, str):
            continue
        row = br_by_id.get(br_id)
        if not isinstance(row, dict):
            return (
                None,
                [],
                [
                    Failure(
                        loc=f"$.refs.prd_br[{idx}]",
                        problem=f"unknown BR id in PRD: {br_id}",
                        expected="BR id exists in docs/prd-pack.json business_rules[]",
                        impact="cannot build exec context",
                        fix=f"regenerate {rel_posix(story_source_path, workspace_root)}",
                    )
                ],
            )
        business_rules.append(row)

    api_obj = prd_pack.get("api") if isinstance(prd_pack.get("api"), dict) else {}
    api_meta = dict(api_obj)
    api_meta["endpoints"] = []

    decisions = scaffold_pack.get("decisions") if isinstance(scaffold_pack.get("decisions"), dict) else {}
    extracted = scaffold_pack.get("extracted") if isinstance(scaffold_pack.get("extracted"), dict) else {}

    module_ids = story.get("modules") if isinstance(story.get("modules"), list) else []
    module_ids = [m for m in module_ids if isinstance(m, str)]
    modules_rows = scaffold_module_rows(scaffold_pack, module_ids=module_ids)

    source = {
        "story_source_path": rel_posix(story_source_path, workspace_root),
        "story_source_sha256": sha256_file(story_source_path),
        "prd_pack_path": rel_posix(prd_pack_path, workspace_root),
        "prd_pack_schema_version": prd_pack.get("schema_version"),
        "prd_pack_sha256": sha256_file(prd_pack_path) if prd_pack_path.exists() else None,
        "scaffold_pack_path": rel_posix(scaffold_pack_path, workspace_root),
        "scaffold_pack_schema_version": scaffold_pack.get("schema_version"),
        "scaffold_pack_sha256": sha256_file(scaffold_pack_path) if scaffold_pack_path.exists() else None,
    }

    base_obj: dict[str, Any] = {
        "schema_version": STORY_EXEC_CONTEXT_BASE_SCHEMA_VERSION,
        "source": source,
        "budget": {"max_lines": budget.max_lines, "max_chars": budget.max_chars},
        "project": extracted.get("project"),
        "modules": modules_rows,
        "tech_stack": decisions.get("tech_stack"),
        "repo_structure": decisions.get("repo_structure"),
        "coding_conventions": decisions.get("coding_conventions"),
        "validation_commands": decisions.get("validation_commands"),
        "api_meta": api_meta,
    }
    base_path = out_dir / STORY_EXEC_CONTEXT_BASE_FILENAME
    base_lines, base_chars = write_json(base_path, base_obj)
    if base_lines > budget.max_lines or base_chars > budget.max_chars:
        base_candidates = {
            k: v for k, v in base_obj.items() if k not in {"schema_version", "source", "budget"}
        }
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
            [],
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

    def build_business_rules_obj(part_items: list[Any]) -> dict[str, Any]:
        return {
            "schema_version": STORY_EXEC_CONTEXT_BUSINESS_RULES_SCHEMA_VERSION,
            "source": source,
            "business_rules": part_items,
        }

    business_rules_parts, business_rules_failures = chunk_list(
        business_rules,
        build_business_rules_obj,
        budget=budget,
        loc="$.context.business_rules",
        item_label="business_rule",
    )
    if business_rules_failures:
        return None, [], business_rules_failures

    def build_tables_obj(part_items: list[Any]) -> dict[str, Any]:
        return {
            "schema_version": STORY_EXEC_CONTEXT_TABLES_SCHEMA_VERSION,
            "source": source,
            "tables": part_items,
        }

    table_parts, table_failures = chunk_list(
        tables,
        build_tables_obj,
        budget=budget,
        loc="$.context.tables",
        item_label="table",
    )
    if table_failures:
        return None, [], table_failures

    written: list[Path] = [story_snapshot_path, base_path]
    business_rules_paths: list[Path] = []
    table_paths: list[Path] = []
    files: list[dict[str, Any]] = [
        {
            "kind": "story",
            "path": rel_posix(story_snapshot_path, workspace_root),
            "lines": story_lines,
            "chars": story_chars,
        },
        {
            "kind": "context_base",
            "path": rel_posix(base_path, workspace_root),
            "lines": base_lines,
            "chars": base_chars,
        },
    ]

    for idx, part_obj in enumerate(business_rules_parts, start=1):
        if len(business_rules_parts) == 1:
            filename = STORY_EXEC_CONTEXT_BUSINESS_RULES_FILENAME
        else:
            filename = f"context.business_rules.part-{idx:03d}.json"
        path = out_dir / filename
        lines, chars = write_json(path, part_obj)
        if lines > budget.max_lines or chars > budget.max_chars:
            return (
                None,
                [],
                [
                    Failure(
                        loc=rel_posix(path, workspace_root),
                        problem=f"business rules context exceeds budget: {lines} lines, {chars} chars",
                        expected=f"<= {budget.max_lines} lines and <= {budget.max_chars} chars",
                        impact="cannot produce low-noise story exec pack",
                        fix="reduce referenced business rules per story in docs/split-plan-pack.json",
                    )
                ],
            )
        business_rules_paths.append(path)
        written.append(path)
        rules_in_part = (
            part_obj.get("business_rules", []) if isinstance(part_obj.get("business_rules"), list) else []
        )
        rule_ids = [r.get("id") for r in rules_in_part if isinstance(r, dict)]
        files.append(
            {
                "kind": "context_business_rules",
                "path": rel_posix(path, workspace_root),
                "lines": lines,
                "chars": chars,
                "count": len(rule_ids),
                "ids": [r for r in rule_ids if isinstance(r, str)],
            }
        )

    for idx, part_obj in enumerate(table_parts, start=1):
        if len(table_parts) == 1:
            filename = STORY_EXEC_CONTEXT_TABLES_FILENAME
        else:
            filename = f"context.tables.part-{idx:03d}.json"
        path = out_dir / filename
        lines, chars = write_json(path, part_obj)
        if lines > budget.max_lines or chars > budget.max_chars:
            return (
                None,
                [],
                [
                    Failure(
                        loc=rel_posix(path, workspace_root),
                        problem=f"tables context exceeds budget: {lines} lines, {chars} chars",
                        expected=f"<= {budget.max_lines} lines and <= {budget.max_chars} chars",
                        impact="cannot produce low-noise story exec pack",
                        fix="reduce referenced tables per story in docs/split-plan-pack.json",
                    )
                ],
            )
        table_paths.append(path)
        written.append(path)
        tables_in_part = part_obj.get("tables", []) if isinstance(part_obj.get("tables"), list) else []
        table_ids = [t.get("id") for t in tables_in_part if isinstance(t, dict)]
        files.append(
            {
                "kind": "context_tables",
                "path": rel_posix(path, workspace_root),
                "lines": lines,
                "chars": chars,
                "count": len(table_ids),
                "ids": [t for t in table_ids if isinstance(t, str)],
            }
        )

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
    if index_lines > budget.max_lines or index_chars > budget.max_chars:
        return (
            None,
            [],
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
    written.append(index_path)

    return out_dir, written, []
