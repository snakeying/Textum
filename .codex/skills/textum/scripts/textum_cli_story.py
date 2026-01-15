from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from prd_pack import Failure, read_prd_pack, workspace_paths
from prd_slices_types import SliceBudget
from scaffold_pack import check_scaffold_pack, read_scaffold_pack
from story_check import check_story_source
from story_exec_pack import write_story_exec_pack
from story_exec_pack_validate import check_story_exec_pack
from story_exec_paths import find_story_source, story_exec_dir
from textum_cli_support import _print_failures, _require_scaffold_extracted_modules_index
from textum_cli_support import _ensure_prd_ready


def _next_for_failures(failures: list[Failure]) -> str:
    def loc_has(substr: str) -> bool:
        s = substr.lower()
        return any(s in failure.loc.lower() for failure in failures)

    def fix_has(substr: str) -> bool:
        s = substr.lower()
        return any(s in failure.fix.lower() for failure in failures)

    def any_has(substr: str) -> bool:
        return loc_has(substr) or fix_has(substr)

    # Most-upstream first (fail-fast).
    if loc_has("prd-pack.json") or fix_has("docs/prd-pack.json") or fix_has("create docs/prd-pack.json"):
        return "PRD Plan"

    if loc_has("scaffold-pack.json") or fix_has("docs/scaffold-pack.json") or fix_has("create docs/scaffold-pack.json"):
        if any_has("$.extracted") or any_has("modules_index"):
            return "Scaffold Check"
        return "Scaffold Plan"

    if fix_has("split-plan-pack.json"):
        return "Split Plan"

    if any_has("docs/stories/") or any_has("docs\\stories") or fix_has("regenerate docs/stories") or fix_has("create docs/stories"):
        return "Split Generate"

    if any_has("story-exec") or fix_has("exec pack"):
        return "Story Pack"

    return "Split Generate"


def _print_failures_with_next(failures: list[Failure]) -> None:
    _print_failures(failures)
    print(f"next: {_next_for_failures(failures)}")


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
                    fix=f"regenerate {story_path.as_posix()}",
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
                    fix=f"regenerate {story_path.as_posix()}",
                )
            ],
        )

    return story_path, story_text, story, []


def _cmd_story_check(args: argparse.Namespace) -> int:
    workspace = Path(args.workspace).resolve()
    paths = workspace_paths(workspace)

    story_path, story_text, story, failures = _load_story_source(stories_dir=paths["stories_dir"], n=args.n)
    if failures:
        _print_failures_with_next(failures)
        return 1
    assert story_path is not None
    assert story_text is not None
    assert story is not None

    prd_pack, prd_failures = read_prd_pack(paths["prd_pack"])
    if prd_failures:
        _print_failures_with_next(prd_failures)
        return 1
    assert prd_pack is not None
    prd_ready_failures = _ensure_prd_ready(prd_pack, prd_pack_path=paths["prd_pack"])
    if prd_ready_failures:
        _print_failures_with_next(prd_ready_failures)
        return 1

    scaffold_pack, scaffold_failures = read_scaffold_pack(paths["scaffold_pack"])
    if scaffold_failures:
        _print_failures_with_next(scaffold_failures)
        return 1
    assert scaffold_pack is not None
    scaffold_ready_failures = _require_scaffold_extracted_modules_index(scaffold_pack=scaffold_pack, prd_pack=prd_pack)
    if scaffold_ready_failures:
        _print_failures_with_next(scaffold_ready_failures)
        return 1
    scaffold_ready, scaffold_check_failures = check_scaffold_pack(scaffold_pack)
    if not scaffold_ready:
        _print_failures_with_next(scaffold_check_failures)
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
        _print_failures_with_next(failures)
        return 1
    print("PASS")
    print("next: Story Pack")
    return 0


def _cmd_story_pack(args: argparse.Namespace) -> int:
    workspace = Path(args.workspace).resolve()
    paths = workspace_paths(workspace)

    story_path, story_text, story, failures = _load_story_source(stories_dir=paths["stories_dir"], n=args.n)
    if failures:
        _print_failures_with_next(failures)
        return 1
    assert story_path is not None
    assert story_text is not None
    assert story is not None

    prd_pack, prd_failures = read_prd_pack(paths["prd_pack"])
    if prd_failures:
        _print_failures_with_next(prd_failures)
        return 1
    assert prd_pack is not None
    prd_ready_failures = _ensure_prd_ready(prd_pack, prd_pack_path=paths["prd_pack"])
    if prd_ready_failures:
        _print_failures_with_next(prd_ready_failures)
        return 1

    scaffold_pack, scaffold_failures = read_scaffold_pack(paths["scaffold_pack"])
    if scaffold_failures:
        _print_failures_with_next(scaffold_failures)
        return 1
    assert scaffold_pack is not None
    scaffold_ready_failures = _require_scaffold_extracted_modules_index(scaffold_pack=scaffold_pack, prd_pack=prd_pack)
    if scaffold_ready_failures:
        _print_failures_with_next(scaffold_ready_failures)
        return 1
    scaffold_ready, scaffold_check_failures = check_scaffold_pack(scaffold_pack)
    if not scaffold_ready:
        _print_failures_with_next(scaffold_check_failures)
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
        _print_failures_with_next(failures)
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
        _print_failures_with_next(pack_failures)
        return 1
    assert out_dir is not None

    exec_failures = check_story_exec_pack(workspace_root=workspace, exec_dir=out_dir, budget=budget)
    if exec_failures:
        _print_failures_with_next(exec_failures)
        return 1

    rel_dir = out_dir.relative_to(workspace).as_posix()
    print("PASS")
    print(f"entry: {rel_dir}/index.json")
    print("next: Story Exec")
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
