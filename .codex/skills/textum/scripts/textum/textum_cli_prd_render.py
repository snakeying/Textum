from __future__ import annotations

import argparse
from pathlib import Path

from .prd_pack import workspace_paths
from .prd_render import render_prd_markdown
from .textum_cli_emit import emit_stage_result
from .textum_cli_runner import simple_stage_result
from .textum_cli_support import _load_prd_pack_and_normalize


def _cmd_prd_render(args: argparse.Namespace) -> int:
    workspace = Path(args.workspace).resolve()
    paths = workspace_paths(workspace)

    prd_pack, _, failures = _load_prd_pack_and_normalize(paths, fix=args.fix)
    if failures:
        result = simple_stage_result(
            failures=failures,
            warnings=[],
            wrote=[],
            entry=None,
            next_on_pass="PRD Slice",
            fallback_on_fail="PRD Plan",
        )
        emit_stage_result(result)
        return result.exit_code
    assert prd_pack is not None

    markdown = render_prd_markdown(prd_pack, lang=args.lang)
    paths["docs_dir"].mkdir(parents=True, exist_ok=True)
    paths["prd_render"].write_text(markdown, encoding="utf-8")
    result = simple_stage_result(
        failures=[],
        warnings=[],
        wrote=[paths["prd_render"].relative_to(workspace).as_posix()],
        entry=None,
        next_on_pass="PRD Slice",
        fallback_on_fail="PRD Plan",
    )
    emit_stage_result(result)
    return result.exit_code

