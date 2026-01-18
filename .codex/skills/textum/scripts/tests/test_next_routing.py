from __future__ import annotations

import unittest

from textum.prd_pack import Failure
from textum.textum_cli_next import _next_stage_for_failures


def _f(*, loc: str, fix: str) -> Failure:
    return Failure(
        loc=loc,
        problem="x",
        expected="x",
        impact="x",
        fix=fix,
    )


class TestNextStageRouting(unittest.TestCase):
    def test_routes_prd_pack_failures_to_prd_plan(self) -> None:
        failures = [_f(loc="docs/prd-pack.json:$", fix="create docs/prd-pack.json")]
        self.assertEqual(_next_stage_for_failures(failures, fallback="Story Check"), "PRD Plan")

    def test_routes_scaffold_extracted_failures_to_scaffold_check(self) -> None:
        failures = [_f(loc="docs/scaffold-pack.json:$.extracted.modules_index", fix="populate docs/scaffold-pack.json:$.extracted")]
        self.assertEqual(_next_stage_for_failures(failures, fallback="Split Plan"), "Scaffold Check")

    def test_routes_story_file_failures_to_split_generate(self) -> None:
        failures = [_f(loc="docs/stories/story-001-core-flow.json", fix="regenerate docs/stories")]
        self.assertEqual(_next_stage_for_failures(failures, fallback="Split Plan"), "Split Generate")

    def test_routes_story_exec_failures_to_story_pack(self) -> None:
        failures = [_f(loc="docs/story-exec/story-001-*/index.json", fix="rebuild exec pack")]
        self.assertEqual(_next_stage_for_failures(failures, fallback="Split Generate"), "Story Pack")

