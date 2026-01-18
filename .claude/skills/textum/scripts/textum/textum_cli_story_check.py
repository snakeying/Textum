from __future__ import annotations

import argparse
from pathlib import Path

from textum.prd.prd_pack import read_prd_pack, workspace_paths
from textum.scaffold.scaffold_pack import check_scaffold_pack, read_scaffold_pack
from textum.story.story_check import check_story_source
from .textum_cli_emit import emit_stage_result
from .textum_cli_runner import check_stage_result
from .textum_cli_story_load import load_story_source
from .textum_cli_support import _ensure_prd_ready, _require_scaffold_extracted_modules_index


def _cmd_story_check(args: argparse.Namespace) -> int:
    workspace = Path(args.workspace).resolve()
    paths = workspace_paths(workspace)

    story_path, story_text, story, failures = load_story_source(stories_dir=paths["stories_dir"], n=args.n)
    if failures:
        result = check_stage_result(
            workspace_root=workspace,
            stage_id="story-check",
            command=f"uv run --project .claude/skills/textum/scripts textum story check --workspace {workspace.as_posix()} --n {args.n}",
            failures=failures,
            warnings=[],
            next_on_pass="Story Pack",
            fallback_on_fail="Split Generate",
        )
        emit_stage_result(result)
        return result.exit_code
    assert story_path is not None
    assert story_text is not None
    assert story is not None

    prd_pack, prd_failures = read_prd_pack(paths["prd_pack"])
    if prd_failures:
        result = check_stage_result(
            workspace_root=workspace,
            stage_id="story-check",
            command=f"uv run --project .claude/skills/textum/scripts textum story check --workspace {workspace.as_posix()} --n {args.n}",
            failures=prd_failures,
            warnings=[],
            next_on_pass="Story Pack",
            fallback_on_fail="Split Generate",
        )
        emit_stage_result(result)
        return result.exit_code
    assert prd_pack is not None

    prd_ready_failures = _ensure_prd_ready(prd_pack, prd_pack_path=paths["prd_pack"])
    if prd_ready_failures:
        result = check_stage_result(
            workspace_root=workspace,
            stage_id="story-check",
            command=f"uv run --project .claude/skills/textum/scripts textum story check --workspace {workspace.as_posix()} --n {args.n}",
            failures=prd_ready_failures,
            warnings=[],
            next_on_pass="Story Pack",
            fallback_on_fail="Split Generate",
        )
        emit_stage_result(result)
        return result.exit_code

    scaffold_pack, scaffold_failures = read_scaffold_pack(paths["scaffold_pack"])
    if scaffold_failures:
        result = check_stage_result(
            workspace_root=workspace,
            stage_id="story-check",
            command=f"uv run --project .claude/skills/textum/scripts textum story check --workspace {workspace.as_posix()} --n {args.n}",
            failures=scaffold_failures,
            warnings=[],
            next_on_pass="Story Pack",
            fallback_on_fail="Split Generate",
        )
        emit_stage_result(result)
        return result.exit_code
    assert scaffold_pack is not None

    scaffold_ready_failures = _require_scaffold_extracted_modules_index(scaffold_pack=scaffold_pack, prd_pack=prd_pack)
    if scaffold_ready_failures:
        result = check_stage_result(
            workspace_root=workspace,
            stage_id="story-check",
            command=f"uv run --project .claude/skills/textum/scripts textum story check --workspace {workspace.as_posix()} --n {args.n}",
            failures=scaffold_ready_failures,
            warnings=[],
            next_on_pass="Story Pack",
            fallback_on_fail="Split Generate",
        )
        emit_stage_result(result)
        return result.exit_code

    scaffold_ready, scaffold_check_failures = check_scaffold_pack(scaffold_pack)
    if not scaffold_ready:
        result = check_stage_result(
            workspace_root=workspace,
            stage_id="story-check",
            command=f"uv run --project .claude/skills/textum/scripts textum story check --workspace {workspace.as_posix()} --n {args.n}",
            failures=scaffold_check_failures,
            warnings=[],
            next_on_pass="Story Pack",
            fallback_on_fail="Split Generate",
        )
        emit_stage_result(result)
        return result.exit_code

    story_rel = story_path.relative_to(workspace).as_posix()
    failures = check_story_source(
        story_path=story_rel,
        story_text=story_text,
        story=story,
        n=args.n,
        max_lines=args.max_lines,
        max_chars=args.max_chars,
        prd_pack=prd_pack,
        scaffold_pack=scaffold_pack,
    )
    result = check_stage_result(
        workspace_root=workspace,
        stage_id="story-check",
        command=f"uv run --project .claude/skills/textum/scripts textum story check --workspace {workspace.as_posix()} --n {args.n}",
        failures=failures,
        warnings=[],
        next_on_pass="Story Pack",
        fallback_on_fail="Split Generate",
    )
    emit_stage_result(result)
    return result.exit_code
