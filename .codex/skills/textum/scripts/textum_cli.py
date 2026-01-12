from __future__ import annotations

import argparse
from pathlib import Path

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
    prd_pack, read_failures = read_prd_pack(paths["prd_pack"])
    if read_failures:
        _print_failures(read_failures)
        return 1
    assert prd_pack is not None

    updated, id_failures = normalize_prd_pack(prd_pack)
    if id_failures:
        _print_failures(id_failures)
        return 1

    if updated and args.fix:
        write_prd_pack(paths["prd_pack"], prd_pack)

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
    prd_pack, read_failures = read_prd_pack(paths["prd_pack"])
    if read_failures:
        _print_failures(read_failures)
        return 1
    assert prd_pack is not None

    updated, id_failures = normalize_prd_pack(prd_pack)
    if id_failures:
        _print_failures(id_failures)
        return 1
    if updated and args.fix:
        write_prd_pack(paths["prd_pack"], prd_pack)

    markdown = render_prd_markdown(prd_pack, lang=args.lang)
    paths["docs_dir"].mkdir(parents=True, exist_ok=True)
    paths["prd_render"].write_text(markdown, encoding="utf-8")
    print(f"OK: wrote {paths['prd_render'].as_posix()}")
    return 0


def _cmd_prd_slice(args: argparse.Namespace) -> int:
    workspace = Path(args.workspace).resolve()
    paths = workspace_paths(workspace)
    prd_pack, read_failures = read_prd_pack(paths["prd_pack"])
    if read_failures:
        _print_failures(read_failures)
        return 1
    assert prd_pack is not None

    updated, id_failures = normalize_prd_pack(prd_pack)
    if id_failures:
        _print_failures(id_failures)
        return 1
    if updated and args.fix:
        write_prd_pack(paths["prd_pack"], prd_pack)

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


def _ensure_prd_ready(prd_pack: dict[str, object], *, prd_pack_path: Path) -> list[Failure]:
    updated, id_failures = normalize_prd_pack(prd_pack)
    if id_failures:
        return id_failures
    ready, check_failures = check_prd_pack(prd_pack)
    if not ready:
        return check_failures
    return []


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

    prd_pack, read_prd_failures = read_prd_pack(paths["prd_pack"])
    if read_prd_failures:
        _print_failures(read_prd_failures)
        return 1
    assert prd_pack is not None

    prd_ready_failures = _ensure_prd_ready(prd_pack, prd_pack_path=paths["prd_pack"])
    if prd_ready_failures:
        _print_failures(prd_ready_failures)
        return 1

    scaffold_pack, read_scaffold_failures = read_scaffold_pack(paths["scaffold_pack"])
    if read_scaffold_failures:
        _print_failures(read_scaffold_failures)
        return 1
    assert scaffold_pack is not None

    updated, norm_failures = normalize_scaffold_pack(
        scaffold_pack,
        prd_pack_path=paths["prd_pack"],
        prd_pack=prd_pack,
    )
    if norm_failures:
        _print_failures(norm_failures)
        return 1
    if updated and args.fix:
        write_scaffold_pack(paths["scaffold_pack"], scaffold_pack)

    ready, check_failures = check_scaffold_pack(scaffold_pack)
    if not ready:
        _print_failures(check_failures)
        return 1

    print("PASS")
    if updated and args.fix:
        print(f"UPDATED: {paths['scaffold_pack'].as_posix()}")
    return 0


def _cmd_scaffold_render(args: argparse.Namespace) -> int:
    workspace = Path(args.workspace).resolve()
    paths = workspace_paths(workspace)

    prd_pack, read_prd_failures = read_prd_pack(paths["prd_pack"])
    if read_prd_failures:
        _print_failures(read_prd_failures)
        return 1
    assert prd_pack is not None

    prd_ready_failures = _ensure_prd_ready(prd_pack, prd_pack_path=paths["prd_pack"])
    if prd_ready_failures:
        _print_failures(prd_ready_failures)
        return 1

    scaffold_pack, read_scaffold_failures = read_scaffold_pack(paths["scaffold_pack"])
    if read_scaffold_failures:
        _print_failures(read_scaffold_failures)
        return 1
    assert scaffold_pack is not None

    updated, norm_failures = normalize_scaffold_pack(
        scaffold_pack,
        prd_pack_path=paths["prd_pack"],
        prd_pack=prd_pack,
    )
    if norm_failures:
        _print_failures(norm_failures)
        return 1
    if updated and args.fix:
        write_scaffold_pack(paths["scaffold_pack"], scaffold_pack)

    ready, check_failures = check_scaffold_pack(scaffold_pack)
    if not ready:
        _print_failures(check_failures)
        return 1

    markdown = render_global_context_markdown(scaffold_pack)
    paths["docs_dir"].mkdir(parents=True, exist_ok=True)
    paths["global_context"].write_text(markdown, encoding="utf-8")
    print(f"OK: wrote {paths['global_context'].as_posix()}")
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

    parsed = parser.parse_args(argv)
    return int(parsed.func(parsed))


if __name__ == "__main__":
    raise SystemExit(main())
