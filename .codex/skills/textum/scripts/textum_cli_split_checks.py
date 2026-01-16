from __future__ import annotations

import argparse
from pathlib import Path

from prd_pack import read_prd_pack, workspace_paths
from scaffold_pack import read_scaffold_pack
from split_check_index_pack import build_split_replan_pack, generate_split_check_index_pack
from split_check_refs import validate_split_refs
from split_checkout import write_story_dependency_mermaid
from split_pack_io import read_json_object
from split_plan_pack import read_split_plan_pack
from textum_cli_artifacts import write_check_artifacts
from textum_cli_next import _next_stage_for_failures
from textum_cli_support import _ensure_prd_ready, _ensure_scaffold_ready


def _cmd_split_check1(args: argparse.Namespace) -> int:
    workspace = Path(args.workspace).resolve()
    paths = workspace_paths(workspace)

    split_plan_pack, read_failures = read_split_plan_pack(paths["split_plan_pack"])
    if read_failures:
        next_stage = _next_stage_for_failures(read_failures, fallback="Split Plan")
        _, wrote = write_check_artifacts(
            workspace_root=workspace,
            stage_id="split-check1",
            command=f"uv run --project .codex/skills/textum/scripts textum split check1 --workspace {workspace.as_posix()}",
            next_stage=next_stage,
            failures=read_failures,
        )
        print("FAIL")
        for rel in wrote:
            print(f"wrote: {rel}")
        print(f"next: {next_stage}")
        return 1
    assert split_plan_pack is not None

    index_pack, failures, warnings = generate_split_check_index_pack(
        split_plan_pack_path=paths["split_plan_pack"],
        split_plan_pack=split_plan_pack,
        stories_dir=paths["stories_dir"],
        out_path=paths["split_check_index_pack"],
        max_story_lines=args.max_lines,
        max_story_chars=args.max_chars,
        strict=getattr(args, "strict", False) is True,
    )

    split_replan_written = False
    if isinstance(index_pack, dict):
        replan = build_split_replan_pack(index_pack=index_pack)
        if isinstance(replan.get("oversized_stories"), list) and len(replan["oversized_stories"]) > 0:
            import json

            paths["split_replan_pack"].write_text(
                json.dumps(replan, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
            split_replan_written = True

    if failures:
        next_stage = _next_stage_for_failures(failures, fallback="Split Generate")
        _, wrote = write_check_artifacts(
            workspace_root=workspace,
            stage_id="split-check1",
            command=f"uv run --project .codex/skills/textum/scripts textum split check1 --workspace {workspace.as_posix()}",
            next_stage=next_stage,
            failures=failures,
            warnings=warnings,
            extra={"split_replan_pack": "docs/split-replan-pack.json"} if split_replan_written else None,
        )
        print("FAIL")
        if split_replan_written:
            print(f"wrote: {paths['split_replan_pack'].relative_to(workspace).as_posix()}")
        for rel in wrote:
            print(f"wrote: {rel}")
        print(f"next: {next_stage}")
        return 1

    print("PASS")
    if split_replan_written:
        print(f"wrote: {paths['split_replan_pack'].relative_to(workspace).as_posix()}")
    _, wrote = write_check_artifacts(
        workspace_root=workspace,
        stage_id="split-check1",
        command=f"uv run --project .codex/skills/textum/scripts textum split check1 --workspace {workspace.as_posix()}",
        next_stage="Split Check2",
        failures=[],
        warnings=warnings,
        extra={"split_replan_pack": "docs/split-replan-pack.json"} if split_replan_written else None,
    )
    for rel in wrote:
        print(f"wrote: {rel}")
    print("next: Split Check2")
    return 0


def _cmd_split_check2(args: argparse.Namespace) -> int:
    workspace = Path(args.workspace).resolve()
    paths = workspace_paths(workspace)

    prd_pack, prd_read_failures = read_prd_pack(paths["prd_pack"])
    if prd_read_failures:
        next_stage = _next_stage_for_failures(prd_read_failures, fallback="Split Plan")
        _, wrote = write_check_artifacts(
            workspace_root=workspace,
            stage_id="split-check2",
            command=f"uv run --project .codex/skills/textum/scripts textum split check2 --workspace {workspace.as_posix()}",
            next_stage=next_stage,
            failures=prd_read_failures,
        )
        print("FAIL")
        for rel in wrote:
            print(f"wrote: {rel}")
        print(f"next: {next_stage}")
        return 1
    assert prd_pack is not None

    prd_ready_failures = _ensure_prd_ready(prd_pack, prd_pack_path=paths["prd_pack"])
    if prd_ready_failures:
        next_stage = _next_stage_for_failures(prd_ready_failures, fallback="Split Plan")
        _, wrote = write_check_artifacts(
            workspace_root=workspace,
            stage_id="split-check2",
            command=f"uv run --project .codex/skills/textum/scripts textum split check2 --workspace {workspace.as_posix()}",
            next_stage=next_stage,
            failures=prd_ready_failures,
        )
        print("FAIL")
        for rel in wrote:
            print(f"wrote: {rel}")
        print(f"next: {next_stage}")
        return 1

    scaffold_pack, scaffold_read_failures = read_scaffold_pack(paths["scaffold_pack"])
    if scaffold_read_failures:
        next_stage = _next_stage_for_failures(scaffold_read_failures, fallback="Split Plan")
        _, wrote = write_check_artifacts(
            workspace_root=workspace,
            stage_id="split-check2",
            command=f"uv run --project .codex/skills/textum/scripts textum split check2 --workspace {workspace.as_posix()}",
            next_stage=next_stage,
            failures=scaffold_read_failures,
        )
        print("FAIL")
        for rel in wrote:
            print(f"wrote: {rel}")
        print(f"next: {next_stage}")
        return 1
    assert scaffold_pack is not None

    scaffold_updated, scaffold_ready_failures = _ensure_scaffold_ready(
        scaffold_pack,  # type: ignore[arg-type]
        prd_pack_path=paths["prd_pack"],
        prd_pack=prd_pack,  # type: ignore[arg-type]
        scaffold_pack_path=paths["scaffold_pack"],
        fix=args.fix,
    )
    if scaffold_ready_failures:
        next_stage = _next_stage_for_failures(scaffold_ready_failures, fallback="Split Plan")
        _, wrote = write_check_artifacts(
            workspace_root=workspace,
            stage_id="split-check2",
            command=f"uv run --project .codex/skills/textum/scripts textum split check2 --workspace {workspace.as_posix()}",
            next_stage=next_stage,
            failures=scaffold_ready_failures,
        )
        print("FAIL")
        if scaffold_updated and args.fix:
            print(f"wrote: {paths['scaffold_pack'].relative_to(workspace).as_posix()}")
        for rel in wrote:
            print(f"wrote: {rel}")
        print(f"next: {next_stage}")
        return 1
    index_pack, index_failures = read_json_object(
        paths["split_check_index_pack"],
        missing_fix="regenerate docs/split-check-index-pack.json",
    )
    if index_failures:
        next_stage = _next_stage_for_failures(index_failures, fallback="Split Plan")
        _, wrote = write_check_artifacts(
            workspace_root=workspace,
            stage_id="split-check2",
            command=f"uv run --project .codex/skills/textum/scripts textum split check2 --workspace {workspace.as_posix()}",
            next_stage=next_stage,
            failures=index_failures,
        )
        print("FAIL")
        if scaffold_updated and args.fix:
            print(f"wrote: {paths['scaffold_pack'].relative_to(workspace).as_posix()}")
        for rel in wrote:
            print(f"wrote: {rel}")
        print(f"next: {next_stage}")
        return 1
    assert index_pack is not None

    failures = validate_split_refs(index_pack=index_pack, prd_pack=prd_pack, scaffold_pack=scaffold_pack)
    if failures:
        next_stage = _next_stage_for_failures(failures, fallback="Split Plan")
        _, wrote = write_check_artifacts(
            workspace_root=workspace,
            stage_id="split-check2",
            command=f"uv run --project .codex/skills/textum/scripts textum split check2 --workspace {workspace.as_posix()}",
            next_stage=next_stage,
            failures=failures,
        )
        print("FAIL")
        if scaffold_updated and args.fix:
            print(f"wrote: {paths['scaffold_pack'].relative_to(workspace).as_posix()}")
        for rel in wrote:
            print(f"wrote: {rel}")
        print(f"next: {next_stage}")
        return 1
    print("PASS")
    if scaffold_updated and args.fix:
        print(f"wrote: {paths['scaffold_pack'].relative_to(workspace).as_posix()}")
    _, wrote = write_check_artifacts(
        workspace_root=workspace,
        stage_id="split-check2",
        command=f"uv run --project .codex/skills/textum/scripts textum split check2 --workspace {workspace.as_posix()}",
        next_stage="Split Checkout",
        failures=[],
    )
    for rel in wrote:
        print(f"wrote: {rel}")
    print("next: Split Checkout")
    return 0


def _cmd_split_checkout(args: argparse.Namespace) -> int:
    workspace = Path(args.workspace).resolve()
    paths = workspace_paths(workspace)
    failures = write_story_dependency_mermaid(stories_dir=paths["stories_dir"], out_path=paths["story_mermaid"])
    if failures:
        next_stage = _next_stage_for_failures(failures, fallback="Split Generate")
        _, wrote = write_check_artifacts(
            workspace_root=workspace,
            stage_id="split-checkout",
            command=f"uv run --project .codex/skills/textum/scripts textum split checkout --workspace {workspace.as_posix()}",
            next_stage=next_stage,
            failures=failures,
        )
        print("FAIL")
        for rel in wrote:
            print(f"wrote: {rel}")
        print(f"next: {next_stage}")
        return 1
    print("PASS")
    print(f"wrote: {paths['story_mermaid'].relative_to(workspace).as_posix()}")
    _, wrote = write_check_artifacts(
        workspace_root=workspace,
        stage_id="split-checkout",
        command=f"uv run --project .codex/skills/textum/scripts textum split checkout --workspace {workspace.as_posix()}",
        next_stage="Story Check",
        failures=[],
    )
    for rel in wrote:
        print(f"wrote: {rel}")
    print("next: Story Check")
    return 0
