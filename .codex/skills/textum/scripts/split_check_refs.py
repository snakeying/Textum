from __future__ import annotations

from typing import Any

from prd_pack_types import API_ID_RE, BR_ID_RE, Failure, FP_ID_RE, MODULE_ID_RE, TBL_ID_RE
from split_check_refs_prd import extract_prd_ref_sets
from split_check_refs_scaffold import extract_gc_br_ids


def validate_split_refs(
    *,
    index_pack: dict[str, Any],
    prd_pack: dict[str, Any],
    scaffold_pack: dict[str, Any],
) -> list[Failure]:
    failures: list[Failure] = []

    if index_pack.get("schema_version") != "split-check-index-pack@v1":
        failures.append(
            Failure(
                loc="$.schema_version",
                problem=f"unexpected schema_version: {index_pack.get('schema_version')!r}",
                expected="'split-check-index-pack@v1'",
                impact="cannot validate split refs",
                fix="rerun: textum split check1",
            )
        )
        return failures

    summary = index_pack.get("summary")
    if not isinstance(summary, dict):
        failures.append(
            Failure(
                loc="$.summary",
                problem=f"expected object, got {type(summary).__name__}",
                expected="object",
                impact="cannot validate split refs",
                fix="rerun: textum split check1",
            )
        )
        return failures

    refs = summary.get("refs")
    if not isinstance(refs, dict):
        failures.append(
            Failure(
                loc="$.summary.refs",
                problem=f"expected object, got {type(refs).__name__}",
                expected="object",
                impact="cannot validate split refs",
                fix="rerun: textum split check1",
            )
        )
        return failures

    prd_sets = extract_prd_ref_sets(prd_pack)
    gc_br = extract_gc_br_ids(scaffold_pack)

    s_fp = {x for x in (refs.get("fp_ids") or []) if isinstance(x, str) and FP_ID_RE.match(x)}
    s_tbl = {x for x in (refs.get("prd_tbl_ids") or []) if isinstance(x, str) and TBL_ID_RE.match(x)}
    s_api = {x for x in (refs.get("prd_api_ids") or []) if isinstance(x, str) and API_ID_RE.match(x)}
    s_prd_br = {x for x in (refs.get("prd_br_ids") or []) if isinstance(x, str) and BR_ID_RE.match(x)}
    s_gc_br = {x for x in (refs.get("gc_br_ids") or []) if isinstance(x, str) and BR_ID_RE.match(x)}

    missing_fp = sorted(prd_sets.fp_ids - s_fp)
    if missing_fp:
        failures.append(
            Failure(
                loc="docs/prd-pack.json",
                problem=f"some PRD feature points are not covered by stories: {', '.join(missing_fp)}",
                expected="every PRD FP-### covered by at least one story",
                impact="requirements are missing in execution plan",
                fix="revise split plan boundaries and rerun split generate + check1",
            )
        )

    unknown_fp = sorted(s_fp - prd_sets.fp_ids)
    if unknown_fp:
        failures.append(
            Failure(
                loc="docs/split-check-index-pack.json",
                problem=f"unknown fp ids referenced: {', '.join(unknown_fp)}",
                expected="fp ids exist in PRD modules[].feature_points[].id",
                impact="index pack is inconsistent",
                fix="rerun: textum split generate then textum split check1",
            )
        )

    for tid in sorted(s_tbl - prd_sets.tbl_ids):
        failures.append(
            Failure(
                loc="docs/split-check-index-pack.json",
                problem=f"unknown table id referenced: {tid}",
                expected="TBL-### exists in PRD data_model.tables[].id",
                impact="execution plan references unknown storage",
                fix="fix PRD tables or landing tokens, then rerun split generate + check1",
            )
        )

    for rid in sorted(s_prd_br - prd_sets.br_ids):
        failures.append(
            Failure(
                loc="docs/split-check-index-pack.json",
                problem=f"unknown PRD business rule id referenced: {rid}",
                expected="BR-### exists in PRD business_rules[].id",
                impact="execution plan references unknown rule",
                fix="fix PRD business_rules or story refs, then rerun split generate + check1",
            )
        )

    for rid in sorted(s_gc_br - gc_br):
        failures.append(
            Failure(
                loc="docs/scaffold-pack.json",
                problem=f"unknown GC business rule id referenced: {rid}",
                expected="BR-### exists in scaffold-pack extracted.business_rules",
                impact="execution plan references unknown rule",
                fix="run: textum scaffold check, then rerun split generate + check1",
            )
        )

    modules_covered = {m for m in (summary.get("modules") or []) if isinstance(m, str) and MODULE_ID_RE.match(m)}
    missing_p0 = sorted(prd_sets.p0_modules - modules_covered)
    if missing_p0:
        failures.append(
            Failure(
                loc="docs/split-check-index-pack.json",
                problem=f"P0 modules not covered: {', '.join(missing_p0)}",
                expected="every P0 module appears in at least 1 story",
                impact="critical scope is uncovered",
                fix="revise split plan modules mapping and rerun split generate + check1",
            )
        )

    if prd_sets.has_api is False:
        if len(prd_sets.api_ids) != 0:
            failures.append(
                Failure(
                    loc="docs/prd-pack.json",
                    problem="PRD has_api=false but endpoints are present",
                    expected="endpoints empty when has_api=false",
                    impact="PRD is contradictory",
                    fix="run: textum prd check and fix api.has_api/endpoints",
                )
            )
        if len(s_api) != 0:
            failures.append(
                Failure(
                    loc="docs/split-check-index-pack.json",
                    problem="PRD has_api=false but stories reference APIs",
                    expected="no API refs when PRD has_api=false",
                    impact="execution plan is contradictory",
                    fix="remove API assignments from split plan and regenerate stories",
                )
            )
    else:
        missing_api = sorted(prd_sets.api_ids - s_api)
        extra_api = sorted(s_api - prd_sets.api_ids)
        if missing_api:
            failures.append(
                Failure(
                    loc="docs/split-check-index-pack.json",
                    problem=f"some PRD APIs are not covered by stories: {', '.join(missing_api)}",
                    expected="every PRD API-### assigned to exactly 1 story",
                    impact="API work has no owning story",
                    fix="revise split plan API assignments and regenerate stories + index pack",
                )
            )
        if extra_api:
            failures.append(
                Failure(
                    loc="docs/split-check-index-pack.json",
                    problem=f"unknown API ids referenced: {', '.join(extra_api)}",
                    expected="API ids exist in PRD api.endpoints[].id",
                    impact="execution plan references unknown endpoints",
                    fix="rerun: textum split generate then textum split check1",
                )
            )

    return failures

