from __future__ import annotations

from typing import Any

from .prd_slices_writer import SliceWriter


def write_prd_slices_part_b(*, writer: SliceWriter, source: dict[str, Any], prd_pack: dict[str, Any]) -> None:
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

