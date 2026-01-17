from __future__ import annotations

from typing import Any

from .prd_pack_types import Failure, TBL_ID_RE


def parse_landing_tokens(
    landing: list[Any],
    *,
    table_name_to_id: dict[str, str],
    failures: list[Failure],
    loc_prefix: str,
) -> tuple[set[str], set[str], set[str], set[str]]:
    tbl_ids: set[str] = set()
    art_file: set[str] = set()
    art_cfg: set[str] = set()
    art_ext: set[str] = set()

    for index, token in enumerate(landing):
        loc = f"{loc_prefix}[{index}]"
        if not isinstance(token, str):
            failures.append(
                Failure(
                    loc=loc,
                    problem=f"landing token must be string, got {type(token).__name__}",
                    expected="string token",
                    impact="cannot derive story refs",
                    fix=f"rewrite {loc} as a string",
                )
            )
            continue
        stripped = token.strip()
        if stripped == "" or stripped.upper() == "N/A":
            continue

        if stripped.startswith("DB:"):
            ref = stripped.removeprefix("DB:").strip()
            if ref == "":
                failures.append(
                    Failure(
                        loc=loc,
                        problem="DB: token missing table reference",
                        expected="DB:<table_name> or DB:TBL-###",
                        impact="cannot derive table refs",
                        fix=f"set {loc} to DB:<table_name> or DB:TBL-###",
                    )
                )
                continue
            if TBL_ID_RE.match(ref):
                tbl_ids.add(ref)
                continue
            if ref not in table_name_to_id:
                failures.append(
                    Failure(
                        loc=loc,
                        problem=f"DB table name not found: {ref}",
                        expected="DB:<table_name> must exist in data_model.tables[].name",
                        impact="cannot derive table refs",
                        fix=f"add data_model.tables[] entry with name={ref}",
                    )
                )
                continue
            tbl_ids.add(table_name_to_id[ref])
            continue

        if stripped.startswith("FILE:"):
            value = stripped.removeprefix("FILE:").strip()
            if value == "":
                failures.append(
                    Failure(
                        loc=loc,
                        problem="FILE: token missing path",
                        expected="FILE:<path>",
                        impact="cannot derive artifacts",
                        fix=f"set {loc} to FILE:<path>",
                    )
                )
                continue
            art_file.add(f"ART:FILE:{value}")
            continue

        if stripped.startswith("CFG:"):
            value = stripped.removeprefix("CFG:").strip()
            if value == "":
                failures.append(
                    Failure(
                        loc=loc,
                        problem="CFG: token missing key",
                        expected="CFG:<key>",
                        impact="cannot derive artifacts",
                        fix=f"set {loc} to CFG:<key>",
                    )
                )
                continue
            art_cfg.add(f"ART:CFG:{value}")
            continue

        if stripped.startswith("EXT:"):
            value = stripped.removeprefix("EXT:").strip()
            if value == "":
                failures.append(
                    Failure(
                        loc=loc,
                        problem="EXT: token missing system",
                        expected="EXT:<system>",
                        impact="cannot derive artifacts",
                        fix=f"set {loc} to EXT:<system>",
                    )
                )
                continue
            art_ext.add(f"ART:EXT:{value}")
            continue

    return tbl_ids, art_file, art_cfg, art_ext

