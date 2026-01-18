from __future__ import annotations

import re
from dataclasses import dataclass


PRD_PACK_FILENAME = "prd-pack.json"
PRD_RENDER_FILENAME = "PRD.md"
PRD_TEMPLATE_FILENAME = "prd-pack.template.json"
PRD_SCHEMA_FILENAME = "prd-pack.schema.json"

PLACEHOLDER_SENTINEL = "<<FILL>>"

MODULE_ID_RE = re.compile(r"^M-(\d{2})$")
FP_ID_RE = re.compile(r"^FP-(\d{3})$")
BR_ID_RE = re.compile(r"^BR-(\d{3})$")
SC_ID_RE = re.compile(r"^SC-(\d{2})$")
TBL_ID_RE = re.compile(r"^TBL-(\d{3})$")
API_ID_RE = re.compile(r"^API-(\d{3})$")

LANDING_PREFIXES = ("DB:", "FILE:", "CFG:", "EXT:")


@dataclass(frozen=True)
class Failure:
    loc: str
    problem: str
    expected: str
    impact: str
    fix: str
