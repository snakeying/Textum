from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SliceBudget:
    max_lines: int
    max_chars: int

