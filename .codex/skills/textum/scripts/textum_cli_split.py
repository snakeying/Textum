from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from prd_pack import read_prd_pack, skill_asset_paths, workspace_paths
from scaffold_pack import read_scaffold_pack
from split_check_index_pack import build_split_replan_pack, generate_split_check_index_pack
from split_check_refs import validate_split_refs
from split_checkout import write_story_dependency_mermaid
from split_pack_io import read_json_object
from split_plan_pack import (
    check_split_plan_pack,
    init_split_plan_pack,
    normalize_split_plan_pack,
    read_split_plan_pack,
    write_split_plan_pack,
)
from split_story_generate import generate_story_files
from textum_cli_support import _ensure_prd_ready, _ensure_scaffold_ready, _print_failures


def _cmd_split_plan_init(args: argparse.Namespace) -> int:
    workspace = Path(args.workspace).resolve()
    paths = workspace_paths(workspace)
    skill_paths = skill_asset_paths()
    written, failures = init_split_plan_pack(
        skill_paths["split_plan_template"], paths["split_plan_pack"], force=args.force
    )
    if failures:
        _print_failures(failures)
        return 1
    if written:
        print(f"OK: wrote {paths['split_plan_pack'].as_posix()}")
    else:
        print(f"SKIP: {paths['split_plan_pack'].as_posix()} already exists (use --force to overwrite)")
    return 0


def _cmd_split_plan_check(args: argparse.Namespace) -> int:
    workspace = Path(args.workspace).resolve()
    paths = workspace_paths(workspace)

    prd_pack, prd_read_failures = read_prd_pack(paths["prd_pack"])
    if prd_read_failures:
        _print_failures(prd_read_failures)
        return 1
    assert prd_pack is not None

    prd_ready_failures = _ensure_prd_ready(prd_pack, prd_pack_path=paths["prd_pack"])
    if prd_ready_failures:
        _print_failures(prd_ready_failures)
        return 1

    scaffold_pack, scaffold_read_failures = read_scaffold_pack(paths["scaffold_pack"])
    if scaffold_read_failures:
        _print_failures(scaffold_read_failures)
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
        return 1

    split_plan_pack, read_failures = read_split_plan_pack(paths["split_plan_pack"])
    if read_failures:
        _print_failures(read_failures)
        return 1
    assert split_plan_pack is not None

    updated, norm_failures = normalize_split_plan_pack(
        split_plan_pack,
        workspace_root=workspace,
        prd_pack_path=paths["prd_pack"],
        scaffold_pack_path=paths["scaffold_pack"],
    )
    if norm_failures:
        _print_failures(norm_failures)
        return 1
    if updated and args.fix:
        write_split_plan_pack(paths["split_plan_pack"], split_plan_pack)

    ready, check_failures = check_split_plan_pack(split_plan_pack, prd_pack=prd_pack)
    if not ready:
        _print_failures(check_failures)
        return 1

    api_counts: dict[str, int] = {}
    api_rows = (
        split_plan_pack.get("api_assignments") if isinstance(split_plan_pack.get("api_assignments"), list) else []
    )
    for row in api_rows:
        if not isinstance(row, dict):
            continue
        story = row.get("story")
        if isinstance(story, str) and story.strip():
            api_counts[story] = api_counts.get(story, 0) + 1
    decisions = [(s, c) for s, c in sorted(api_counts.items(), key=lambda x: x[0]) if c in (4, 5)]

    if decisions:
        print("DECISION")
        for i, (story, count) in enumerate(decisions, start=1):
            print(f"- D-{i:03d}; story={story}; api_assigned={count}; action=consider splitting/redistributing")
        print(f"OK: wrote {paths['split_plan_pack'].as_posix()}")
        return 0

    print("PASS")
    if updated and args.fix:
        print(f"UPDATED: {paths['split_plan_pack'].as_posix()}")
    return 0


def _cmd_split_generate(args: argparse.Namespace) -> int:
    workspace = Path(args.workspace).resolve()
    paths = workspace_paths(workspace)

    prd_pack, prd_read_failures = read_prd_pack(paths["prd_pack"])
    if prd_read_failures:
        _print_failures(prd_read_failures)
        return 1
    assert prd_pack is not None

    prd_ready_failures = _ensure_prd_ready(prd_pack, prd_pack_path=paths["prd_pack"])
    if prd_ready_failures:
        _print_failures(prd_ready_failures)
        return 1

    scaffold_pack, scaffold_read_failures = read_scaffold_pack(paths["scaffold_pack"])
    if scaffold_read_failures:
        _print_failures(scaffold_read_failures)
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
        return 1

    split_plan_pack, read_failures = read_split_plan_pack(paths["split_plan_pack"])
    if read_failures:
        _print_failures(read_failures)
        return 1
    assert split_plan_pack is not None

    updated, norm_failures = normalize_split_plan_pack(
        split_plan_pack,
        workspace_root=workspace,
        prd_pack_path=paths["prd_pack"],
        scaffold_pack_path=paths["scaffold_pack"],
    )
    if norm_failures:
        _print_failures(norm_failures)
        return 1
    if updated and args.fix:
        write_split_plan_pack(paths["split_plan_pack"], split_plan_pack)

    ready, check_failures = check_split_plan_pack(split_plan_pack, prd_pack=prd_pack)
    if not ready:
        _print_failures(check_failures)
        return 1

    written, gen_failures = generate_story_files(
        split_plan_pack=split_plan_pack,
        prd_pack=prd_pack,
        out_dir=paths["stories_dir"],
        clean=args.clean,
    )
    if gen_failures:
        _print_failures(gen_failures)
        return 1

    print("PASS")
    print(f"OK: wrote {len(written)} story files under {paths['stories_dir'].as_posix()}")
    return 0


def _cmd_split_check1(args: argparse.Namespace) -> int:
    workspace = Path(args.workspace).resolve()
    paths = workspace_paths(workspace)

    split_plan_pack, read_failures = read_split_plan_pack(paths["split_plan_pack"])
    if read_failures:
        _print_failures(read_failures)
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
                print(f"REPLAN: wrote {paths['split_replan_pack'].as_posix()}")
                print("REPLAN_SUMMARY:")
                for story in replan["oversized_stories"]:
                    if not isinstance(story, dict):
                        continue
                    metrics = story.get("metrics") if isinstance(story.get("metrics"), dict) else {}
                    fp = metrics.get("feature_points")
                    api = metrics.get("api_refs")
                    tbl = metrics.get("tbl_refs")
                    print(f"- {story.get('story')}: fp={fp}; api={api}; tbl={tbl}")
        return 1

    if decisions:
        print("DECISION")
        for i, decision in enumerate(decisions, start=1):
            story = decision.get("story")
            detail = decision.get("decision")
            action = decision.get("suggested_action")
            print(f"- D-{i:03d}; story={story}; issue={detail}; action={action}")
        print(f"OK: wrote {paths['split_check_index_pack'].as_posix()}")
        return 0

    print("PASS")
    print(f"OK: wrote {paths['split_check_index_pack'].as_posix()}")
    return 0


def _cmd_split_check2(args: argparse.Namespace) -> int:
    workspace = Path(args.workspace).resolve()
    paths = workspace_paths(workspace)

    prd_pack, prd_read_failures = read_prd_pack(paths["prd_pack"])
    if prd_read_failures:
        _print_failures(prd_read_failures)
        return 1
    assert prd_pack is not None

    prd_ready_failures = _ensure_prd_ready(prd_pack, prd_pack_path=paths["prd_pack"])
    if prd_ready_failures:
        _print_failures(prd_ready_failures)
        return 1

    scaffold_pack, scaffold_read_failures = read_scaffold_pack(paths["scaffold_pack"])
    if scaffold_read_failures:
        _print_failures(scaffold_read_failures)
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
        return 1
    index_pack, index_failures = read_json_object(
        paths["split_check_index_pack"], missing_fix="run: textum split check1"
    )
    if index_failures:
        _print_failures(index_failures)
        return 1
    assert index_pack is not None

    failures = validate_split_refs(index_pack=index_pack, prd_pack=prd_pack, scaffold_pack=scaffold_pack)
    if failures:
        _print_failures(failures)
        return 1
    print("PASS")
    return 0


def _cmd_split_checkout(args: argparse.Namespace) -> int:
    workspace = Path(args.workspace).resolve()
    paths = workspace_paths(workspace)
    failures = write_story_dependency_mermaid(stories_dir=paths["stories_dir"], out_path=paths["story_mermaid"])
    if failures:
        _print_failures(failures)
        return 1
    rel = paths["story_mermaid"].relative_to(workspace).as_posix()
    print("PASS")
    print(f"OK: wrote {rel}")
    return 0


def register_split_commands(subparsers: Any) -> None:
    split_parser = subparsers.add_parser("split", help="Split plan/story generation commands")
    split_subparsers = split_parser.add_subparsers(dest="split_command", required=True)

    split_plan_parser = split_subparsers.add_parser("plan", help="Split planning pack commands")
    split_plan_sub = split_plan_parser.add_subparsers(dest="split_plan_command", required=True)

    split_plan_init = split_plan_sub.add_parser("init", help="Initialize docs/split-plan-pack.json from assets template")
    split_plan_init.add_argument("--workspace", default=".", help="Workspace root that contains ./docs.")
    split_plan_init.add_argument("--force", action="store_true", help="Overwrite existing docs/split-plan-pack.json")
    split_plan_init.set_defaults(func=_cmd_split_plan_init)

    split_plan_check = split_plan_sub.add_parser("check", help="Validate docs/split-plan-pack.json")
    split_plan_check.add_argument("--workspace", default=".", help="Workspace root that contains ./docs.")
    split_plan_check.add_argument(
        "--fix",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Auto-fix and write back (default: true).",
    )
    split_plan_check.set_defaults(func=_cmd_split_plan_check)

    split_generate = split_subparsers.add_parser("generate", help="Generate per-story JSON files under docs/stories/")
    split_generate.add_argument("--workspace", default=".", help="Workspace root that contains ./docs.")
    split_generate.add_argument(
        "--fix",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Auto-fix and write back split-plan-pack.json before generating (default: true).",
    )
    split_generate.add_argument(
        "--clean",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Delete docs/stories/story-*.json before writing (default: true).",
    )
    split_generate.set_defaults(func=_cmd_split_generate)

    split_check1 = split_subparsers.add_parser("check1", help="Core split check and index pack generation")
    split_check1.add_argument("--workspace", default=".", help="Workspace root that contains ./docs.")
    split_check1.add_argument("--max-lines", type=int, default=350, help="Max lines per story file (default: 350).")
    split_check1.add_argument("--max-chars", type=int, default=12000, help="Max chars per story file (default: 12000).")
    split_check1.set_defaults(func=_cmd_split_check1)

    split_check2 = split_subparsers.add_parser("check2", help="Ref consistency checks (PRD/Scaffold)")
    split_check2.add_argument("--workspace", default=".", help="Workspace root that contains ./docs.")
    split_check2.add_argument(
        "--fix",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Auto-fix PRD/Scaffold packs before checking (default: true).",
    )
    split_check2.set_defaults(func=_cmd_split_check2)

    split_checkout = split_subparsers.add_parser(
        "checkout", help="Export story dependency graph (docs/story-mermaid.md)"
    )
    split_checkout.add_argument("--workspace", default=".", help="Workspace root that contains ./docs.")
    split_checkout.set_defaults(func=_cmd_split_checkout)

