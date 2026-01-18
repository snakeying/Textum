from __future__ import annotations

from typing import Any

from .prd_slices_writer import SliceWriter


def write_prd_slices_part_a(*, writer: SliceWriter, source: dict[str, Any], prd_pack: dict[str, Any]) -> None:
    assumptions_constraints_items = (
        prd_pack.get("assumptions_constraints") if isinstance(prd_pack.get("assumptions_constraints"), list) else []
    )

    def build_assumptions_constraints(part_items: list[Any]) -> dict[str, Any]:
        return {
            "schema_version": "prd-slice-assumptions-constraints@v1",
            "source": source,
            "assumptions_constraints": part_items,
        }

    writer.write_chunked_parts(
        kind="assumptions_constraints",
        items=assumptions_constraints_items,
        build_obj=build_assumptions_constraints,
        loc="$.assumptions_constraints",
        item_label="assumption/constraint",
        single_filename="assumptions_constraints.json",
        part_filename=lambda i: f"assumptions_constraints.part-{i:03d}.json",
        count_from_obj=lambda obj: len(obj.get("assumptions_constraints", []))
        if isinstance(obj.get("assumptions_constraints"), list)
        else 0,
    )

    roles_items = prd_pack.get("roles") if isinstance(prd_pack.get("roles"), list) else []

    def build_roles(part_items: list[Any]) -> dict[str, Any]:
        return {
            "schema_version": "prd-slice-roles@v1",
            "source": source,
            "roles": part_items,
        }

    writer.write_chunked_parts(
        kind="roles",
        items=roles_items,
        build_obj=build_roles,
        loc="$.roles",
        item_label="role",
        single_filename="roles.json",
        part_filename=lambda i: f"roles.part-{i:03d}.json",
        count_from_obj=lambda obj: len(obj.get("roles", [])) if isinstance(obj.get("roles"), list) else 0,
    )

    permission_matrix_obj = prd_pack.get("permission_matrix") if isinstance(prd_pack.get("permission_matrix"), dict) else {}
    permission_ops = (
        permission_matrix_obj.get("operations") if isinstance(permission_matrix_obj.get("operations"), list) else []
    )

    def build_permission_ops(part_items: list[Any]) -> dict[str, Any]:
        return {
            "schema_version": "prd-slice-permission-matrix-operations@v1",
            "source": source,
            "permission_matrix": {"operations": part_items},
        }

    writer.write_chunked_parts(
        kind="permission_matrix_operations",
        items=permission_ops,
        build_obj=build_permission_ops,
        loc="$.permission_matrix.operations",
        item_label="permission operation",
        single_filename="permission_matrix_operations.json",
        part_filename=lambda i: f"permission_matrix_operations.part-{i:03d}.json",
        count_from_obj=lambda obj: len(obj.get("permission_matrix", {}).get("operations", []))
        if isinstance(obj.get("permission_matrix"), dict)
        else 0,
    )

    nfr_items = prd_pack.get("nfr") if isinstance(prd_pack.get("nfr"), list) else []

    def build_nfr(part_items: list[Any]) -> dict[str, Any]:
        return {
            "schema_version": "prd-slice-nfr@v1",
            "source": source,
            "nfr": part_items,
        }

    writer.write_chunked_parts(
        kind="nfr",
        items=nfr_items,
        build_obj=build_nfr,
        loc="$.nfr",
        item_label="nfr item",
        single_filename="nfr.json",
        part_filename=lambda i: f"nfr.part-{i:03d}.json",
        count_from_obj=lambda obj: len(obj.get("nfr", [])) if isinstance(obj.get("nfr"), list) else 0,
    )

    states = {
        "schema_version": "prd-slice-states-enums@v1",
        "source": source,
        "states_enums": prd_pack.get("states_enums"),
    }
    writer.write_part("states_enums", "states_enums.json", states)

    ui_routes_items = prd_pack.get("ui_routes") if isinstance(prd_pack.get("ui_routes"), list) else []
    ui_routes_obj = {
        "schema_version": "prd-slice-ui-routes@v1",
        "source": source,
        "ui_routes": ui_routes_items,
    }
    writer.write_part("ui_routes", "ui_routes.json", ui_routes_obj, count=len(ui_routes_items))

    br_items = prd_pack.get("business_rules") if isinstance(prd_pack.get("business_rules"), list) else []
    br_obj = {
        "schema_version": "prd-slice-business-rules@v1",
        "source": source,
        "business_rules": br_items,
    }
    writer.write_part("business_rules", "business_rules.json", br_obj, count=len(br_items))

    api_obj = prd_pack.get("api") if isinstance(prd_pack.get("api"), dict) else {}
    api_meta = dict(api_obj)
    api_meta["endpoints"] = []
    writer.write_part(
        "api_meta",
        "api_meta.json",
        {"schema_version": "prd-slice-api-meta@v1", "source": source, "api": api_meta},
    )

    api_endpoints = api_obj.get("endpoints") if isinstance(api_obj.get("endpoints"), list) else []

    def build_api_endpoints(part_items: list[Any]) -> dict[str, Any]:
        return {
            "schema_version": "prd-slice-api-endpoints@v1",
            "source": source,
            "api": {"endpoints": part_items},
        }

    writer.write_chunked_parts(
        kind="api_endpoints",
        items=api_endpoints,
        build_obj=build_api_endpoints,
        loc="$.api.endpoints",
        item_label="api endpoint",
        single_filename="api_endpoints.json",
        part_filename=lambda i: f"api_endpoints.part-{i:03d}.json",
        count_from_obj=lambda obj: len(obj.get("api", {}).get("endpoints", []))
        if isinstance(obj.get("api"), dict)
        else 0,
        id_list_from_obj=lambda obj: [
            e.get("id")
            for e in obj.get("api", {}).get("endpoints", [])
            if isinstance(e, dict) and isinstance(e.get("id"), str)
        ]
        if isinstance(obj.get("api"), dict)
        else [],
    )

