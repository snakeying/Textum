from __future__ import annotations

from .textum_cli_result import StageResult
from .textum_cli_support import _print_check_items


def emit_stage_result(result: StageResult) -> None:
    print(result.status)
    if result.status == "FAIL":
        _print_check_items(result.failures, label="FAIL")
    else:
        if result.warnings:
            _print_check_items(result.warnings, label="WARN")

    if result.entry:
        print(f"entry: {result.entry}")
    for rel in result.wrote:
        print(f"wrote: {rel}")
    print(f"next: {result.next_stage}")

