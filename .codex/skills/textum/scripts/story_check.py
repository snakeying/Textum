from __future__ import annotations

from typing import Any

from prd_pack_types import Failure
from story_check_utils import scan_story_placeholders, scan_story_text
from story_check_validate_external import validate_story_against_prd, validate_story_against_scaffold
from story_check_validate_internal import validate_story_internal


def check_story_source(
    *,
    story_path: str,
    story_text: str,
    story: dict[str, Any],
    n: int,
    max_lines: int,
    max_chars: int,
    prd_pack: dict[str, Any] | None,
    scaffold_pack: dict[str, Any] | None,
) -> list[Failure]:
    failures: list[Failure] = []

    failures += scan_story_text(story_text, path=story_path)
    failures += scan_story_placeholders(story, path=story_path)

    lines = story_text.count("\n")
    chars = len(story_text)
    if lines > max_lines or chars > max_chars:
        failures.append(
            Failure(
                loc=story_path,
                problem=f"story file exceeds budget: {lines} lines, {chars} chars",
                expected=f"<= {max_lines} lines and <= {max_chars} chars",
                impact="would pollute model attention/context",
                fix=f"split Story {n} into smaller stories in docs/split-plan-pack.json",
            )
        )

    ctx, internal_failures = validate_story_internal(story=story, n=n)
    failures += internal_failures

    if prd_pack is not None:
        failures += validate_story_against_prd(
            story_n=n,
            fp_ids=ctx.get("fp_ids", []),
            prd_api=ctx.get("prd_api", []),
            prd_tbl=ctx.get("prd_tbl", []),
            prd_br=ctx.get("prd_br", []),
            api_endpoints=ctx.get("api_endpoints", []),
            tbl_name_by_id=ctx.get("tbl_name_by_id", {}),
            prd_pack=prd_pack,
        )

    if scaffold_pack is not None:
        failures += validate_story_against_scaffold(
            story_n=n, modules=ctx.get("modules", []), scaffold_pack=scaffold_pack
        )

    return failures
