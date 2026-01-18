from __future__ import annotations

from typing import Any

from textum.prd.prd_pack_types import API_ID_RE, FP_ID_RE, LANDING_PREFIXES, TBL_ID_RE, Failure
from .story_check_utils import require_dict, require_list, require_non_empty_str


def validate_story_details(
    *,
    story: dict[str, Any],
    regenerate_story_fix: str,
    fp_ids: list[str],
    prd_api: list[str],
    prd_tbl: list[str],
) -> tuple[list[dict[str, Any]], dict[str, str], list[Failure]]:
    failures: list[Failure] = []

    details, details_failures = require_dict(story.get("details"), loc="$.details")
    failures += details_failures
    if details is None:
        return [], {}, failures

    feature_points, fp_failures = require_list(details.get("feature_points"), loc="$.details.feature_points")
    failures += fp_failures
    fp_ids_from_details: list[str] = []
    if feature_points is not None:
        for idx, fp in enumerate(feature_points):
            if not isinstance(fp, dict):
                failures.append(
                    Failure(
                        loc=f"$.details.feature_points[{idx}]",
                        problem=f"expected object, got {type(fp).__name__}",
                        expected="feature point object",
                        impact="cannot execute story",
                        fix=regenerate_story_fix,
                    )
                )
                continue
            fp_id = fp.get("id")
            if not isinstance(fp_id, str) or FP_ID_RE.match(fp_id) is None:
                failures.append(
                    Failure(
                        loc=f"$.details.feature_points[{idx}].id",
                        problem=f"invalid fp id: {fp_id!r}",
                        expected="FP-###",
                        impact="cannot map feature points",
                        fix=regenerate_story_fix,
                    )
                )
            else:
                fp_ids_from_details.append(fp_id)
            failures += require_non_empty_str(fp.get("desc"), loc=f"$.details.feature_points[{idx}].desc")
            landing, landing_failures = require_list(fp.get("landing"), loc=f"$.details.feature_points[{idx}].landing")
            failures += landing_failures
            if landing is not None:
                for j, item in enumerate(landing):
                    if not isinstance(item, str):
                        failures.append(
                            Failure(
                                loc=f"$.details.feature_points[{idx}].landing[{j}]",
                                problem=f"expected landing token string, got {type(item).__name__}",
                                expected="string landing token",
                                impact="landing tokens invalid",
                                fix=regenerate_story_fix,
                            )
                        )
                        continue
                    if item == "N/A":
                        continue
                    if not item.startswith(LANDING_PREFIXES):
                        failures.append(
                            Failure(
                                loc=f"$.details.feature_points[{idx}].landing[{j}]",
                                problem=f"invalid landing token: {item}",
                                expected=f"'N/A' or startswith one of {', '.join(LANDING_PREFIXES)}",
                                impact="landing tokens invalid",
                                fix=regenerate_story_fix,
                            )
                        )

    if set(fp_ids) != set(fp_ids_from_details):
        failures.append(
            Failure(
                loc="$.fp_ids / $.details.feature_points[].id",
                problem="fp_ids does not match feature_points ids",
                expected="same set of FP-### ids",
                impact="story is internally inconsistent",
                fix=regenerate_story_fix,
            )
        )

    api_endpoints, api_failures = require_list(details.get("api_endpoints"), loc="$.details.api_endpoints")
    failures += api_failures
    api_ids_from_details: list[str] = []
    api_endpoints_ctx: list[dict[str, Any]] = []
    if api_endpoints is not None:
        for idx, ep in enumerate(api_endpoints):
            if not isinstance(ep, dict):
                failures.append(
                    Failure(
                        loc=f"$.details.api_endpoints[{idx}]",
                        problem=f"expected object, got {type(ep).__name__}",
                        expected="api endpoint object",
                        impact="cannot implement API",
                        fix=regenerate_story_fix,
                    )
                )
                continue
            api_endpoints_ctx.append(ep)
            ep_id = ep.get("id")
            if not isinstance(ep_id, str) or API_ID_RE.match(ep_id) is None:
                failures.append(
                    Failure(
                        loc=f"$.details.api_endpoints[{idx}].id",
                        problem=f"invalid api id: {ep_id!r}",
                        expected="API-###",
                        impact="cannot map API work",
                        fix=regenerate_story_fix,
                    )
                )
            else:
                api_ids_from_details.append(ep_id)
            failures += require_non_empty_str(ep.get("method"), loc=f"$.details.api_endpoints[{idx}].method")
            failures += require_non_empty_str(ep.get("path"), loc=f"$.details.api_endpoints[{idx}].path")

    if set(prd_api) != set(api_ids_from_details):
        failures.append(
            Failure(
                loc="$.refs.prd_api / $.details.api_endpoints[].id",
                problem="refs.prd_api does not match api_endpoints ids",
                expected="same set of API-### ids",
                impact="story is internally inconsistent",
                fix=regenerate_story_fix,
            )
        )

    tables_overview, tbl_ov_failures = require_list(details.get("tables_overview"), loc="$.details.tables_overview")
    failures += tbl_ov_failures
    tbl_ids_from_details: list[str] = []
    tbl_name_by_id: dict[str, str] = {}
    if tables_overview is not None:
        for idx, row in enumerate(tables_overview):
            if not isinstance(row, dict):
                failures.append(
                    Failure(
                        loc=f"$.details.tables_overview[{idx}]",
                        problem=f"expected object, got {type(row).__name__}",
                        expected="table overview object",
                        impact="cannot implement data model",
                        fix=regenerate_story_fix,
                    )
                )
                continue
            row_id = row.get("id")
            if not isinstance(row_id, str) or TBL_ID_RE.match(row_id) is None:
                failures.append(
                    Failure(
                        loc=f"$.details.tables_overview[{idx}].id",
                        problem=f"invalid tbl id: {row_id!r}",
                        expected="TBL-###",
                        impact="cannot map data model work",
                        fix=regenerate_story_fix,
                    )
                )
            else:
                tbl_ids_from_details.append(row_id)
            name = row.get("name")
            if isinstance(row_id, str) and isinstance(name, str):
                tbl_name_by_id[row_id] = name
            failures += require_non_empty_str(name, loc=f"$.details.tables_overview[{idx}].name")

    if set(prd_tbl) != set(tbl_ids_from_details):
        failures.append(
            Failure(
                loc="$.refs.prd_tbl / $.details.tables_overview[].id",
                problem="refs.prd_tbl does not match tables_overview ids",
                expected="same set of TBL-### ids",
                impact="story is internally inconsistent",
                fix=regenerate_story_fix,
            )
        )

    return api_endpoints_ctx, tbl_name_by_id, failures

