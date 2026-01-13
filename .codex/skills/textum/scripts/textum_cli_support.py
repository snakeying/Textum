from __future__ import annotations

from pathlib import Path
from typing import Any

from prd_pack import Failure, check_prd_pack, normalize_prd_pack, read_prd_pack, write_prd_pack
from scaffold_pack import (
    check_scaffold_pack,
    normalize_scaffold_pack,
    read_scaffold_pack,
    write_scaffold_pack,
)


def _print_failures(failures: list[Failure]) -> None:
    print("FAIL")
    for failure in failures:
        print(
            "- "
            + "; ".join(
                [
                    f"loc={failure.loc}",
                    f"problem={failure.problem}",
                    f"expected={failure.expected}",
                    f"impact={failure.impact}",
                    f"fix={failure.fix}",
                ]
            )
        )


def _load_prd_pack(paths: dict[str, Path]) -> tuple[dict[str, Any] | None, list[Failure]]:
    prd_pack, read_failures = read_prd_pack(paths["prd_pack"])
    if read_failures:
        return None, read_failures
    assert prd_pack is not None
    return prd_pack, []


def _normalize_prd_pack_in_place(
    prd_pack: dict[str, Any], *, write_back_path: Path | None
) -> tuple[bool, list[Failure]]:
    updated, id_failures = normalize_prd_pack(prd_pack)
    if id_failures:
        return False, id_failures
    if updated and write_back_path is not None:
        write_prd_pack(write_back_path, prd_pack)
    return updated, []


def _load_prd_pack_and_normalize(
    paths: dict[str, Path], *, fix: bool
) -> tuple[dict[str, Any] | None, bool, list[Failure]]:
    prd_pack, read_failures = _load_prd_pack(paths)
    if read_failures:
        return None, False, read_failures
    assert prd_pack is not None

    updated, id_failures = _normalize_prd_pack_in_place(
        prd_pack, write_back_path=paths["prd_pack"] if fix else None
    )
    if id_failures:
        return None, updated, id_failures

    return prd_pack, updated, []


def _ensure_prd_ready(prd_pack: dict[str, Any], *, prd_pack_path: Path) -> list[Failure]:
    _, id_failures = _normalize_prd_pack_in_place(prd_pack, write_back_path=None)
    if id_failures:
        return id_failures
    ready, check_failures = check_prd_pack(prd_pack)
    if not ready:
        return check_failures
    return []


def _load_prd_pack_and_ensure_ready(paths: dict[str, Path]) -> tuple[dict[str, Any] | None, list[Failure]]:
    prd_pack, read_failures = _load_prd_pack(paths)
    if read_failures:
        return None, read_failures
    assert prd_pack is not None

    prd_ready_failures = _ensure_prd_ready(prd_pack, prd_pack_path=paths["prd_pack"])
    if prd_ready_failures:
        return None, prd_ready_failures

    return prd_pack, []


def _ensure_scaffold_ready(
    scaffold_pack: dict[str, object],
    *,
    prd_pack_path: Path,
    prd_pack: dict[str, object],
    scaffold_pack_path: Path,
    fix: bool,
) -> tuple[bool, list[Failure]]:
    updated, failures = normalize_scaffold_pack(scaffold_pack, prd_pack_path=prd_pack_path, prd_pack=prd_pack)
    if failures:
        return updated, failures
    if updated and fix:
        write_scaffold_pack(scaffold_pack_path, scaffold_pack)  # type: ignore[arg-type]
    ready, check_failures = check_scaffold_pack(scaffold_pack)  # type: ignore[arg-type]
    if not ready:
        return updated, check_failures
    return updated, []


def _load_scaffold_pack_and_ensure_ready(
    paths: dict[str, Path], *, prd_pack: dict[str, Any], fix: bool
) -> tuple[dict[str, Any] | None, bool, list[Failure]]:
    scaffold_pack, read_failures = read_scaffold_pack(paths["scaffold_pack"])
    if read_failures:
        return None, False, read_failures
    assert scaffold_pack is not None

    updated, ready_failures = _ensure_scaffold_ready(
        scaffold_pack,  # type: ignore[arg-type]
        prd_pack_path=paths["prd_pack"],
        prd_pack=prd_pack,  # type: ignore[arg-type]
        scaffold_pack_path=paths["scaffold_pack"],
        fix=fix,
    )
    if ready_failures:
        return None, updated, ready_failures

    return scaffold_pack, updated, []


def _require_scaffold_extracted_modules_index(
    *, scaffold_pack: dict[str, Any], prd_pack: dict[str, Any]
) -> list[Failure]:
    extracted = scaffold_pack.get("extracted")
    if not isinstance(extracted, dict):
        return [
            Failure(
                loc="docs/scaffold-pack.json:$.extracted",
                problem="missing extracted section",
                expected="extracted populated by scaffold check",
                impact="cannot validate story modules without high-noise failures",
                fix="run: textum scaffold check",
            )
        ]

    modules_index = extracted.get("modules_index")
    if not isinstance(modules_index, list):
        return [
            Failure(
                loc="docs/scaffold-pack.json:$.extracted.modules_index",
                problem="missing extracted.modules_index",
                expected="modules_index populated by scaffold check",
                impact="cannot validate story modules without high-noise failures",
                fix="run: textum scaffold check",
            )
        ]

    prd_modules = prd_pack.get("modules")
    prd_has_modules = isinstance(prd_modules, list) and any(
        isinstance(module_row, dict)
        and isinstance(module_row.get("id"), str)
        and module_row["id"].strip()
        for module_row in prd_modules
    )
    index_has_ids = any(
        isinstance(row, dict) and isinstance(row.get("id"), str) and row["id"].strip() for row in modules_index
    )
    if prd_has_modules and not index_has_ids:
        return [
            Failure(
                loc="docs/scaffold-pack.json:$.extracted.modules_index",
                problem="modules_index is empty/unusable",
                expected="modules_index contains PRD module ids",
                impact="cannot validate story modules without high-noise failures",
                fix="run: textum scaffold check",
            )
        ]
    return []

