from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

from .prd_pack import Failure

StageStatus = Literal["PASS", "FAIL"]


@dataclass(frozen=True)
class StageResult:
    status: StageStatus
    next_stage: str
    exit_code: int
    failures: list[Failure] = field(default_factory=list)
    warnings: list[Failure] = field(default_factory=list)
    wrote: list[str] = field(default_factory=list)
    entry: str | None = None

