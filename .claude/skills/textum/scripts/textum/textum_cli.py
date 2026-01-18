from __future__ import annotations

import argparse

from .textum_cli_prd import register_prd_commands
from .textum_cli_scaffold import register_scaffold_commands
from .textum_cli_split import register_split_commands
from .textum_cli_story import register_story_commands


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="textum", add_help=True)
    subparsers = parser.add_subparsers(dest="command", required=True)

    register_prd_commands(subparsers)
    register_scaffold_commands(subparsers)
    register_split_commands(subparsers)
    register_story_commands(subparsers)

    parsed = parser.parse_args(argv)
    return int(parsed.func(parsed))


if __name__ == "__main__":
    raise SystemExit(main())


