from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any

from textum.prd.prd_pack_types import Failure
from textum.prd.prd_slices_types import SliceBudget
from textum.prd.prd_slices_utils import chunk_list, rel_posix
from .story_exec_pack_context import collect_story_prd_context
from .story_exec_pack_utils import scaffold_module_rows
from .story_exec_pack_write import (
    build_story_exec_source,
    write_story_exec_context_base,
    write_story_exec_context_parts,
    write_story_exec_index,
)
from .story_exec_pack_snapshot import write_story_snapshot_and_check_budget
from .story_exec_types import (
    STORY_EXEC_CONTEXT_BUSINESS_RULES_FILENAME,
    STORY_EXEC_CONTEXT_BUSINESS_RULES_SCHEMA_VERSION,
    STORY_EXEC_CONTEXT_TABLES_FILENAME,
    STORY_EXEC_CONTEXT_TABLES_SCHEMA_VERSION,
    STORY_EXEC_STORY_SNAPSHOT_FILENAME,
)


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

    story_snapshot_path, story_lines, story_chars, snapshot_failures = write_story_snapshot_and_check_budget(
        workspace_root=workspace_root,
        out_dir=out_dir,
        story_text=story_text,
        budget=budget,
    )
    if snapshot_failures:
        return None, [], snapshot_failures

    tables, business_rules, context_failures = collect_story_prd_context(
        story=story, prd_pack=prd_pack, story_source_path=story_source_path, workspace_root=workspace_root
    )
    if context_failures:
        return None, [], context_failures

    api_obj = prd_pack.get("api") if isinstance(prd_pack.get("api"), dict) else {}
    api_meta = dict(api_obj)
    api_meta["endpoints"] = []

    decisions = scaffold_pack.get("decisions") if isinstance(scaffold_pack.get("decisions"), dict) else {}
    extracted = scaffold_pack.get("extracted") if isinstance(scaffold_pack.get("extracted"), dict) else {}

    module_ids = story.get("modules") if isinstance(story.get("modules"), list) else []
    module_ids = [m for m in module_ids if isinstance(m, str)]
    modules_rows = scaffold_module_rows(scaffold_pack, module_ids=module_ids)

    source = build_story_exec_source(
        workspace_root=workspace_root,
        story_source_path=story_source_path,
        prd_pack_path=prd_pack_path,
        prd_pack=prd_pack,
        scaffold_pack_path=scaffold_pack_path,
        scaffold_pack=scaffold_pack,
    )

    base_path, base_lines, base_chars, base_failures = write_story_exec_context_base(
        out_dir=out_dir,
        workspace_root=workspace_root,
        budget=budget,
        source=source,
        extracted_project=extracted.get("project"),
        modules_rows=modules_rows,
        decisions=decisions,
        api_meta=api_meta,
    )
    if base_failures:
        return None, [], base_failures
    assert base_path is not None

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

    business_rules_paths, rules_files, rules_failures = write_story_exec_context_parts(
        out_dir=out_dir,
        workspace_root=workspace_root,
        budget=budget,
        parts=business_rules_parts,
        single_filename=STORY_EXEC_CONTEXT_BUSINESS_RULES_FILENAME,
        part_filename_fmt="context.business_rules.part-{idx:03d}.json",
        kind="context_business_rules",
        list_key="business_rules",
        budget_label="business rules context",
        budget_fix="reduce referenced business rules per story in docs/split-plan-pack.json",
    )
    if rules_failures:
        return None, [], rules_failures

    table_paths, table_files, table_failures2 = write_story_exec_context_parts(
        out_dir=out_dir,
        workspace_root=workspace_root,
        budget=budget,
        parts=table_parts,
        single_filename=STORY_EXEC_CONTEXT_TABLES_FILENAME,
        part_filename_fmt="context.tables.part-{idx:03d}.json",
        kind="context_tables",
        list_key="tables",
        budget_label="tables context",
        budget_fix="reduce referenced tables per story in docs/split-plan-pack.json",
    )
    if table_failures2:
        return None, [], table_failures2

    written.extend(business_rules_paths)
    written.extend(table_paths)
    files.extend(rules_files)
    files.extend(table_files)

    index_path, _, _, index_failures = write_story_exec_index(
        out_dir=out_dir,
        workspace_root=workspace_root,
        budget=budget,
        source=source,
        story=story,
        story_snapshot_path=story_snapshot_path,
        base_path=base_path,
        business_rules_paths=business_rules_paths,
        table_paths=table_paths,
        files=files,
    )
    if index_failures:
        return None, [], index_failures
    assert index_path is not None

    written.append(index_path)
    return out_dir, written, []


