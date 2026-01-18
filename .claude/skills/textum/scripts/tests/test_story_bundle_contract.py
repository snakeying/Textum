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
        "project": {"name": "TestApp", "one_liner": "PRD pack for story contract tests."},
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


def _minimal_split_plan_pack() -> dict:
    return {
        "schema_version": "split-plan-pack@v1",
        "source": {"prd_pack_path": "docs/prd-pack.json", "scaffold_pack_path": "docs/scaffold-pack.json"},
        "stories": [
            {
                "story": "Story 1",
                "n": 1,
                "slug": "core-flow",
                "modules": ["M-01"],
                "goal": "Implement core flow",
                "prereq_stories": [],
            }
        ],
        "api_assignments": [],
    }


class TestStoryBundleContract(unittest.TestCase):
    def test_story_check_and_pack_pass_flow(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            _write_json(workspace / "docs" / "prd-pack.json", _minimal_valid_prd_pack())
            _write_json(workspace / "docs" / "scaffold-pack.json", _minimal_scaffold_pack_decisions_only())
            _write_json(workspace / "docs" / "split-plan-pack.json", _minimal_split_plan_pack())

            code, out, err = _run_textum(["split", "plan", "check", "--workspace", str(workspace)])
            self.assertEqual(code, 0, msg=err)

            code, out, err = _run_textum(["split", "generate", "--workspace", str(workspace)])
            self.assertEqual(code, 0, msg=err)

            code, out, err = _run_textum(["story", "check", "--workspace", str(workspace), "--n", "1"])
            self.assertEqual(code, 0, msg=err)
            self.assertEqual(out.strip().split("\n")[-1], "next: Story Pack", msg=out)

            code, out, err = _run_textum(["story", "pack", "--workspace", str(workspace), "--n", "1"])
            self.assertEqual(code, 0, msg=err)
            self.assertEqual(out.strip().split("\n")[-1], "next: Story Exec", msg=out)
            self.assertTrue((workspace / "docs" / "story-exec").exists())

