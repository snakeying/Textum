from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from prd_pack import Failure

REPLAN_SCHEMA_VERSION = "textum-replan-pack@v1"


def _replan_pack_path(*, docs_dir: Path, stage_id: str) -> Path:
    return docs_dir / f"{stage_id}-replan-pack.json"


def _diagnostics_path(*, docs_dir: Path, stage_id: str) -> Path:
    return docs_dir / "diagnostics" / f"{stage_id}.md"


def _ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def _read_text(path: Path) -> str | None:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return None


def _write_text_if_changed(path: Path, content: str) -> bool:
    old = _read_text(path)
    if old == content:
        return False
    _ensure_dir(path.parent)
    path.write_text(content, encoding="utf-8")
    return True


def _write_json_if_changed(path: Path, obj: dict[str, Any]) -> bool:
    content = json.dumps(obj, ensure_ascii=False, indent=2) + "\n"
    return _write_text_if_changed(path, content)


def _item_dict(failure: Failure, *, severity: str) -> dict[str, Any]:
    return {
        "severity": severity,
        "loc": failure.loc,
        "problem": failure.problem,
        "expected": failure.expected,
        "impact": failure.impact,
        "fix": failure.fix,
    }


def write_check_artifacts(
    *,
    workspace_root: Path,
    stage_id: str,
    command: str,
    next_stage: str,
    failures: list[Failure],
    warnings: list[Failure] | None = None,
    extra: dict[str, Any] | None = None,
) -> tuple[str, list[str]]:
    docs_dir = workspace_root / "docs"
    replan_path = _replan_pack_path(docs_dir=docs_dir, stage_id=stage_id)
    diag_path = _diagnostics_path(docs_dir=docs_dir, stage_id=stage_id)

    warnings = warnings or []
    status = "FAIL" if failures else ("WARN" if warnings else "PASS")

    items: list[dict[str, Any]] = []
    for f in failures:
        items.append(_item_dict(f, severity="fail"))
    for w in warnings:
        items.append(_item_dict(w, severity="warn"))

    replan: dict[str, Any] = {
        "schema_version": REPLAN_SCHEMA_VERSION,
        "stage": stage_id,
        "status": status,
        "next": next_stage,
        "command": command,
        "items": items,
    }
    if extra:
        replan["extra"] = extra

    lines: list[str] = []
    lines.append(f"# Diagnostics: {stage_id}")
    lines.append("")
    lines.append(f"- status: {status}")
    lines.append(f"- next: {next_stage}")
    lines.append(f"- command: `{command}`")
    lines.append("")
    if not items:
        lines.append("No items.")
    else:
        lines.append("## Items")
        lines.append("")
        for item in items:
            sev = item.get("severity", "fail")
            prefix = "FAIL" if sev == "fail" else "WARN"
            lines.append(
                "- "
                + "; ".join(
                    [
                        f"[{prefix}]",
                        f"loc={item.get('loc')}",
                        f"problem={item.get('problem')}",
                        f"expected={item.get('expected')}",
                        f"impact={item.get('impact')}",
                        f"fix={item.get('fix')}",
                    ]
                )
            )
    diagnostics = "\n".join(lines) + "\n"

    wrote: list[str] = []
    if _write_json_if_changed(replan_path, replan):
        wrote.append(replan_path.relative_to(workspace_root).as_posix())
    if _write_text_if_changed(diag_path, diagnostics):
        wrote.append(diag_path.relative_to(workspace_root).as_posix())
    return status, wrote

