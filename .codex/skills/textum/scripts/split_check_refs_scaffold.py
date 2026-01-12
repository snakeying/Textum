from __future__ import annotations

from typing import Any

from prd_pack_types import BR_ID_RE


def extract_gc_br_ids(scaffold_pack: dict[str, Any]) -> set[str]:
    extracted = scaffold_pack.get("extracted") if isinstance(scaffold_pack.get("extracted"), dict) else {}
    gc_rules = extracted.get("business_rules") if isinstance(extracted.get("business_rules"), list) else []
    gc_br: set[str] = set()
    for rule in gc_rules:
        if not isinstance(rule, dict):
            continue
        rid = rule.get("id")
        if isinstance(rid, str) and BR_ID_RE.match(rid):
            gc_br.add(rid)
    return gc_br

