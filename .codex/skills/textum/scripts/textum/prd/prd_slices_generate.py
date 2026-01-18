from __future__ import annotations

import hashlib
import shutil
from pathlib import Path
from typing import Any

from .prd_pack_types import Failure
from .prd_slices_types import SliceBudget
from .prd_slices_utils import json_text, rel_posix, sha256_file
from .prd_slices_writer import SliceWriter
from .prd_slices_generate_write_a import write_prd_slices_part_a
from .prd_slices_generate_write_b import write_prd_slices_part_b


def generate_prd_slices(
    *,
    prd_pack_path: Path,
    prd_pack: dict[str, Any],
    out_dir: Path,
    budget: SliceBudget,
    clean: bool,
) -> tuple[list[Path], list[Failure]]:
    if clean and out_dir.exists():
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    workspace_root = prd_pack_path.parent.parent

    if prd_pack_path.exists():
        prd_pack_sha256 = sha256_file(prd_pack_path)
    else:
        prd_pack_sha256 = hashlib.sha256(json_text(prd_pack).encode("utf-8")).hexdigest()

    source = {
        "prd_pack_path": rel_posix(prd_pack_path, workspace_root),
        "prd_pack_schema_version": prd_pack.get("schema_version"),
        "prd_pack_sha256": prd_pack_sha256,
    }

    writer = SliceWriter(out_dir=out_dir, budget=budget, workspace_root=workspace_root)

    overview = {
        "schema_version": "prd-slice-overview@v1",
        "source": source,
        "project": prd_pack.get("project"),
        "goals": prd_pack.get("goals"),
        "non_goals": prd_pack.get("non_goals"),
        "scope": prd_pack.get("scope"),
    }
    writer.write_part("overview", "overview.json", overview)
    write_prd_slices_part_a(writer=writer, source=source, prd_pack=prd_pack)
    write_prd_slices_part_b(writer=writer, source=source, prd_pack=prd_pack)

    writer.write_index(source=source)

    return writer.written, writer.failures

