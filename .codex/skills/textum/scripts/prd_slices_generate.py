from __future__ import annotations

import hashlib
import shutil
from pathlib import Path
from typing import Any

from prd_pack_types import Failure
from prd_slices_types import SliceBudget
from prd_slices_utils import (
    chunk_list,
    id_range,
    json_text,
    measure_json,
    rel_posix,
    sha256_file,
    write_json,
)


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

    written: list[Path] = []
    parts_index: list[dict[str, Any]] = []

    def write_part(kind: str, filename: str, obj: dict[str, Any], *, count: int | None = None) -> list[Failure]:
        path = out_dir / filename
        lines, chars = write_json(path, obj)
        if lines > budget.max_lines or chars > budget.max_chars:
            return [
                Failure(
                    loc=f"docs/prd-slices/{filename}",
                    problem=f"slice exceeds budget: {lines} lines, {chars} chars",
                    expected=f"<= {budget.max_lines} lines and <= {budget.max_chars} chars",
                    impact="slice would pollute model attention/context",
                    fix="increase slice budget or ensure the slice is chunked",
                )
            ]
        written.append(path)
        entry: dict[str, Any] = {
            "kind": kind,
            "path": rel_posix(path, workspace_root),
            "lines": lines,
            "chars": chars,
        }
        if count is not None:
            entry["count"] = count
        parts_index.append(entry)
        return []

    failures: list[Failure] = []

    overview = {
        "schema_version": "prd-slice-overview@v1",
        "source": source,
        "project": prd_pack.get("project"),
        "goals": prd_pack.get("goals"),
        "non_goals": prd_pack.get("non_goals"),
        "scope": prd_pack.get("scope"),
        "assumptions_constraints": prd_pack.get("assumptions_constraints"),
        "roles": prd_pack.get("roles"),
        "permission_matrix": prd_pack.get("permission_matrix"),
        "nfr": prd_pack.get("nfr"),
    }
    failures += write_part("overview", "overview.json", overview)

    states = {
        "schema_version": "prd-slice-states-enums@v1",
        "source": source,
        "states_enums": prd_pack.get("states_enums"),
    }
    failures += write_part("states_enums", "states_enums.json", states)

    ui_routes_items = prd_pack.get("ui_routes") if isinstance(prd_pack.get("ui_routes"), list) else []
    ui_routes_obj = {
        "schema_version": "prd-slice-ui-routes@v1",
        "source": source,
        "ui_routes": ui_routes_items,
    }
    failures += write_part("ui_routes", "ui_routes.json", ui_routes_obj, count=len(ui_routes_items))

    br_items = prd_pack.get("business_rules") if isinstance(prd_pack.get("business_rules"), list) else []
    br_obj = {
        "schema_version": "prd-slice-business-rules@v1",
        "source": source,
        "business_rules": br_items,
    }
    failures += write_part("business_rules", "business_rules.json", br_obj, count=len(br_items))

    api_obj = prd_pack.get("api") if isinstance(prd_pack.get("api"), dict) else {}
    api_meta = dict(api_obj)
    api_meta["endpoints"] = []
    failures += write_part(
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

    api_parts, api_part_failures = chunk_list(
        api_endpoints,
        build_api_endpoints,
        budget=budget,
        loc="$.api.endpoints",
        item_label="api endpoint",
    )
    failures += api_part_failures
    for part_index, part_obj in enumerate(api_parts, start=1):
        endpoints = part_obj.get("api", {}).get("endpoints", [])
        endpoint_ids = [e.get("id") for e in endpoints if isinstance(e, dict) and isinstance(e.get("id"), str)]
        first_id, last_id = id_range(endpoint_ids)
        filename = "api_endpoints.json" if len(api_parts) == 1 else f"api_endpoints.part-{part_index:03d}.json"
        failures += write_part("api_endpoints", filename, part_obj, count=len(endpoints))
        if first_id and last_id:
            parts_index[-1]["id_range"] = f"{first_id}..{last_id}"

    dm_obj = prd_pack.get("data_model") if isinstance(prd_pack.get("data_model"), dict) else {}
    dm_meta = dict(dm_obj)
    dm_meta["tables"] = []
    failures += write_part(
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

    dm_parts, dm_part_failures = chunk_list(
        dm_tables,
        build_dm_tables,
        budget=budget,
        loc="$.data_model.tables",
        item_label="data model table",
    )
    failures += dm_part_failures
    for part_index, part_obj in enumerate(dm_parts, start=1):
        tables = part_obj.get("data_model", {}).get("tables", [])
        table_ids = [t.get("id") for t in tables if isinstance(t, dict) and isinstance(t.get("id"), str)]
        first_id, last_id = id_range(table_ids)
        filename = "data_model_tables.json" if len(dm_parts) == 1 else f"data_model_tables.part-{part_index:03d}.json"
        failures += write_part("data_model_tables", filename, part_obj, count=len(tables))
        if first_id and last_id:
            parts_index[-1]["id_range"] = f"{first_id}..{last_id}"

    modules = prd_pack.get("modules") if isinstance(prd_pack.get("modules"), list) else []

    def build_modules(part_items: list[Any]) -> dict[str, Any]:
        return {
            "schema_version": "prd-slice-modules@v1",
            "source": source,
            "modules": part_items,
        }

    module_parts, module_part_failures = chunk_list(
        modules,
        build_modules,
        budget=budget,
        loc="$.modules",
        item_label="module",
    )
    failures += module_part_failures
    for part_index, part_obj in enumerate(module_parts, start=1):
        part_modules = part_obj.get("modules", [])
        module_ids = [m.get("id") for m in part_modules if isinstance(m, dict) and isinstance(m.get("id"), str)]
        first_id, last_id = id_range(module_ids)
        filename = "modules.json" if len(module_parts) == 1 else f"modules.part-{part_index:03d}.json"
        failures += write_part("modules", filename, part_obj, count=len(part_modules))
        if first_id and last_id:
            parts_index[-1]["id_range"] = f"{first_id}..{last_id}"

    index_obj = {
        "schema_version": "prd-slices-index@v1",
        "source": source,
        "budget": {"max_lines": budget.max_lines, "max_chars": budget.max_chars},
        "parts": parts_index,
    }
    index_path = out_dir / "index.json"
    index_lines, index_chars = write_json(index_path, index_obj)
    if index_lines > budget.max_lines or index_chars > budget.max_chars:
        failures.append(
            Failure(
                loc=rel_posix(index_path, workspace_root),
                problem=f"index exceeds budget: {index_lines} lines, {index_chars} chars",
                expected=f"<= {budget.max_lines} lines and <= {budget.max_chars} chars",
                impact="index would pollute model attention/context",
                fix="reduce index metadata (e.g., remove id ranges) or increase slice budget",
            )
        )
    written.append(index_path)

    return written, failures

