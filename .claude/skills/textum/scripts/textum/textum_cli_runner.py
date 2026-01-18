from __future__ import annotations

from pathlib import Path
from typing import Any

from textum.prd.prd_pack_types import Failure
from .textum_cli_artifacts import write_check_artifacts
from .textum_cli_next import _next_stage_for_failures
from .textum_cli_result import StageResult


def check_stage_result(
    *,
    workspace_root: Path,
    stage_id: str,
    command: str,
    failures: list[Failure],
    next_on_pass: str,
    fallback_on_fail: str,
    warnings: list[Failure] | None = None,
    wrote: list[str] | None = None,
    entry: str | None = None,
    extra: dict[str, Any] | None = None,
) -> StageResult:
    warnings = warnings or []
    wrote = wrote or []

    if failures:
        next_stage = _next_stage_for_failures(failures, fallback=fallback_on_fail)
        _, artifact_wrote = write_check_artifacts(
            workspace_root=workspace_root,
            stage_id=stage_id,
            command=command,
            next_stage=next_stage,
            failures=failures,
            warnings=warnings,
            extra=extra,
        )
        return StageResult(
            status="FAIL",
            failures=failures,
            warnings=warnings,
            wrote=[*wrote, *artifact_wrote],
            entry=entry,
            next_stage=next_stage,
            exit_code=1,
        )

    _, artifact_wrote = write_check_artifacts(
        workspace_root=workspace_root,
        stage_id=stage_id,
        command=command,
        next_stage=next_on_pass,
        failures=[],
        warnings=warnings,
        extra=extra,
    )
    return StageResult(
        status="PASS",
        failures=[],
        warnings=warnings,
        wrote=[*wrote, *artifact_wrote],
        entry=entry,
        next_stage=next_on_pass,
        exit_code=0,
    )


def simple_stage_result(
    *,
    failures: list[Failure],
    next_on_pass: str,
    fallback_on_fail: str,
    warnings: list[Failure] | None = None,
    wrote: list[str] | None = None,
    entry: str | None = None,
) -> StageResult:
    warnings = warnings or []
    wrote = wrote or []

    if failures:
        next_stage = _next_stage_for_failures(failures, fallback=fallback_on_fail)
        return StageResult(
            status="FAIL",
            failures=failures,
            warnings=warnings,
            wrote=wrote,
            entry=entry,
            next_stage=next_stage,
            exit_code=1,
        )

    return StageResult(
        status="PASS",
        failures=[],
        warnings=warnings,
        wrote=wrote,
        entry=entry,
        next_stage=next_on_pass,
        exit_code=0,
    )
