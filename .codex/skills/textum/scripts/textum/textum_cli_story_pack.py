from __future__ import annotations

import argparse
from pathlib import Path

from .prd_pack import read_prd_pack, workspace_paths
from .prd_slices_types import SliceBudget
from .scaffold_pack import check_scaffold_pack, read_scaffold_pack
from .story_check import check_story_source
from .story_exec_pack import write_story_exec_pack
from .story_exec_pack_validate import check_story_exec_pack
from .story_exec_paths import story_exec_dir
from .textum_cli_emit import emit_stage_result
from .textum_cli_runner import check_stage_result
from .textum_cli_story_load import load_story_source
from .textum_cli_support import _ensure_prd_ready, _require_scaffold_extracted_modules_index


def _cmd_story_pack(args: argparse.Namespace) -> int:
    workspace = Path(args.workspace).resolve()
    paths = workspace_paths(workspace)

    story_path, story_text, story, failures = load_story_source(stories_dir=paths["stories_dir"], n=args.n)
    if failures:
        result = check_stage_result(
            workspace_root=workspace,
            stage_id="story-pack",
            command=f"uv run --project .codex/skills/textum/scripts textum story pack --workspace {workspace.as_posix()} --n {args.n}",
            failures=failures,
            warnings=[],
            next_on_pass="Story Exec",
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
            stage_id="story-pack",
            command=f"uv run --project .codex/skills/textum/scripts textum story pack --workspace {workspace.as_posix()} --n {args.n}",
            failures=prd_failures,
            warnings=[],
            next_on_pass="Story Exec",
            fallback_on_fail="Split Generate",
        )
        emit_stage_result(result)
        return result.exit_code
    assert prd_pack is not None

    prd_ready_failures = _ensure_prd_ready(prd_pack, prd_pack_path=paths["prd_pack"])
    if prd_ready_failures:
        result = check_stage_result(
            workspace_root=workspace,
            stage_id="story-pack",
            command=f"uv run --project .codex/skills/textum/scripts textum story pack --workspace {workspace.as_posix()} --n {args.n}",
            failures=prd_ready_failures,
            warnings=[],
            next_on_pass="Story Exec",
            fallback_on_fail="Split Generate",
        )
        emit_stage_result(result)
        return result.exit_code

    scaffold_pack, scaffold_failures = read_scaffold_pack(paths["scaffold_pack"])
    if scaffold_failures:
        result = check_stage_result(
            workspace_root=workspace,
            stage_id="story-pack",
            command=f"uv run --project .codex/skills/textum/scripts textum story pack --workspace {workspace.as_posix()} --n {args.n}",
            failures=scaffold_failures,
            warnings=[],
            next_on_pass="Story Exec",
            fallback_on_fail="Split Generate",
        )
        emit_stage_result(result)
        return result.exit_code
    assert scaffold_pack is not None

    scaffold_ready_failures = _require_scaffold_extracted_modules_index(scaffold_pack=scaffold_pack, prd_pack=prd_pack)
    if scaffold_ready_failures:
        result = check_stage_result(
            workspace_root=workspace,
            stage_id="story-pack",
            command=f"uv run --project .codex/skills/textum/scripts textum story pack --workspace {workspace.as_posix()} --n {args.n}",
            failures=scaffold_ready_failures,
            warnings=[],
            next_on_pass="Story Exec",
            fallback_on_fail="Split Generate",
        )
        emit_stage_result(result)
        return result.exit_code

    scaffold_ready, scaffold_check_failures = check_scaffold_pack(scaffold_pack)
    if not scaffold_ready:
        result = check_stage_result(
            workspace_root=workspace,
            stage_id="story-pack",
            command=f"uv run --project .codex/skills/textum/scripts textum story pack --workspace {workspace.as_posix()} --n {args.n}",
            failures=scaffold_check_failures,
            warnings=[],
            next_on_pass="Story Exec",
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
    if failures:
        result = check_stage_result(
            workspace_root=workspace,
            stage_id="story-pack",
            command=f"uv run --project .codex/skills/textum/scripts textum story pack --workspace {workspace.as_posix()} --n {args.n}",
            failures=failures,
            warnings=[],
            next_on_pass="Story Exec",
            fallback_on_fail="Split Generate",
        )
        emit_stage_result(result)
        return result.exit_code

    exec_dir = story_exec_dir(paths["docs_dir"], story_source=story_path)
    budget = SliceBudget(max_lines=args.max_lines, max_chars=args.max_chars)
    out_dir, _, pack_failures = write_story_exec_pack(
        workspace_root=workspace,
        story_source_path=story_path,
        story_text=story_text,
        story=story,
        prd_pack_path=paths["prd_pack"],
        prd_pack=prd_pack,
        scaffold_pack_path=paths["scaffold_pack"],
        scaffold_pack=scaffold_pack,
        out_dir=exec_dir,
        budget=budget,
        clean=args.clean,
    )
    if pack_failures:
        result = check_stage_result(
            workspace_root=workspace,
            stage_id="story-pack",
            command=f"uv run --project .codex/skills/textum/scripts textum story pack --workspace {workspace.as_posix()} --n {args.n}",
            failures=pack_failures,
            warnings=[],
            next_on_pass="Story Exec",
            fallback_on_fail="Split Generate",
        )
        emit_stage_result(result)
        return result.exit_code
    assert out_dir is not None

    exec_failures = check_story_exec_pack(workspace_root=workspace, exec_dir=out_dir, budget=budget)
    if exec_failures:
        result = check_stage_result(
            workspace_root=workspace,
            stage_id="story-pack",
            command=f"uv run --project .codex/skills/textum/scripts textum story pack --workspace {workspace.as_posix()} --n {args.n}",
            failures=exec_failures,
            warnings=[],
            next_on_pass="Story Exec",
            fallback_on_fail="Split Generate",
        )
        emit_stage_result(result)
        return result.exit_code

    rel_dir = out_dir.relative_to(workspace).as_posix()
    result = check_stage_result(
        workspace_root=workspace,
        stage_id="story-pack",
        command=f"uv run --project .codex/skills/textum/scripts textum story pack --workspace {workspace.as_posix()} --n {args.n}",
        failures=[],
        warnings=[],
        entry=f"{rel_dir}/index.json",
        next_on_pass="Story Exec",
        fallback_on_fail="Split Generate",
    )
    emit_stage_result(result)
    return result.exit_code

