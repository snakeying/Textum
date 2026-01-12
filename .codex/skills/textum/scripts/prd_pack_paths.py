from __future__ import annotations

from pathlib import Path

from prd_pack_types import (
    PRD_PACK_FILENAME,
    PRD_RENDER_FILENAME,
    PRD_SCHEMA_FILENAME,
    PRD_TEMPLATE_FILENAME,
)
from scaffold_pack_types import GLOBAL_CONTEXT_FILENAME, SCAFFOLD_PACK_FILENAME, SCAFFOLD_TEMPLATE_FILENAME


def workspace_paths(workspace: Path) -> dict[str, Path]:
    docs_dir = workspace / "docs"
    prd_slices_dir = docs_dir / "prd-slices"
    return {
        "docs_dir": docs_dir,
        "prd_pack": docs_dir / PRD_PACK_FILENAME,
        "prd_render": docs_dir / PRD_RENDER_FILENAME,
        "prd_slices_dir": prd_slices_dir,
        "prd_slices_index": prd_slices_dir / "index.json",
        "scaffold_pack": docs_dir / SCAFFOLD_PACK_FILENAME,
        "global_context": docs_dir / GLOBAL_CONTEXT_FILENAME,
    }


def _find_skill_root() -> Path:
    module_path = Path(__file__).resolve()
    for parent in module_path.parents:
        if (parent / "SKILL.md").exists():
            return parent
    return module_path.parents[2]


def skill_asset_paths() -> dict[str, Path]:
    skill_root = _find_skill_root()
    assets_dir = skill_root / "assets"
    return {
        "skill_root": skill_root,
        "assets_dir": assets_dir,
        "prd_template": assets_dir / PRD_TEMPLATE_FILENAME,
        "prd_schema": assets_dir / PRD_SCHEMA_FILENAME,
        "scaffold_template": assets_dir / SCAFFOLD_TEMPLATE_FILENAME,
    }
