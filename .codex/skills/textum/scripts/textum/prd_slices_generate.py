from __future__ import annotations

import hashlib
import shutil
from pathlib import Path
from typing import Any

from .prd_pack_types import Failure
from .prd_slices_types import SliceBudget
from .prd_slices_utils import json_text, rel_posix, sha256_file
from .prd_slices_writer import SliceWriter


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

    permission_matrix_obj = (
        prd_pack.get("permission_matrix") if isinstance(prd_pack.get("permission_matrix"), dict) else {}
    )
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
        count_from_obj=lambda obj: len(obj.get("api", {}).get("endpoints", [])) if isinstance(obj.get("api"), dict) else 0,
        id_list_from_obj=lambda obj: [
            e.get("id")
            for e in obj.get("api", {}).get("endpoints", [])
            if isinstance(e, dict) and isinstance(e.get("id"), str)
        ]
        if isinstance(obj.get("api"), dict)
        else [],
    )

    dm_obj = prd_pack.get("data_model") if isinstance(prd_pack.get("data_model"), dict) else {}
    dm_meta = dict(dm_obj)
    dm_meta["tables"] = []
    writer.write_part(
        "data_model_meta",
        "data_model_meta.json",
        {"schema_version": "prd-slice-data-model-meta@v1", "source": source, "data_model": dm_meta},
    )

    dm_tables = dm_obj.get("tables") if isinstance(dm_obj.get("tables"), list) else []

    def build_dm_tables(part_items: list[Any]) -> dict[str, Any]:
        return {
            "schema_version": "prd-slice-data-model-tables@v1",
            "source": source,
            "data_model": {"tables": part_items},
        }

    writer.write_chunked_parts(
        kind="data_model_tables",
        items=dm_tables,
        build_obj=build_dm_tables,
        loc="$.data_model.tables",
        item_label="data model table",
        single_filename="data_model_tables.json",
        part_filename=lambda i: f"data_model_tables.part-{i:03d}.json",
        count_from_obj=lambda obj: len(obj.get("data_model", {}).get("tables", []))
        if isinstance(obj.get("data_model"), dict)
        else 0,
        id_list_from_obj=lambda obj: [
            t.get("id")
            for t in obj.get("data_model", {}).get("tables", [])
            if isinstance(t, dict) and isinstance(t.get("id"), str)
        ]
        if isinstance(obj.get("data_model"), dict)
        else [],
    )

    modules = prd_pack.get("modules") if isinstance(prd_pack.get("modules"), list) else []

    def build_modules(part_items: list[Any]) -> dict[str, Any]:
        return {
            "schema_version": "prd-slice-modules@v1",
            "source": source,
            "modules": part_items,
        }

    writer.write_chunked_parts(
        kind="modules",
        items=modules,
        build_obj=build_modules,
        loc="$.modules",
        item_label="module",
        single_filename="modules.json",
        part_filename=lambda i: f"modules.part-{i:03d}.json",
        count_from_obj=lambda obj: len(obj.get("modules", [])) if isinstance(obj.get("modules"), list) else 0,
        id_list_from_obj=lambda obj: [
            m.get("id") for m in obj.get("modules", []) if isinstance(m, dict) and isinstance(m.get("id"), str)
        ]
        if isinstance(obj.get("modules"), list)
        else [],
    )

    writer.write_index(source=source)

    return writer.written, writer.failures

