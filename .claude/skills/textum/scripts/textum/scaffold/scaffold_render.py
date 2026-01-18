from __future__ import annotations

from typing import Any

from .scaffold_render_emit import render_global_context_markdown_from_parts
from .scaffold_render_extract import extract_global_context_parts


def render_global_context_markdown(scaffold_pack: dict[str, Any]) -> str:
    parts = extract_global_context_parts(scaffold_pack)
    return render_global_context_markdown_from_parts(parts)

