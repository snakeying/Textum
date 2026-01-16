from __future__ import annotations

import argparse
import json
from pathlib import Path

from .prd_pack import Failure, normalize_prd_pack, read_prd_pack, workspace_paths, write_prd_pack
from .textum_cli_support import _print_failures
from .textum_json_path import append_value, delete_value, set_value


def _parse_patch_value(args: argparse.Namespace) -> tuple[object | None, list[Failure]]:
    sources = [
        args.value is not None,
        args.value_json is not None,
        args.value_file is not None,
    ]
    if sum(1 for value in sources if value) != 1:
        return None, [
            Failure(
                loc="textum prd patch",
                problem="value must be provided via exactly one of: --value, --value-json, --value-file",
                expected="one value source",
                impact="patch not applied",
                fix="rerun with exactly one value source",
            )
        ]

    if args.value is not None:
        return args.value, []

    if args.value_json is not None:
        try:
            return json.loads(args.value_json), []
        except json.JSONDecodeError as error:
            loc_hint = f"line {error.lineno} col {error.colno}"
            return None, [
                Failure(
                    loc="--value-json",
                    problem=f"invalid JSON: {error.msg} at line {error.lineno} col {error.colno}",
                    expected="a valid JSON literal (string/number/object/array/null/true/false)",
                    impact="patch not applied",
                    fix=f"fix JSON syntax at {loc_hint} and rerun",
                )
            ]

    assert args.value_file is not None
    value_path = Path(args.value_file).expanduser()
    if not value_path.exists():
        return None, [
            Failure(
                loc="--value-file",
                problem=f"file not found: {value_path.as_posix()}",
                expected="existing JSON file",
                impact="patch not applied",
                fix="provide a valid --value-file path and rerun",
            )
        ]
    try:
        return json.loads(value_path.read_text(encoding="utf-8")), []
    except json.JSONDecodeError as error:
        loc_hint = f"line {error.lineno} col {error.colno}"
        return None, [
            Failure(
                loc=value_path.as_posix(),
                problem=f"invalid JSON: {error.msg} at line {error.lineno} col {error.colno}",
                expected="a valid JSON document",
                impact="patch not applied",
                fix=f"fix JSON syntax at {loc_hint} and rerun",
            )
        ]


def _cmd_prd_patch(args: argparse.Namespace) -> int:
    workspace = Path(args.workspace).resolve()
    paths = workspace_paths(workspace)

    prd_pack, read_failures = read_prd_pack(paths["prd_pack"])
    if read_failures:
        _print_failures(read_failures)
        print("next: PRD Plan")
        return 1
    assert prd_pack is not None

    op = args.op
    if op in ("set", "append"):
        value, value_failures = _parse_patch_value(args)
        if value_failures:
            _print_failures(value_failures)
            print("next: PRD Plan")
            return 1
    else:
        if args.value is not None or args.value_json is not None or args.value_file is not None:
            _print_failures(
                [
                    Failure(
                        loc="textum prd patch",
                        problem="unexpected value for delete op",
                        expected="no --value/--value-json/--value-file for delete",
                        impact="patch not applied",
                        fix="remove value flags and rerun",
                    )
                ]
            )
            print("next: PRD Plan")
            return 1
        value = None

    try:
        if op == "set":
            changed = set_value(prd_pack, args.path, value, create=args.create)  # type: ignore[arg-type]
        elif op == "append":
            changed = append_value(prd_pack, args.path, value, create=args.create)  # type: ignore[arg-type]
        elif op == "delete":
            changed = delete_value(prd_pack, args.path, missing_ok=args.missing_ok)
        else:
            _print_failures(
                [
                    Failure(
                        loc="textum prd patch",
                        problem=f"unknown op: {op}",
                        expected="set|append|delete",
                        impact="patch not applied",
                        fix="choose a valid op and rerun",
                    )
                ]
            )
            print("next: PRD Plan")
            return 1
    except ValueError as error:
        _print_failures(
            [
                Failure(
                    loc=f"docs/prd-pack.json:{args.path}",
                    problem=str(error),
                    expected="a valid JSON path into docs/prd-pack.json",
                    impact="patch not applied",
                    fix="fix --path / op arguments and rerun",
                )
            ]
        )
        print("next: PRD Plan")
        return 1

    normalized = False
    if args.normalize:
        normalized, normalize_failures = normalize_prd_pack(prd_pack)
        if normalize_failures:
            _print_failures(normalize_failures)
            print("next: PRD Plan")
            return 1

    should_write = bool(changed or normalized)
    if should_write:
        write_prd_pack(paths["prd_pack"], prd_pack)

    print("PASS")
    if should_write:
        print(f"wrote: {paths['prd_pack'].relative_to(workspace).as_posix()}")
    print("next: PRD Check")
    return 0


def register_prd_patch_command(prd_subparsers: argparse._SubParsersAction) -> None:
    prd_patch = prd_subparsers.add_parser("patch", help="Apply a small patch to docs/prd-pack.json")
    prd_patch.add_argument("op", choices=["set", "append", "delete"], help="Patch operation")
    prd_patch.add_argument("--workspace", default=".", help="Workspace root that contains ./docs.")
    prd_patch.add_argument("--path", required=True, help="JSON path like $.project.name or $.modules[0].name")
    prd_patch.add_argument("--value", default=None, help="Value as plain string (stored as JSON string).")
    prd_patch.add_argument("--value-json", default=None, help="Value as JSON literal (object/array/string/null/etc).")
    prd_patch.add_argument("--value-file", default=None, help="Read JSON value from a file path.")
    prd_patch.add_argument(
        "--create",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Create missing containers (default: true).",
    )
    prd_patch.add_argument(
        "--missing-ok",
        action=argparse.BooleanOptionalAction,
        default=False,
        help="Delete: missing path is OK (default: false).",
    )
    prd_patch.add_argument(
        "--normalize",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Normalize IDs after patch (default: true).",
    )
    prd_patch.set_defaults(func=_cmd_prd_patch)


