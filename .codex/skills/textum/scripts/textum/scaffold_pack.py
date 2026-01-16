from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

from .prd_pack_types import Failure
from .scaffold_pack_extract import extract_from_prd_pack
from .scaffold_pack_io import init_scaffold_pack, read_scaffold_pack, write_scaffold_pack
from .scaffold_pack_types import SCAFFOLD_PACK_FILENAME
from .scaffold_pack_validate import check_scaffold_pack, validate_scaffold_pack

__all__ = [
    "SCAFFOLD_PACK_FILENAME",
    "Failure",
    "check_scaffold_pack",
    "extract_from_prd_pack",
    "init_scaffold_pack",
    "normalize_scaffold_pack",
    "read_scaffold_pack",
    "validate_scaffold_pack",
    "write_scaffold_pack",
]


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def normalize_scaffold_pack(
    scaffold_pack: dict[str, Any],
    *,
    prd_pack_path: Path,
    prd_pack: dict[str, Any],
) -> tuple[bool, list[Failure]]:
    updated = False
    failures: list[Failure] = []

    if scaffold_pack.get("schema_version") != "scaffold-pack@v1":
        scaffold_pack["schema_version"] = "scaffold-pack@v1"
        updated = True

    workspace_root = prd_pack_path.parent.parent
    try:
        prd_rel = prd_pack_path.relative_to(workspace_root).as_posix()
    except ValueError:
        prd_rel = prd_pack_path.as_posix()
    source = {
        "prd_pack_path": prd_rel,
        "prd_pack_schema_version": prd_pack.get("schema_version"),
        "prd_pack_sha256": _sha256_file(prd_pack_path) if prd_pack_path.exists() else None,
    }
    if scaffold_pack.get("source") != source:
        scaffold_pack["source"] = source
        updated = True

    extracted = extract_from_prd_pack(prd_pack)
    if scaffold_pack.get("extracted") != extracted:
        scaffold_pack["extracted"] = extracted
        updated = True

    decisions = scaffold_pack.get("decisions")
    if not isinstance(decisions, dict):
        decisions = {}
        scaffold_pack["decisions"] = decisions
        updated = True

    if "tech_stack" not in decisions or not isinstance(decisions.get("tech_stack"), dict):
        decisions["tech_stack"] = {"backend": None, "frontend": None, "database": None, "other": []}
        updated = True
    if "repo_structure" not in decisions or not isinstance(decisions.get("repo_structure"), list):
        decisions["repo_structure"] = []
        updated = True
    if "validation_commands" not in decisions or not isinstance(decisions.get("validation_commands"), list):
        decisions["validation_commands"] = []
        updated = True
    if "coding_conventions" not in decisions:
        decisions["coding_conventions"] = None
        updated = True

    return updated, failures

