from __future__ import annotations

from typing import Any

from .prd_render_sections_10 import render_section_10
from .prd_render_sections_8 import render_section_8
from .prd_render_sections_9 import render_section_9


def render_sections_8_10(ctx: dict[str, Any], labels: dict[str, Any]) -> list[str]:
    lines: list[str] = []
    lines.extend(render_section_8(ctx, labels))
    lines.extend(render_section_9(ctx, labels))
    lines.extend(render_section_10(ctx, labels))
    return lines

