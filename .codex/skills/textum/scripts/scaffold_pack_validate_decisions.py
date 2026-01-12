from __future__ import annotations

from typing import Any

from prd_pack_types import Failure
from scaffold_pack_validate_utils import require_str


def validate_decisions(decisions: dict[str, Any], failures: list[Failure]) -> None:
    tech_stack = decisions.get("tech_stack")
    if not isinstance(tech_stack, dict):
        failures.append(
            Failure(
                loc="$.decisions.tech_stack",
                problem=f"expected object, got {type(tech_stack).__name__}",
                expected="object",
                impact="tech stack is missing",
                fix="set decisions.tech_stack to an object",
            )
        )
    else:
        require_str(tech_stack.get("backend"), "$.decisions.tech_stack.backend", failures, allow_na=False)
        require_str(tech_stack.get("frontend"), "$.decisions.tech_stack.frontend", failures, allow_na=False)
        require_str(tech_stack.get("database"), "$.decisions.tech_stack.database", failures, allow_na=False)

        other = tech_stack.get("other")
        if other is not None and not isinstance(other, list):
            failures.append(
                Failure(
                    loc="$.decisions.tech_stack.other",
                    problem=f"expected array, got {type(other).__name__}",
                    expected="array of strings",
                    impact="tech stack.other is invalid",
                    fix="rewrite decisions.tech_stack.other as an array",
                )
            )

    repo_structure = decisions.get("repo_structure")
    if not isinstance(repo_structure, list):
        failures.append(
            Failure(
                loc="$.decisions.repo_structure",
                problem=f"expected array, got {type(repo_structure).__name__}",
                expected="array of {path,purpose}",
                impact="repo structure is missing",
                fix="set decisions.repo_structure to an array",
            )
        )
    else:
        if len(repo_structure) == 0:
            failures.append(
                Failure(
                    loc="$.decisions.repo_structure",
                    problem="repo_structure is empty",
                    expected="at least 1 path mapping",
                    impact="cannot establish project layout",
                    fix="add at least one item to decisions.repo_structure[]",
                )
            )
        for index, item in enumerate(repo_structure):
            loc = f"$.decisions.repo_structure[{index}]"
            if not isinstance(item, dict):
                failures.append(
                    Failure(
                        loc=loc,
                        problem=f"expected object, got {type(item).__name__}",
                        expected="{path,purpose}",
                        impact="repo structure row is invalid",
                        fix=f"rewrite {loc} as an object with path and purpose",
                    )
                )
                continue
            require_str(item.get("path"), f"{loc}.path", failures, allow_na=False)
            require_str(item.get("purpose"), f"{loc}.purpose", failures, allow_na=False)

    validation_commands = decisions.get("validation_commands")
    if not isinstance(validation_commands, list):
        failures.append(
            Failure(
                loc="$.decisions.validation_commands",
                problem=f"expected array, got {type(validation_commands).__name__}",
                expected="array of {type,command,note}",
                impact="verification commands are missing",
                fix="set decisions.validation_commands to an array",
            )
        )
    else:
        if len(validation_commands) == 0:
            failures.append(
                Failure(
                    loc="$.decisions.validation_commands",
                    problem="validation_commands is empty",
                    expected="at least 1 row or a single N/A row",
                    impact="cannot define gates for next bundles",
                    fix="add one row to decisions.validation_commands[]",
                )
            )
        for index, item in enumerate(validation_commands):
            loc = f"$.decisions.validation_commands[{index}]"
            if not isinstance(item, dict):
                failures.append(
                    Failure(
                        loc=loc,
                        problem=f"expected object, got {type(item).__name__}",
                        expected="{type,command,note}",
                        impact="validation command row is invalid",
                        fix=f"rewrite {loc} as an object with type/command/note",
                    )
                )
                continue

            typ = require_str(item.get("type"), f"{loc}.type", failures, allow_na=True)
            cmd = require_str(item.get("command"), f"{loc}.command", failures, allow_na=True)
            note = require_str(item.get("note"), f"{loc}.note", failures, allow_na=True)
            if typ is None or cmd is None or note is None:
                continue

            any_na = any(x.upper() == "N/A" for x in (typ, cmd, note))
            all_na = all(x.upper() == "N/A" for x in (typ, cmd, note))
            if any_na and not all_na:
                failures.append(
                    Failure(
                        loc=loc,
                        problem="partial N/A row",
                        expected="either all fields are N/A, or none are N/A",
                        impact="validation command row is ambiguous",
                        fix=f"make {loc} fully N/A or fully concrete",
                    )
                )
                continue

            if all_na:
                continue

            if not (typ.startswith("gate:") or typ.startswith("opt:")):
                failures.append(
                    Failure(
                        loc=f"{loc}.type",
                        problem=f"invalid type: {typ!r}",
                        expected="type starts with gate: or opt:",
                        impact="cannot classify the command",
                        fix=f"set {loc}.type to gate:<name> or opt:<name>",
                    )
                )

    coding_conventions = decisions.get("coding_conventions")
    if coding_conventions is not None and not isinstance(coding_conventions, str):
        failures.append(
            Failure(
                loc="$.decisions.coding_conventions",
                problem=f"expected string or null, got {type(coding_conventions).__name__}",
                expected="string or null",
                impact="coding_conventions is invalid",
                fix="set decisions.coding_conventions to a string or null",
            )
        )

