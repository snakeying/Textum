from __future__ import annotations

from typing import Any

from prd_pack_types import API_ID_RE, BR_ID_RE, FP_ID_RE, LANDING_PREFIXES, MODULE_ID_RE, TBL_ID_RE, Failure
from split_pack_types import KEBAB_SLUG_RE, STORY_NAME_RE, STORY_SCHEMA_VERSION
from story_check_utils import check_id_list, require_dict, require_list, require_non_empty_str


def validate_story_internal(*, story: dict[str, Any], n: int) -> tuple[dict[str, Any], list[Failure]]:
    failures: list[Failure] = []
    ctx: dict[str, Any] = {
        "modules": [],
        "fp_ids": [],
        "prd_api": [],
        "prd_tbl": [],
        "prd_br": [],
        "api_endpoints": [],
        "tbl_name_by_id": {},
    }

    if story.get("schema_version") != STORY_SCHEMA_VERSION:
        failures.append(
            Failure(
                loc="$.schema_version",
                problem=f"schema_version must be {STORY_SCHEMA_VERSION}",
                expected=STORY_SCHEMA_VERSION,
                impact="cannot trust story format",
                fix="regenerate story via: textum split generate",
            )
        )

    failures += require_non_empty_str(story.get("story"), loc="$.story")
    expected_story_name = f"Story {n}"
    if story.get("story") != expected_story_name:
        failures.append(
            Failure(
                loc="$.story",
                problem=f"story must equal {expected_story_name}",
                expected=expected_story_name,
                impact="ambiguous story identity",
                fix="regenerate story via: textum split generate",
            )
        )
    if story.get("n") != n:
        failures.append(
            Failure(
                loc="$.n",
                problem=f"n must equal {n}",
                expected=str(n),
                impact="ambiguous story identity",
                fix="regenerate story via: textum split generate",
            )
        )

    slug = story.get("slug")
    if not isinstance(slug, str) or KEBAB_SLUG_RE.match(slug) is None:
        failures.append(
            Failure(
                loc="$.slug",
                problem=f"invalid slug: {slug!r}",
                expected="kebab-case string",
                impact="file naming and routing break",
                fix="regenerate story via: textum split generate",
            )
        )

    failures += require_non_empty_str(story.get("title"), loc="$.title")
    failures += require_non_empty_str(story.get("goal"), loc="$.goal")

    modules, module_failures = check_id_list(story.get("modules"), loc="$.modules", pattern=MODULE_ID_RE, label="module")
    failures += module_failures
    ctx["modules"] = modules

    prereq, prereq_failures = require_list(story.get("prereq_stories"), loc="$.prereq_stories")
    failures += prereq_failures
    prereq_numbers: list[int] = []
    if prereq is not None:
        for idx, item in enumerate(prereq):
            if not isinstance(item, str) or STORY_NAME_RE.match(item) is None:
                failures.append(
                    Failure(
                        loc=f"$.prereq_stories[{idx}]",
                        problem=f"invalid prereq story ref: {item!r}",
                        expected="Story <number>",
                        impact="dependency graph invalid",
                        fix=f"fix $.prereq_stories[{idx}]",
                    )
                )
                continue
            num = int(STORY_NAME_RE.match(item).group(1))
            prereq_numbers.append(num)
            if num >= n:
                failures.append(
                    Failure(
                        loc=f"$.prereq_stories[{idx}]",
                        problem=f"prereq story must be < {n}, got {item}",
                        expected="only earlier stories",
                        impact="cannot execute in order",
                        fix=f"remove {item} from prereq_stories",
                    )
                )
    if len(set(prereq_numbers)) != len(prereq_numbers):
        failures.append(
            Failure(
                loc="$.prereq_stories",
                problem="duplicate prereq stories",
                expected="unique prereq story refs",
                impact="dependency graph ambiguous",
                fix="dedupe $.prereq_stories",
            )
        )

    fp_ids, fp_id_failures = check_id_list(story.get("fp_ids"), loc="$.fp_ids", pattern=FP_ID_RE, label="fp")
    failures += fp_id_failures
    ctx["fp_ids"] = fp_ids

    refs, refs_failures = require_dict(story.get("refs"), loc="$.refs")
    failures += refs_failures
    prd_api: list[str] = []
    prd_tbl: list[str] = []
    prd_br: list[str] = []
    if refs is not None:
        prd_api, failures_api = check_id_list(refs.get("prd_api"), loc="$.refs.prd_api", pattern=API_ID_RE, label="api")
        prd_tbl, failures_tbl = check_id_list(refs.get("prd_tbl"), loc="$.refs.prd_tbl", pattern=TBL_ID_RE, label="tbl")
        prd_br, failures_br = check_id_list(refs.get("prd_br"), loc="$.refs.prd_br", pattern=BR_ID_RE, label="br")
        failures += failures_api + failures_tbl + failures_br
        _, failures_gc = require_list(refs.get("gc_br"), loc="$.refs.gc_br")
        failures += failures_gc
    ctx["prd_api"] = prd_api
    ctx["prd_tbl"] = prd_tbl
    ctx["prd_br"] = prd_br

    details, details_failures = require_dict(story.get("details"), loc="$.details")
    failures += details_failures
    if details is None:
        return ctx, failures

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
                        fix=f"fix $.details.feature_points[{idx}]",
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
                        fix=f"fix $.details.feature_points[{idx}].id",
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
                                fix=f"fix $.details.feature_points[{idx}].landing[{j}]",
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
                                fix=f"fix landing token at $.details.feature_points[{idx}].landing[{j}]",
                            )
                        )

    if set(fp_ids) != set(fp_ids_from_details):
        failures.append(
            Failure(
                loc="$.fp_ids / $.details.feature_points[].id",
                problem="fp_ids does not match feature_points ids",
                expected="same set of FP-### ids",
                impact="story is internally inconsistent",
                fix="regenerate story via: textum split generate",
            )
        )

    api_endpoints, api_failures = require_list(details.get("api_endpoints"), loc="$.details.api_endpoints")
    failures += api_failures
    api_ids_from_details: list[str] = []
    if api_endpoints is not None:
        for idx, ep in enumerate(api_endpoints):
            if not isinstance(ep, dict):
                failures.append(
                    Failure(
                        loc=f"$.details.api_endpoints[{idx}]",
                        problem=f"expected object, got {type(ep).__name__}",
                        expected="api endpoint object",
                        impact="cannot implement API",
                        fix=f"fix $.details.api_endpoints[{idx}]",
                    )
                )
                continue
            ep_id = ep.get("id")
            if not isinstance(ep_id, str) or API_ID_RE.match(ep_id) is None:
                failures.append(
                    Failure(
                        loc=f"$.details.api_endpoints[{idx}].id",
                        problem=f"invalid api id: {ep_id!r}",
                        expected="API-###",
                        impact="cannot map API work",
                        fix=f"fix $.details.api_endpoints[{idx}].id",
                    )
                )
            else:
                api_ids_from_details.append(ep_id)
            failures += require_non_empty_str(ep.get("method"), loc=f"$.details.api_endpoints[{idx}].method")
            failures += require_non_empty_str(ep.get("path"), loc=f"$.details.api_endpoints[{idx}].path")
    ctx["api_endpoints"] = api_endpoints or []

    if set(prd_api) != set(api_ids_from_details):
        failures.append(
            Failure(
                loc="$.refs.prd_api / $.details.api_endpoints[].id",
                problem="refs.prd_api does not match api_endpoints ids",
                expected="same set of API-### ids",
                impact="story is internally inconsistent",
                fix="regenerate story via: textum split generate",
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
                        fix=f"fix $.details.tables_overview[{idx}]",
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
                        fix=f"fix $.details.tables_overview[{idx}].id",
                    )
                )
            else:
                tbl_ids_from_details.append(row_id)
            name = row.get("name")
            if isinstance(row_id, str) and isinstance(name, str):
                tbl_name_by_id[row_id] = name
            failures += require_non_empty_str(name, loc=f"$.details.tables_overview[{idx}].name")
    ctx["tbl_name_by_id"] = tbl_name_by_id

    if set(prd_tbl) != set(tbl_ids_from_details):
        failures.append(
            Failure(
                loc="$.refs.prd_tbl / $.details.tables_overview[].id",
                problem="refs.prd_tbl does not match tables_overview ids",
                expected="same set of TBL-### ids",
                impact="story is internally inconsistent",
                fix="regenerate story via: textum split generate",
            )
        )

    return ctx, failures
