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
from textum_cli_support import _ensure_prd_ready, _ensure_scaffold_ready, _print_failures


def _cmd_split_check1(args: argparse.Namespace) -> int:
    workspace = Path(args.workspace).resolve()
    paths = workspace_paths(workspace)

    split_plan_pack, read_failures = read_split_plan_pack(paths["split_plan_pack"])
    if read_failures:
        _print_failures(read_failures)
        print("next: Split Plan")
        return 1
    assert split_plan_pack is not None

    index_pack, failures, decisions = generate_split_check_index_pack(
        split_plan_pack_path=paths["split_plan_pack"],
        split_plan_pack=split_plan_pack,
        stories_dir=paths["stories_dir"],
        out_path=paths["split_check_index_pack"],
        max_story_lines=args.max_lines,
        max_story_chars=args.max_chars,
    )

    if failures:
        _print_failures(failures)
        if isinstance(index_pack, dict):
            replan = build_split_replan_pack(index_pack=index_pack)
            if isinstance(replan.get("oversized_stories"), list) and len(replan["oversized_stories"]) > 0:
                import json

                paths["split_replan_pack"].write_text(
                    json.dumps(replan, ensure_ascii=False, indent=2) + "\n",
                    encoding="utf-8",
                )
                rel = paths["split_replan_pack"].relative_to(workspace).as_posix()
                print(f"wrote: {rel}")
        print("next: Split Plan")
        return 1

    if decisions:
        print("DECISION")
        for i, decision in enumerate(decisions, start=1):
            story = decision.get("story")
            detail = decision.get("decision")
            action = decision.get("suggested_action")
            print(f"- D-{i:03d}; story={story}; issue={detail}; action={action}")
        print("next: Split Check2")
        return 0

    print("PASS")
    print("next: Split Check2")
    return 0


def _cmd_split_check2(args: argparse.Namespace) -> int:
    workspace = Path(args.workspace).resolve()
    paths = workspace_paths(workspace)

    prd_pack, prd_read_failures = read_prd_pack(paths["prd_pack"])
    if prd_read_failures:
        _print_failures(prd_read_failures)
        print("next: Split Plan")
        return 1
    assert prd_pack is not None

    prd_ready_failures = _ensure_prd_ready(prd_pack, prd_pack_path=paths["prd_pack"])
    if prd_ready_failures:
        _print_failures(prd_ready_failures)
        print("next: Split Plan")
        return 1

    scaffold_pack, scaffold_read_failures = read_scaffold_pack(paths["scaffold_pack"])
    if scaffold_read_failures:
        _print_failures(scaffold_read_failures)
        print("next: Split Plan")
        return 1
    assert scaffold_pack is not None

    _, scaffold_ready_failures = _ensure_scaffold_ready(
        scaffold_pack,  # type: ignore[arg-type]
        prd_pack_path=paths["prd_pack"],
        prd_pack=prd_pack,  # type: ignore[arg-type]
        scaffold_pack_path=paths["scaffold_pack"],
        fix=args.fix,
    )
    if scaffold_ready_failures:
        _print_failures(scaffold_ready_failures)
        print("next: Split Plan")
        return 1
    index_pack, index_failures = read_json_object(
        paths["split_check_index_pack"],
        missing_fix="regenerate docs/split-check-index-pack.json",
    )
    if index_failures:
        _print_failures(index_failures)
        print("next: Split Plan")
        return 1
    assert index_pack is not None

    failures = validate_split_refs(index_pack=index_pack, prd_pack=prd_pack, scaffold_pack=scaffold_pack)
    if failures:
        _print_failures(failures)
        print("next: Split Plan")
        return 1
    print("PASS")
    print("next: Split Checkout")
    return 0


def _cmd_split_checkout(args: argparse.Namespace) -> int:
    workspace = Path(args.workspace).resolve()
    paths = workspace_paths(workspace)
    failures = write_story_dependency_mermaid(stories_dir=paths["stories_dir"], out_path=paths["story_mermaid"])
    if failures:
        _print_failures(failures)
        print("next: Split Generate")
        return 1
    print("PASS")
    print("next: Story Check")
    return 0
