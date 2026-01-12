from __future__ import annotations

from pathlib import Path
from typing import Any

from prd_pack_types import PLACEHOLDER_SENTINEL, Failure
from prd_slices_types import SliceBudget
from split_pack_io import read_json_object
from story_exec_types import STORY_EXEC_INDEX_FILENAME, STORY_EXEC_INDEX_SCHEMA_VERSION

def _scan_text(text: str, *, loc: str) -> list[Failure]:
    failures: list[Failure] = []
    if "```" in text:
        failures.append(
            Failure(
                loc=loc,
                problem="contains fenced code block marker ```",
                expected="no ``` in exec pack files",
                impact="would pollute model attention/context",
                fix=f"remove ``` from {loc}",
            )
        )
    if PLACEHOLDER_SENTINEL in text:
        failures.append(
            Failure(
                loc=loc,
                problem=f"contains placeholder sentinel {PLACEHOLDER_SENTINEL}",
                expected="no placeholders in exec pack files",
                impact="ambiguous execution instructions",
                fix=f"remove {PLACEHOLDER_SENTINEL} from {loc}",
            )
        )
    return failures


def _check_budget(path: Path, *, text: str, budget: SliceBudget) -> list[Failure]:
    lines = text.count("\n")
    chars = len(text)
    if lines <= budget.max_lines and chars <= budget.max_chars:
        return []
    return [
        Failure(
            loc=path.as_posix(),
            problem=f"file exceeds budget: {lines} lines, {chars} chars",
            expected=f"<= {budget.max_lines} lines and <= {budget.max_chars} chars",
            impact="would pollute model attention/context",
            fix="split the story into smaller stories",
        )
    ]


def check_story_exec_pack(*, workspace_root: Path, exec_dir: Path, budget: SliceBudget) -> list[Failure]:
    failures: list[Failure] = []
    workspace_root = workspace_root.resolve()
    exec_dir = exec_dir.resolve()
    index_path = exec_dir / STORY_EXEC_INDEX_FILENAME
    index_obj, index_failures = read_json_object(
        index_path,
        missing_fix=f"regenerate exec pack under {exec_dir.as_posix()}",
    )
    if index_failures:
        return index_failures
    assert index_obj is not None

    if index_obj.get("schema_version") != STORY_EXEC_INDEX_SCHEMA_VERSION:
        failures.append(
            Failure(
                loc=f"{index_path.as_posix()}:$.schema_version",
                problem=f"schema_version must be {STORY_EXEC_INDEX_SCHEMA_VERSION}",
                expected=STORY_EXEC_INDEX_SCHEMA_VERSION,
                impact="cannot trust exec index format",
                fix=f"regenerate {index_path.as_posix()}",
            )
        )
        return failures

    read_list = index_obj.get("read")
    if not isinstance(read_list, list) or not read_list:
        failures.append(
            Failure(
                loc=f"{index_path.as_posix()}:$.read",
                problem="read must be a non-empty array of file paths",
                expected="non-empty array of relative paths",
                impact="exec pack has no entry read list",
                fix=f"regenerate {index_path.as_posix()}",
            )
        )
        return failures

    for idx, rel in enumerate(read_list):
        if not isinstance(rel, str) or not rel.strip():
            failures.append(
                Failure(
                    loc=f"{index_path.as_posix()}:$.read[{idx}]",
                    problem=f"invalid path: {rel!r}",
                    expected="non-empty string path",
                    impact="cannot resolve exec pack file",
                    fix=f"regenerate {index_path.as_posix()}",
                )
            )
            continue
        rel_path = Path(rel)
        if rel_path.is_absolute():
            failures.append(
                Failure(
                    loc=f"{index_path.as_posix()}:$.read[{idx}]",
                    problem=f"absolute path is not allowed: {rel}",
                    expected="relative path under the exec pack directory",
                    impact="exec pack can escape its sandbox and pollute context",
                    fix=f"regenerate exec pack under {exec_dir.as_posix()}",
                )
            )
            continue

        path = (workspace_root / rel_path).resolve()
        if not path.is_relative_to(workspace_root):
            failures.append(
                Failure(
                    loc=f"{index_path.as_posix()}:$.read[{idx}]",
                    problem=f"path escapes workspace: {rel}",
                    expected="path stays under workspace root",
                    impact="exec pack can escape its sandbox and pollute context",
                    fix=f"regenerate exec pack under {exec_dir.as_posix()}",
                )
            )
            continue

        if not path.is_relative_to(exec_dir):
            failures.append(
                Failure(
                    loc=f"{index_path.as_posix()}:$.read[{idx}]",
                    problem=f"path is outside exec pack dir: {rel}",
                    expected=f"path stays under {exec_dir.as_posix()}",
                    impact="exec pack is not self-contained",
                    fix=f"regenerate exec pack under {exec_dir.as_posix()}",
                )
            )
            continue

        if not path.exists():
            failures.append(
                Failure(
                    loc=f"{index_path.as_posix()}:$.read[{idx}]",
                    problem=f"missing referenced file: {rel}",
                    expected="referenced file exists",
                    impact="exec pack is incomplete",
                    fix=f"regenerate exec pack under {exec_dir.as_posix()}",
                )
            )
            continue

        text = path.read_text(encoding="utf-8")
        failures += _scan_text(text, loc=rel)
        failures += _check_budget(path, text=text, budget=budget)

        obj, obj_failures = read_json_object(
            path,
            missing_fix=f"regenerate exec pack under {exec_dir.as_posix()}",
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
