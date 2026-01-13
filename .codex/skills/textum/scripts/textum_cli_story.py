from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from prd_pack import Failure, read_prd_pack, workspace_paths
from prd_slices_types import SliceBudget
from scaffold_pack import read_scaffold_pack
from story_check import check_story_source
from story_exec_pack import write_story_exec_pack
from story_exec_pack_validate import check_story_exec_pack
from story_exec_paths import find_story_source, story_exec_dir
from textum_cli_support import _print_failures, _require_scaffold_extracted_modules_index


def _load_story_source(*, stories_dir: Path, n: int) -> tuple[Path | None, str | None, dict | None, list[Failure]]:
    story_path, failures = find_story_source(stories_dir, n=n)
    if failures:
        return None, None, None, failures

    story_text = story_path.read_text(encoding="utf-8")
    import json

    try:
        story = json.loads(story_text)
    except json.JSONDecodeError as error:
        return (
            None,
            None,
            None,
            [
                Failure(
                    loc=story_path.as_posix(),
                    problem=f"invalid JSON: {error.msg} at line {error.lineno} col {error.colno}",
                    expected="valid JSON document",
                    impact="cannot proceed",
                    fix=f"fix JSON syntax in {story_path.as_posix()}",
                )
            ],
        )
    if not isinstance(story, dict):
        return (
            None,
            None,
            None,
            [
                Failure(
                    loc="$",
                    problem=f"root must be object, got {type(story).__name__}",
                    expected="JSON object at root",
                    impact="cannot proceed",
                    fix=f"rewrite {story_path.as_posix()} root as an object",
                )
            ],
        )

    return story_path, story_text, story, []


def _cmd_story_check(args: argparse.Namespace) -> int:
    workspace = Path(args.workspace).resolve()
    paths = workspace_paths(workspace)

    story_path, story_text, story, failures = _load_story_source(stories_dir=paths["stories_dir"], n=args.n)
    if failures:
        _print_failures(failures)
        return 1
    assert story_path is not None
    assert story_text is not None
    assert story is not None

    prd_pack, prd_failures = read_prd_pack(paths["prd_pack"])
    if prd_failures:
        _print_failures(prd_failures)
        return 1
    assert prd_pack is not None

    scaffold_pack, scaffold_failures = read_scaffold_pack(paths["scaffold_pack"])
    if scaffold_failures:
        _print_failures(scaffold_failures)
        return 1
    assert scaffold_pack is not None
    scaffold_ready_failures = _require_scaffold_extracted_modules_index(scaffold_pack=scaffold_pack, prd_pack=prd_pack)
    if scaffold_ready_failures:
        _print_failures(scaffold_ready_failures)
        return 1

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
        _print_failures(failures)
        return 1
    print("PASS")
    return 0


def _cmd_story_pack(args: argparse.Namespace) -> int:
    workspace = Path(args.workspace).resolve()
    paths = workspace_paths(workspace)

    story_path, story_text, story, failures = _load_story_source(stories_dir=paths["stories_dir"], n=args.n)
    if failures:
        _print_failures(failures)
        return 1
    assert story_path is not None
    assert story_text is not None
    assert story is not None

    prd_pack, prd_failures = read_prd_pack(paths["prd_pack"])
    if prd_failures:
        _print_failures(prd_failures)
        return 1
    assert prd_pack is not None

    scaffold_pack, scaffold_failures = read_scaffold_pack(paths["scaffold_pack"])
    if scaffold_failures:
        _print_failures(scaffold_failures)
        return 1
    assert scaffold_pack is not None
    scaffold_ready_failures = _require_scaffold_extracted_modules_index(scaffold_pack=scaffold_pack, prd_pack=prd_pack)
    if scaffold_ready_failures:
        _print_failures(scaffold_ready_failures)
        return 1

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
        _print_failures(failures)
        return 1

    exec_dir = story_exec_dir(paths["docs_dir"], story_source=story_path)
    budget = SliceBudget(max_lines=args.max_lines, max_chars=args.max_chars)
    out_dir, written_files, pack_failures = write_story_exec_pack(
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
        _print_failures(pack_failures)
        return 1
    assert out_dir is not None

    exec_failures = check_story_exec_pack(workspace_root=workspace, exec_dir=out_dir, budget=budget)
    if exec_failures:
        _print_failures(exec_failures)
        return 1

    rel_dir = out_dir.relative_to(workspace).as_posix()
    print("PASS")
    print(f"ENTRY: {rel_dir}/index.json")
    return 0


def register_story_commands(subparsers: Any) -> None:
    story_parser = subparsers.add_parser("story", help="Story execution pack commands")
    story_subparsers = story_parser.add_subparsers(dest="story_command", required=True)

    story_check = story_subparsers.add_parser("check", help="Validate a single docs/stories/story-###-*.json")
    story_check.add_argument("--workspace", default=".", help="Workspace root that contains ./docs.")
    story_check.add_argument("--n", type=int, required=True, help="Story number (e.g. 1).")
    story_check.add_argument("--max-lines", type=int, default=350, help="Max lines per story file (default: 350).")
    story_check.add_argument("--max-chars", type=int, default=12000, help="Max chars per story file (default: 12000).")
    story_check.set_defaults(func=_cmd_story_check)

    story_pack = story_subparsers.add_parser(
        "pack", help="Generate low-noise story exec pack under docs/story-exec/"
    )
    story_pack.add_argument("--workspace", default=".", help="Workspace root that contains ./docs.")
    story_pack.add_argument("--n", type=int, required=True, help="Story number (e.g. 1).")
    story_pack.add_argument(
        "--clean",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Delete existing docs/story-exec/story-###-*/ before writing (default: true).",
    )
    story_pack.add_argument("--max-lines", type=int, default=350, help="Max lines per file (default: 350).")
    story_pack.add_argument("--max-chars", type=int, default=12000, help="Max chars per file (default: 12000).")
    story_pack.set_defaults(func=_cmd_story_pack)
