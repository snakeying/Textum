from __future__ import annotations

from typing import Any

def scaffold_module_rows(scaffold_pack: dict[str, Any], *, module_ids: list[str]) -> list[dict[str, Any]]:
    extracted = scaffold_pack.get("extracted")
    if not isinstance(extracted, dict):
        return []
    modules = extracted.get("modules_index")
    if not isinstance(modules, list):
        return []

    wanted = set(module_ids)
    rows: list[dict[str, Any]] = []
    for item in modules:
        if not isinstance(item, dict):
            continue
        item_id = item.get("id")
        if not isinstance(item_id, str) or item_id not in wanted:
            continue
        rows.append(item)
    return rows
