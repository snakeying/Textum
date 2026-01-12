from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from prd_pack import (
    Failure,
    check_prd_pack,
    init_prd_pack,
    normalize_prd_pack,
    read_prd_pack,
    skill_asset_paths,
    workspace_paths,
    write_prd_pack,
)
from prd_render import render_prd_markdown
from prd_slices import SliceBudget, generate_prd_slices
from scaffold_pack import (
    check_scaffold_pack,
    init_scaffold_pack,
    normalize_scaffold_pack,
    read_scaffold_pack,
    write_scaffold_pack,
)
from scaffold_render import render_global_context_markdown
from split_check_index_pack import build_split_replan_pack, generate_split_check_index_pack
from split_check_refs import validate_split_refs
from split_checkout import write_story_dependency_mermaid
from split_plan_pack import (
    check_split_plan_pack,
    init_split_plan_pack,
    normalize_split_plan_pack,
    read_split_plan_pack,
    write_split_plan_pack,
)
from split_story_generate import generate_story_files
from story_check import check_story_source
from story_exec_pack import write_story_exec_pack
from story_exec_pack_validate import check_story_exec_pack
from story_exec_paths import find_story_source, story_exec_dir


def _print_failures(failures: list[Failure]) -> None:
    print("FAIL")
    for failure in failures:
        print(
            "- "
            + "; ".join(
                [
                    f"loc={failure.loc}",
                    f"problem={failure.problem}",
                    f"expected={failure.expected}",
                    f"impact={failure.impact}",
                    f"fix={failure.fix}",
                ]
            )
        )


def _load_prd_pack(paths: dict[str, Path]) -> tuple[dict[str, Any] | None, list[Failure]]:
    prd_pack, read_failures = read_prd_pack(paths["prd_pack"])
    if read_failures:
        return None, read_failures
    assert prd_pack is not None
    return prd_pack, []


def _normalize_prd_pack_in_place(
    prd_pack: dict[str, Any], *, write_back_path: Path | None
) -> tuple[bool, list[Failure]]:
    updated, id_failures = normalize_prd_pack(prd_pack)
    if id_failures:
        return False, id_failures
    if updated and write_back_path is not None:
        write_prd_pack(write_back_path, prd_pack)
    return updated, []


def _load_prd_pack_and_normalize(
    paths: dict[str, Path], *, fix: bool
) -> tuple[dict[str, Any] | None, bool, list[Failure]]:
    prd_pack, read_failures = _load_prd_pack(paths)
    if read_failures:
        return None, False, read_failures
    assert prd_pack is not None

    updated, id_failures = _normalize_prd_pack_in_place(prd_pack, write_back_path=paths["prd_pack"] if fix else None)
    if id_failures:
        return None, updated, id_failures

    return prd_pack, updated, []


def _cmd_prd_init(args: argparse.Namespace) -> int:
    workspace = Path(args.workspace).resolve()
    paths = workspace_paths(workspace)
    skill_paths = skill_asset_paths()
    written, failures = init_prd_pack(skill_paths["prd_template"], paths["prd_pack"], force=args.force)
    if failures:
        _print_failures(failures)
        return 1
    if written:
        print(f"OK: wrote {paths['prd_pack'].as_posix()}")
    else:
        print(f"SKIP: {paths['prd_pack'].as_posix()} already exists (use --force to overwrite)")
    return 0


def _cmd_prd_check(args: argparse.Namespace) -> int:
    workspace = Path(args.workspace).resolve()
    paths = workspace_paths(workspace)
    prd_pack, updated, failures = _load_prd_pack_and_normalize(paths, fix=args.fix)
    if failures:
        _print_failures(failures)
        return 1
    assert prd_pack is not None

    ready, check_failures = check_prd_pack(prd_pack)
    if not ready:
        _print_failures(check_failures)
        return 1

    print("PASS")
    if updated and args.fix:
        print(f"UPDATED: {paths['prd_pack'].as_posix()}")
    return 0


def _cmd_prd_render(args: argparse.Namespace) -> int:
    workspace = Path(args.workspace).resolve()
    paths = workspace_paths(workspace)
    prd_pack, _, failures = _load_prd_pack_and_normalize(paths, fix=args.fix)
    if failures:
        _print_failures(failures)
        return 1
    assert prd_pack is not None

    markdown = render_prd_markdown(prd_pack, lang=args.lang)
    paths["docs_dir"].mkdir(parents=True, exist_ok=True)
    paths["prd_render"].write_text(markdown, encoding="utf-8")
    print(f"OK: wrote {paths['prd_render'].as_posix()}")
    return 0


def _cmd_prd_slice(args: argparse.Namespace) -> int:
    workspace = Path(args.workspace).resolve()
    paths = workspace_paths(workspace)
    prd_pack, _, failures = _load_prd_pack_and_normalize(paths, fix=args.fix)
    if failures:
        _print_failures(failures)
        return 1
    assert prd_pack is not None

    ready, check_failures = check_prd_pack(prd_pack)
    if not ready:
        _print_failures(check_failures)
        return 1

    budget = SliceBudget(max_lines=args.max_lines, max_chars=args.max_chars)
    written, failures = generate_prd_slices(
        prd_pack_path=paths["prd_pack"],
        prd_pack=prd_pack,
        out_dir=paths["prd_slices_dir"],
        budget=budget,
        clean=args.clean,
    )
    if failures:
        _print_failures(failures)
        return 1

    print("PASS")
    print(f"OK: wrote {paths['prd_slices_index'].as_posix()}")
    print(f"OK: parts={len(written) - 1}")
    return 0


def _ensure_prd_ready(prd_pack: dict[str, Any], *, prd_pack_path: Path) -> list[Failure]:
    _, id_failures = _normalize_prd_pack_in_place(prd_pack, write_back_path=None)
    if id_failures:
        return id_failures
    ready, check_failures = check_prd_pack(prd_pack)
    if not ready:
        return check_failures
    return []


def _load_prd_pack_and_ensure_ready(paths: dict[str, Path]) -> tuple[dict[str, Any] | None, list[Failure]]:
    prd_pack, read_failures = _load_prd_pack(paths)
    if read_failures:
        return None, read_failures
    assert prd_pack is not None

    prd_ready_failures = _ensure_prd_ready(prd_pack, prd_pack_path=paths["prd_pack"])
    if prd_ready_failures:
        return None, prd_ready_failures

    return prd_pack, []


def _load_scaffold_pack_and_ensure_ready(
    paths: dict[str, Path], *, prd_pack: dict[str, Any], fix: bool
) -> tuple[dict[str, Any] | None, bool, list[Failure]]:
    scaffold_pack, read_failures = read_scaffold_pack(paths["scaffold_pack"])
    if read_failures:
        return None, False, read_failures
    assert scaffold_pack is not None

    updated, ready_failures = _ensure_scaffold_ready(
        scaffold_pack,  # type: ignore[arg-type]
        prd_pack_path=paths["prd_pack"],
        prd_pack=prd_pack,  # type: ignore[arg-type]
        scaffold_pack_path=paths["scaffold_pack"],
        fix=fix,
    )
    if ready_failures:
        return None, updated, ready_failures

    return scaffold_pack, updated, []


def _cmd_scaffold_init(args: argparse.Namespace) -> int:
    workspace = Path(args.workspace).resolve()
    paths = workspace_paths(workspace)
    skill_paths = skill_asset_paths()
    written, failures = init_scaffold_pack(skill_paths["scaffold_template"], paths["scaffold_pack"], force=args.force)
    if failures:
        _print_failures(failures)
        return 1
    if written:
        print(f"OK: wrote {paths['scaffold_pack'].as_posix()}")
    else:
        print(f"SKIP: {paths['scaffold_pack'].as_posix()} already exists (use --force to overwrite)")
    return 0


def _cmd_scaffold_check(args: argparse.Namespace) -> int:
    workspace = Path(args.workspace).resolve()
    paths = workspace_paths(workspace)

    prd_pack, prd_failures = _load_prd_pack_and_ensure_ready(paths)
    if prd_failures:
        _print_failures(prd_failures)
        return 1
    assert prd_pack is not None

    scaffold_pack, updated, scaffold_failures = _load_scaffold_pack_and_ensure_ready(
        paths, prd_pack=prd_pack, fix=args.fix
    )
    if scaffold_failures:
        _print_failures(scaffold_failures)
        return 1
    assert scaffold_pack is not None

    print("PASS")
    if updated and args.fix:
        print(f"UPDATED: {paths['scaffold_pack'].as_posix()}")
    return 0


def _cmd_scaffold_render(args: argparse.Namespace) -> int:
    workspace = Path(args.workspace).resolve()
    paths = workspace_paths(workspace)

    prd_pack, prd_failures = _load_prd_pack_and_ensure_ready(paths)
    if prd_failures:
        _print_failures(prd_failures)
        return 1
    assert prd_pack is not None

    scaffold_pack, _, scaffold_failures = _load_scaffold_pack_and_ensure_ready(paths, prd_pack=prd_pack, fix=args.fix)
    if scaffold_failures:
        _print_failures(scaffold_failures)
        return 1
    assert scaffold_pack is not None

    markdown = render_global_context_markdown(scaffold_pack)
    paths["docs_dir"].mkdir(parents=True, exist_ok=True)
    paths["global_context"].write_text(markdown, encoding="utf-8")
    print(f"OK: wrote {paths['global_context'].as_posix()}")
    return 0


def _ensure_scaffold_ready(
    scaffold_pack: dict[str, object],
    *,
    prd_pack_path: Path,
    prd_pack: dict[str, object],
    scaffold_pack_path: Path,
    fix: bool,
) -> tuple[bool, list[Failure]]:
    updated, failures = normalize_scaffold_pack(scaffold_pack, prd_pack_path=prd_pack_path, prd_pack=prd_pack)
    if failures:
        return updated, failures
    if updated and fix:
        write_scaffold_pack(scaffold_pack_path, scaffold_pack)  # type: ignore[arg-type]
    ready, check_failures = check_scaffold_pack(scaffold_pack)  # type: ignore[arg-type]
    if not ready:
        return updated, check_failures
    return updated, []


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
    api_rows = split_plan_pack.get("api_assignments") if isinstance(split_plan_pack.get("api_assignments"), list) else []
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

                print("SPLIT_REPLAN_PACK_JSON:")
                print(json.dumps(replan, ensure_ascii=False, indent=2))
        return 1

    if decisions:
        print("DECISION")
        for i, d in enumerate(decisions, start=1):
            story = d.get("story")
            detail = d.get("decision")
            action = d.get("suggested_action")
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

    import json

    if not paths["split_check_index_pack"].exists():
        _print_failures(
            [
                Failure(
                    loc=paths["split_check_index_pack"].as_posix(),
                    problem="file not found",
                    expected="split-check-index-pack.json exists",
                    impact="cannot validate refs",
                    fix="run: textum split check1",
                )
            ]
        )
        return 1

    try:
        index_pack = json.loads(paths["split_check_index_pack"].read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        _print_failures(
            [
                Failure(
                    loc=paths["split_check_index_pack"].as_posix(),
                    problem=f"invalid JSON: {error.msg} at line {error.lineno} col {error.colno}",
                    expected="valid JSON document",
                    impact="cannot validate refs",
                    fix=f"fix JSON syntax in {paths['split_check_index_pack'].as_posix()}",
                )
            ]
        )
        return 1
    if not isinstance(index_pack, dict):
        _print_failures(
            [
                Failure(
                    loc="$",
                    problem=f"root must be object, got {type(index_pack).__name__}",
                    expected="JSON object at root",
                    impact="cannot validate refs",
                    fix=f"rewrite {paths['split_check_index_pack'].as_posix()} root as an object",
                )
            ]
        )
        return 1

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
    out_dir, written, pack_failures = write_story_exec_pack(
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


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="textum", add_help=True)

    subparsers = parser.add_subparsers(dest="command", required=True)
    prd_parser = subparsers.add_parser("prd", help="PRD pack commands")
    prd_subparsers = prd_parser.add_subparsers(dest="prd_command", required=True)

    prd_init = prd_subparsers.add_parser("init", help="Initialize docs/prd-pack.json from assets template")
    prd_init.add_argument("--workspace", default=".", help="Workspace root that contains ./docs.")
    prd_init.add_argument("--force", action="store_true", help="Overwrite existing docs/prd-pack.json")
    prd_init.set_defaults(func=_cmd_prd_init)

    prd_check = prd_subparsers.add_parser("check", help="Validate docs/prd-pack.json")
    prd_check.add_argument("--workspace", default=".", help="Workspace root that contains ./docs.")
    prd_check.add_argument(
        "--fix",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Auto-fix and write back (default: true).",
    )
    prd_check.set_defaults(func=_cmd_prd_check)

    prd_render = prd_subparsers.add_parser("render", help="Render docs/PRD.md from docs/prd-pack.json")
    prd_render.add_argument("--workspace", default=".", help="Workspace root that contains ./docs.")
    prd_render.add_argument(
        "--fix",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Auto-fix and write back (default: true).",
    )
    prd_render.add_argument(
        "--lang",
        default="auto",
        choices=["auto", "zh", "en"],
        help="PRD.md language: auto/zh/en (default: auto).",
    )
    prd_render.set_defaults(func=_cmd_prd_render)

    prd_slice = prd_subparsers.add_parser("slice", help="Generate low-noise slices under docs/prd-slices/")
    prd_slice.add_argument("--workspace", default=".", help="Workspace root that contains ./docs.")
    prd_slice.add_argument(
        "--fix",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Auto-fix and write back docs/prd-pack.json before slicing (default: true).",
    )
    prd_slice.add_argument(
        "--clean",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Delete docs/prd-slices/ before writing (default: true).",
    )
    prd_slice.add_argument("--max-lines", type=int, default=350, help="Max lines per slice file (default: 350).")
    prd_slice.add_argument("--max-chars", type=int, default=12000, help="Max chars per slice file (default: 12000).")
    prd_slice.set_defaults(func=_cmd_prd_slice)

    scaffold_parser = subparsers.add_parser("scaffold", help="Scaffold/global context commands")
    scaffold_subparsers = scaffold_parser.add_subparsers(dest="scaffold_command", required=True)

    scaffold_init = scaffold_subparsers.add_parser(
        "init", help="Initialize docs/scaffold-pack.json from assets template"
    )
    scaffold_init.add_argument("--workspace", default=".", help="Workspace root that contains ./docs.")
    scaffold_init.add_argument("--force", action="store_true", help="Overwrite existing docs/scaffold-pack.json")
    scaffold_init.set_defaults(func=_cmd_scaffold_init)

    scaffold_check = scaffold_subparsers.add_parser("check", help="Validate docs/scaffold-pack.json")
    scaffold_check.add_argument("--workspace", default=".", help="Workspace root that contains ./docs.")
    scaffold_check.add_argument(
        "--fix",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Auto-fix and write back (default: true).",
    )
    scaffold_check.set_defaults(func=_cmd_scaffold_check)

    scaffold_render = scaffold_subparsers.add_parser(
        "render", help="Render docs/GLOBAL-CONTEXT.md from docs/scaffold-pack.json"
    )
    scaffold_render.add_argument("--workspace", default=".", help="Workspace root that contains ./docs.")
    scaffold_render.add_argument(
        "--fix",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Auto-fix and write back scaffold-pack.json before rendering (default: true).",
    )
    scaffold_render.set_defaults(func=_cmd_scaffold_render)

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

    parsed = parser.parse_args(argv)
    return int(parsed.func(parsed))


if __name__ == "__main__":
    raise SystemExit(main())
