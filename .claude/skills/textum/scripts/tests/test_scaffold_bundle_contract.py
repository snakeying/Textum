from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

from textum.textum_cli import main as textum_main


def _run_textum(argv: list[str]) -> tuple[int, str, str]:
    stdout = io.StringIO()
    stderr = io.StringIO()
    with redirect_stdout(stdout), redirect_stderr(stderr):
        code = textum_main(argv)
    return code, stdout.getvalue().replace("\r\n", "\n"), stderr.getvalue().replace("\r\n", "\n")


def _write_json(path: Path, obj: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _minimal_valid_prd_pack() -> dict:
    return {
        "schema_version": "prd-pack@v1",
        "project": {"name": "TestApp", "one_liner": "PRD pack for scaffold contract tests."},
        "goals": ["Ship a minimal end-to-end flow."],
        "non_goals": ["No integrations."],
        "scope": {"in": ["Core flow"], "out": ["Nice-to-have extras"]},
        "assumptions_constraints": [],
        "roles": [{"role": "user", "description": "Primary user", "typical_scenarios": ["Use the app"]}],
        "permission_matrix": {"legend": "A=Allow, D=Deny, O=Own", "operations": [{"op": "all", "per_role": {"user": "A"}, "note": None}]},
        "modules": [
            {
                "id": None,
                "name": "Core",
                "summary": "Core module",
                "priority": "P0",
                "dependencies": [],
                "feature_points": [{"id": None, "desc": "Do the thing", "landing": ["FILE:app/core.py"]}],
                "scenarios": [{"id": None, "actor": "user", "given": "given", "when": "when", "then": "then"}],
            }
        ],
        "ui_routes": [],
        "business_rules": [{"id": None, "desc": "User actions are local.", "scope": "global", "exception_or_note": None}],
        "states_enums": {"enums": [], "state_machines": [], "naming_conventions": None},
        "data_model": {"tables": [], "relations": None},
        "api": {"has_api": False, "base_url": None, "auth": None, "pagination_sort_filter": None, "response_wrapper": None, "extra_error_codes": [], "endpoints": []},
        "nfr": [],
    }


def _minimal_scaffold_pack_decisions_only() -> dict:
    return {
        "schema_version": "scaffold-pack@v1",
        "source": None,
        "decisions": {
            "tech_stack": {"backend": "Python (FastAPI)", "frontend": "CLI (no UI)", "database": "SQLite", "other": []},
            "repo_structure": [{"path": "app/", "purpose": "Application code"}],
            "validation_commands": [{"type": "N/A", "command": "N/A", "note": "N/A"}],
            "coding_conventions": None,
        },
        "extracted": None,
    }


class TestScaffoldBundleContract(unittest.TestCase):
    def test_scaffold_render_missing_prd_routes_to_prd_plan(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp)

            code, out, err = _run_textum(["scaffold", "render", "--workspace", str(workspace)])
            self.assertEqual(code, 1, msg=err)
            self.assertEqual(out.strip().split("\n")[-1], "next: PRD Plan", msg=out)

    def test_scaffold_check_fail_prints_fix_list(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            _write_json(workspace / "docs" / "prd-pack.json", _minimal_valid_prd_pack())

            code, out, err = _run_textum(["scaffold", "init", "--workspace", str(workspace)])
            self.assertEqual(code, 0, msg=err)

            code, out, err = _run_textum(["scaffold", "check", "--workspace", str(workspace)])
            self.assertEqual(code, 1, msg=err)

            lines = [line for line in out.strip().split("\n") if line.strip()]
            self.assertGreaterEqual(len(lines), 3, msg=out)
            self.assertEqual(lines[0], "FAIL", msg=out)
            self.assertTrue(any(line.startswith("- [FAIL]; loc=") for line in lines), msg=out)
            self.assertEqual(lines[-1], "next: Scaffold Plan", msg=out)

    def test_scaffold_check_render_pass_flow(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            _write_json(workspace / "docs" / "prd-pack.json", _minimal_valid_prd_pack())
            _write_json(workspace / "docs" / "scaffold-pack.json", _minimal_scaffold_pack_decisions_only())

            code, out, err = _run_textum(["scaffold", "check", "--workspace", str(workspace)])
            self.assertEqual(code, 0, msg=err)
            self.assertEqual(out.strip().split("\n")[-1], "next: Scaffold Render", msg=out)

            code, out, err = _run_textum(["scaffold", "render", "--workspace", str(workspace)])
            self.assertEqual(code, 0, msg=err)
            self.assertEqual(out.strip().split("\n")[-1], "next: Split Plan", msg=out)
            self.assertTrue((workspace / "docs" / "GLOBAL-CONTEXT.md").exists())

