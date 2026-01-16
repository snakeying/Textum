from __future__ import annotations

from .prd_pack import Failure

from .textum_cli_support import _print_failures


def _next_stage_for_failures(failures: list[Failure], *, fallback: str) -> str:
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

    if any_has("prd-slices") or fix_has("generate docs/prd-slices"):
        return "PRD Slice"

    if loc_has("scaffold-pack.json") or fix_has("docs/scaffold-pack.json") or fix_has("create docs/scaffold-pack.json"):
        if any_has("$.extracted") or any_has("modules_index"):
            return "Scaffold Check"
        return "Scaffold Plan"

    if loc_has("split-plan-pack.json") or fix_has("docs/split-plan-pack.json") or fix_has("create docs/split-plan-pack.json"):
        return "Split Plan"

    if loc_has("split-check-index-pack.json") or fix_has("split-check-index-pack.json"):
        return "Split Check1"

    if any_has("docs/stories/") or any_has("docs\\stories") or any_has("docs/stories/story-") or fix_has("regenerate docs/stories") or fix_has("generate docs/stories") or fix_has("create docs/stories"):
        return "Split Generate"

    if any_has("story-exec") or fix_has("exec pack"):
        return "Story Pack"

    return fallback


def _print_failures_with_next(failures: list[Failure], *, fallback: str) -> None:
    _print_failures(failures)
    print(f"next: {_next_stage_for_failures(failures, fallback=fallback)}")


