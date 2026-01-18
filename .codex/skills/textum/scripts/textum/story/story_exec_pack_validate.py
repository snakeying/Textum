from __future__ import annotations

from pathlib import Path
from typing import Any

from textum.prd.prd_pack_types import PLACEHOLDER_SENTINEL, Failure
from textum.prd.prd_slices_types import SliceBudget
from textum.prd.prd_slices_utils import rel_posix
from textum.split.split_pack_io import read_json_object
from .story_exec_types import STORY_EXEC_INDEX_FILENAME, STORY_EXEC_INDEX_SCHEMA_VERSION


def _scan_text(text: str, *, loc: str, regen_fix: str) -> list[Failure]:
    failures: list[Failure] = []
    if "```" in text:
        failures.append(
            Failure(
                loc=loc,
                problem="contains fenced code block marker ```",
                expected="no ``` in exec pack files",
                impact="would pollute model attention/context",
                fix=regen_fix,
            )
        )
    if PLACEHOLDER_SENTINEL in text:
        failures.append(
            Failure(
                loc=loc,
                problem=f"contains placeholder sentinel {PLACEHOLDER_SENTINEL}",
                expected="no placeholders in exec pack files",
                impact="ambiguous execution instructions",
                fix=regen_fix,
            )
        )
    return failures


def _check_budget(path: Path, *, workspace_root: Path, text: str, budget: SliceBudget) -> list[Failure]:
    lines = text.count("\n")
    chars = len(text)
    if lines <= budget.max_lines and chars <= budget.max_chars:
        return []
    return [
        Failure(
            loc=rel_posix(path, workspace_root),
            problem=f"file exceeds budget: {lines} lines, {chars} chars",
            expected=f"<= {budget.max_lines} lines and <= {budget.max_chars} chars",
            impact="would pollute model attention/context",
            fix="split this story into smaller stories in docs/split-plan-pack.json",
        )
    ]


def check_story_exec_pack(*, workspace_root: Path, exec_dir: Path, budget: SliceBudget) -> list[Failure]:
    failures: list[Failure] = []
    workspace_root = workspace_root.resolve()
    exec_dir = exec_dir.resolve()
    exec_dir_rel = rel_posix(exec_dir, workspace_root)
    exec_dir_fix = f"regenerate exec pack under {exec_dir_rel}"
    index_path = exec_dir / STORY_EXEC_INDEX_FILENAME
    index_loc = rel_posix(index_path, workspace_root)
    index_obj, index_failures = read_json_object(
        index_path,
        missing_fix=exec_dir_fix,
    )
    if index_failures:
        return index_failures
    assert index_obj is not None

    if index_obj.get("schema_version") != STORY_EXEC_INDEX_SCHEMA_VERSION:
        failures.append(
            Failure(
                loc=f"{index_loc}:$.schema_version",
                problem=f"schema_version must be {STORY_EXEC_INDEX_SCHEMA_VERSION}",
                expected=STORY_EXEC_INDEX_SCHEMA_VERSION,
                impact="cannot trust exec index format",
                fix=f"regenerate {index_loc}",
            )
        )
        return failures

    read_list = index_obj.get("read")
    if not isinstance(read_list, list) or not read_list:
        failures.append(
            Failure(
                loc=f"{index_loc}:$.read",
                problem="read must be a non-empty array of file paths",
                expected="non-empty array of relative paths",
                impact="exec pack has no entry read list",
                fix=f"regenerate {index_loc}",
            )
        )
        return failures

    for idx, rel in enumerate(read_list):
        if not isinstance(rel, str) or not rel.strip():
            failures.append(
                Failure(
                    loc=f"{index_loc}:$.read[{idx}]",
                    problem=f"invalid path: {rel!r}",
                    expected="non-empty string path",
                    impact="cannot resolve exec pack file",
                    fix=f"regenerate {index_loc}",
                )
            )
            continue
        rel_path = Path(rel)
        if rel_path.is_absolute():
            failures.append(
                Failure(
                    loc=f"{index_loc}:$.read[{idx}]",
                    problem=f"absolute path is not allowed: {rel}",
                    expected="relative path under the exec pack directory",
                    impact="exec pack can escape its sandbox and pollute context",
                    fix=exec_dir_fix,
                )
            )
            continue

        path = (workspace_root / rel_path).resolve()
        if not path.is_relative_to(workspace_root):
            failures.append(
                Failure(
                    loc=f"{index_loc}:$.read[{idx}]",
                    problem=f"path escapes workspace: {rel}",
                    expected="path stays under workspace root",
                    impact="exec pack can escape its sandbox and pollute context",
                    fix=exec_dir_fix,
                )
            )
            continue

        if not path.is_relative_to(exec_dir):
            failures.append(
                Failure(
                    loc=f"{index_loc}:$.read[{idx}]",
                    problem=f"path is outside exec pack dir: {rel}",
                    expected=f"path stays under {exec_dir_rel}",
                    impact="exec pack is not self-contained",
                    fix=exec_dir_fix,
                )
            )
            continue

        if not path.exists():
            failures.append(
                Failure(
                    loc=f"{index_loc}:$.read[{idx}]",
                    problem=f"missing referenced file: {rel}",
                    expected="referenced file exists",
                    impact="exec pack is incomplete",
                    fix=exec_dir_fix,
                )
            )
            continue

        text = path.read_text(encoding="utf-8")
        failures += _scan_text(text, loc=rel, regen_fix=exec_dir_fix)
        failures += _check_budget(path, workspace_root=workspace_root, text=text, budget=budget)

        obj, obj_failures = read_json_object(
            path,
            missing_fix=exec_dir_fix,
        )
        failures += obj_failures
        if obj is None:
            continue
        if not isinstance(obj.get("schema_version"), str):
            failures.append(
                Failure(
                    loc=f"{rel}:$.schema_version",
                    problem="missing schema_version",
                    expected="schema_version string",
                    impact="cannot trust file format",
                    fix=f"regenerate {rel}",
                )
            )

    return failures

