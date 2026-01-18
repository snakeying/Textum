from __future__ import annotations

from typing import Any

from .prd_pack_types import API_ID_RE, BR_ID_RE, Failure, FP_ID_RE, MODULE_ID_RE, TBL_ID_RE
from .split_check_refs_prd import extract_prd_ref_sets
from .split_check_refs_scaffold import extract_gc_br_ids


def _examples_summary(examples: list[str], *, limit: int = 8) -> str:
    if len(examples) <= limit:
        return ", ".join(examples)
    shown = examples[:limit]
    remaining = len(examples) - limit
    return ", ".join(shown) + f", ... (+{remaining} more)"


def validate_refs_against_packs(
    *,
    refs: dict[str, Any],
    summary: dict[str, Any],
    prd_pack: dict[str, Any],
    scaffold_pack: dict[str, Any],
) -> list[Failure]:
    failures: list[Failure] = []

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
                problem=f"some PRD feature points are not covered by stories ({len(missing_fp)}): {_examples_summary(missing_fp)}",
                expected="every PRD FP-### covered by at least one story",
                impact="requirements are missing in execution plan",
                fix="revise docs/split-plan-pack.json boundaries to cover missing FP-###",
            )
        )

    unknown_fp = sorted(s_fp - prd_sets.fp_ids)
    if unknown_fp:
        failures.append(
            Failure(
                loc="docs/split-check-index-pack.json",
                problem=f"unknown fp ids referenced ({len(unknown_fp)}): {_examples_summary(unknown_fp)}",
                expected="fp ids exist in PRD modules[].feature_points[].id",
                impact="index pack is inconsistent",
                fix="regenerate docs/stories/",
            )
        )

    unknown_tbl = sorted(s_tbl - prd_sets.tbl_ids)
    if unknown_tbl:
        failures.append(
            Failure(
                loc="docs/split-check-index-pack.json",
                problem=f"unknown table ids referenced ({len(unknown_tbl)}): {_examples_summary(unknown_tbl)}",
                expected="TBL-### exists in PRD data_model.tables[].id",
                impact="execution plan references unknown storage",
                fix="add missing tables to docs/prd-pack.json data_model.tables[]",
            )
        )

    unknown_prd_br = sorted(s_prd_br - prd_sets.br_ids)
    if unknown_prd_br:
        failures.append(
            Failure(
                loc="docs/split-check-index-pack.json",
                problem=f"unknown PRD business rule ids referenced ({len(unknown_prd_br)}): {_examples_summary(unknown_prd_br)}",
                expected="BR-### exists in PRD business_rules[].id",
                impact="execution plan references unknown rule",
                fix="add missing rules to docs/prd-pack.json business_rules[]",
            )
        )

    unknown_gc_br = sorted(s_gc_br - gc_br)
    if unknown_gc_br:
        failures.append(
            Failure(
                loc="docs/prd-pack.json",
                problem=f"unknown GC business rule ids referenced ({len(unknown_gc_br)}): {_examples_summary(unknown_gc_br)}",
                expected="BR-### exists in PRD business_rules[]",
                impact="execution plan references unknown rule",
                fix="add missing rules to docs/prd-pack.json business_rules[]",
            )
        )

    modules_covered = {m for m in (summary.get("modules") or []) if isinstance(m, str) and MODULE_ID_RE.match(m)}
    missing_p0 = sorted(prd_sets.p0_modules - modules_covered)
    if missing_p0:
        failures.append(
            Failure(
                loc="docs/split-check-index-pack.json",
                problem=f"P0 modules not covered ({len(missing_p0)}): {_examples_summary(missing_p0)}",
                expected="every P0 module appears in at least 1 story",
                impact="critical scope is uncovered",
                fix="fix docs/split-plan-pack.json stories[].modules to cover all P0 modules",
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
                    fix="fix docs/prd-pack.json api.has_api/endpoints consistency",
                )
            )
        if len(s_api) != 0:
            failures.append(
                Failure(
                    loc="docs/split-check-index-pack.json",
                    problem="PRD has_api=false but stories reference APIs",
                    expected="no API refs when PRD has_api=false",
                    impact="execution plan is contradictory",
                    fix="set docs/split-plan-pack.json api_assignments to []",
                )
            )
    else:
        missing_api = sorted(prd_sets.api_ids - s_api)
        extra_api = sorted(s_api - prd_sets.api_ids)
        if missing_api:
            failures.append(
                Failure(
                    loc="docs/split-check-index-pack.json",
                    problem=f"some PRD APIs are not covered by stories ({len(missing_api)}): {_examples_summary(missing_api)}",
                    expected="every PRD API-### assigned to exactly 1 story",
                    impact="API work has no owning story",
                    fix="fix docs/split-plan-pack.json api_assignments to cover every PRD API-### exactly once",
                )
            )
        if extra_api:
            failures.append(
                Failure(
                    loc="docs/split-check-index-pack.json",
                    problem=f"unknown API ids referenced ({len(extra_api)}): {_examples_summary(extra_api)}",
                    expected="API ids exist in PRD api.endpoints[].id",
                    impact="execution plan references unknown endpoints",
                    fix="fix docs/split-plan-pack.json api_assignments to use existing PRD API-### ids",
                )
            )

    return failures

