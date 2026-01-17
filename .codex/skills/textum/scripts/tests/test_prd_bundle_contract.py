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


def _write_prd_pack(workspace: Path, prd_pack: dict) -> None:
    docs_dir = workspace / "docs"
    docs_dir.mkdir(parents=True, exist_ok=True)
    (docs_dir / "prd-pack.json").write_text(json.dumps(prd_pack, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _minimal_valid_prd_pack() -> dict:
    return {
        "schema_version": "prd-pack@v1",
        "project": {"name": "TestApp", "one_liner": "A minimal PRD pack for CLI contract tests."},
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
        "business_rules": [{"id": None, "desc": "User actions are scoped to the local workspace.", "scope": "global", "exception_or_note": None}],
        "states_enums": {"enums": [], "state_machines": [], "naming_conventions": None},
        "data_model": {"tables": [], "relations": None},
        "api": {"has_api": False, "base_url": None, "auth": None, "pagination_sort_filter": None, "response_wrapper": None, "extra_error_codes": [], "endpoints": []},
        "nfr": [],
    }


class TestPrdBundleContract(unittest.TestCase):
    def test_prd_patch_missing_pack_prints_fix_list(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp)

            code, out, err = _run_textum(
                [
                    "prd",
                    "patch",
                    "set",
                    "--workspace",
                    str(workspace),
                    "--path",
                    "$.project.name",
                    "--value",
                    "TestApp",
                ]
            )
            self.assertEqual(code, 1, msg=err)

            lines = [line for line in out.strip().split("\n") if line.strip()]
            self.assertGreaterEqual(len(lines), 3, msg=out)
            self.assertEqual(lines[0], "FAIL", msg=out)
            self.assertTrue(any(line.startswith("- [FAIL]; loc=") for line in lines), msg=out)
            self.assertEqual(lines[-1], "next: PRD Plan", msg=out)

    def test_prd_check_fail_prints_fix_list(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp)

            code, out, err = _run_textum(["prd", "init", "--workspace", str(workspace)])
            self.assertEqual(code, 0, msg=err)

            code, out, err = _run_textum(["prd", "check", "--workspace", str(workspace)])
            self.assertEqual(code, 1, msg=err)

            lines = [line for line in out.strip().split("\n") if line.strip()]
            self.assertGreaterEqual(len(lines), 3, msg=out)
            self.assertEqual(lines[0], "FAIL", msg=out)
            self.assertTrue(any(line.startswith("- [FAIL]; loc=") for line in lines), msg=out)
            self.assertTrue(lines[-1].startswith("next: "), msg=out)

    def test_prd_check_render_slice_pass_flow(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            _write_prd_pack(workspace, _minimal_valid_prd_pack())

            code, out, err = _run_textum(["prd", "check", "--workspace", str(workspace)])
            self.assertEqual(code, 0, msg=err)
            self.assertEqual(out.strip().split("\n")[-1], "next: PRD Render", msg=out)

            code, out, err = _run_textum(["prd", "render", "--workspace", str(workspace), "--lang", "en"])
            self.assertEqual(code, 0, msg=err)
            self.assertEqual(out.strip().split("\n")[-1], "next: PRD Slice", msg=out)
            self.assertTrue((workspace / "docs" / "PRD.md").exists())

            code, out, err = _run_textum(["prd", "slice", "--workspace", str(workspace)])
            self.assertEqual(code, 0, msg=err)
            self.assertEqual(out.strip().split("\n")[-1], "next: Scaffold Plan", msg=out)
            self.assertTrue((workspace / "docs" / "prd-slices" / "index.json").exists())

