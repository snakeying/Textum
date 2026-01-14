from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

from prd_pack_types import Failure
from prd_slices_types import SliceBudget
from prd_slices_utils import chunk_list, id_range, rel_posix, write_json


@dataclass
class SliceWriter:
    out_dir: Path
    budget: SliceBudget
    workspace_root: Path
    written: list[Path] = field(default_factory=list)
    parts_index: list[dict[str, Any]] = field(default_factory=list)
    failures: list[Failure] = field(default_factory=list)

    def write_part(self, kind: str, filename: str, obj: dict[str, Any], *, count: int | None = None) -> bool:
        path = self.out_dir / filename
        lines, chars = write_json(path, obj)
        if lines > self.budget.max_lines or chars > self.budget.max_chars:
            self.failures.append(
                Failure(
                    loc=f"docs/prd-slices/{filename}",
                    problem=f"slice exceeds budget: {lines} lines, {chars} chars",
                    expected=f"<= {self.budget.max_lines} lines and <= {self.budget.max_chars} chars",
                    impact="slice would pollute model attention/context",
                    fix="increase slice budget (max_lines/max_chars)",
                )
            )
            return False

        self.written.append(path)
        entry: dict[str, Any] = {
            "kind": kind,
            "path": rel_posix(path, self.workspace_root),
            "lines": lines,
            "chars": chars,
        }
        if count is not None:
            entry["count"] = count
        self.parts_index.append(entry)
        return True

    def write_chunked_parts(
        self,
        *,
        kind: str,
        items: list[Any],
        build_obj: Callable[[list[Any]], dict[str, Any]],
        loc: str,
        item_label: str,
        single_filename: str,
        part_filename: Callable[[int], str],
        count_from_obj: Callable[[dict[str, Any]], int],
        id_list_from_obj: Callable[[dict[str, Any]], list[str]] | None = None,
    ) -> None:
        parts, part_failures = chunk_list(items, build_obj, budget=self.budget, loc=loc, item_label=item_label)
        self.failures.extend(part_failures)
        for part_index, part_obj in enumerate(parts, start=1):
            filename = single_filename if len(parts) == 1 else part_filename(part_index)
            ok = self.write_part(kind, filename, part_obj, count=count_from_obj(part_obj))
            if not ok or id_list_from_obj is None:
                continue
            first_id, last_id = id_range(id_list_from_obj(part_obj))
            if first_id and last_id:
                self.parts_index[-1]["id_range"] = f"{first_id}..{last_id}"

    def write_index(self, *, source: dict[str, Any]) -> None:
        index_obj = {
            "schema_version": "prd-slices-index@v1",
            "source": source,
            "budget": {"max_lines": self.budget.max_lines, "max_chars": self.budget.max_chars},
            "parts": self.parts_index,
        }
        index_path = self.out_dir / "index.json"
        index_lines, index_chars = write_json(index_path, index_obj)
        if index_lines > self.budget.max_lines or index_chars > self.budget.max_chars:
            self.failures.append(
                Failure(
                    loc=rel_posix(index_path, self.workspace_root),
                    problem=f"index exceeds budget: {index_lines} lines, {index_chars} chars",
                    expected=f"<= {self.budget.max_lines} lines and <= {self.budget.max_chars} chars",
                    impact="index would pollute model attention/context",
                    fix="increase slice budget (max_lines/max_chars)",
                )
            )
        self.written.append(index_path)
