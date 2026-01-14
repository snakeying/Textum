from __future__ import annotations

from typing import Any

from prd_pack_types import Failure, LANDING_PREFIXES, TBL_ID_RE


def _get_dict(value: Any, loc: str, failures: list[Failure]) -> dict[str, Any] | None:
    if isinstance(value, dict):
        return value
    failures.append(
        Failure(
            loc=loc,
            problem=f"expected object, got {type(value).__name__}",
            expected="object",
            impact="cannot validate PRD pack",
            fix=f"rewrite {loc} as an object",
        )
    )
    return None


def _get_list(value: Any, loc: str, failures: list[Failure]) -> list[Any] | None:
    if isinstance(value, list):
        return value
    failures.append(
        Failure(
            loc=loc,
            problem=f"expected array, got {type(value).__name__}",
            expected="array",
            impact="cannot validate PRD pack",
            fix=f"rewrite {loc} as an array",
        )
    )
    return None


def _require_str(value: Any, loc: str, failures: list[Failure], *, allow_na: bool = False) -> None:
    if not isinstance(value, str):
        failures.append(
            Failure(
                loc=loc,
                problem=f"expected string, got {type(value).__name__}",
                expected="non-empty string",
                impact="PRD content is missing or invalid",
                fix=f"set {loc} to a non-empty string",
            )
        )
        return
    if value.strip() == "":
        failures.append(
            Failure(
                loc=loc,
                problem="empty string",
                expected="non-empty string",
                impact="PRD content is missing",
                fix=f"fill {loc}",
            )
        )
        return
    if not allow_na and value.strip().upper() == "N/A":
        failures.append(
            Failure(
                loc=loc,
                problem="N/A not allowed here",
                expected="a concrete value",
                impact="PRD becomes ambiguous",
                fix=f"replace N/A at {loc}",
            )
        )


def _build_table_index(data_model: dict[str, Any], failures: list[Failure]) -> dict[str, str]:
    table_index: dict[str, str] = {}
    tables = _get_list(data_model.get("tables"), "$.data_model.tables", failures)
    if tables is None:
        return {}
    for index, table in enumerate(tables):
        table_loc = f"$.data_model.tables[{index}]"
        table_obj = _get_dict(table, table_loc, failures)
        if table_obj is None:
            continue
        name = table_obj.get("name")
        if not isinstance(name, str) or name.strip() == "":
            failures.append(
                Failure(
                    loc=f"{table_loc}.name",
                    problem="missing table name",
                    expected="non-empty string",
                    impact="cannot resolve DB:<table_name>",
                    fix=f"fill {table_loc}.name",
                )
            )
            continue
        if name in table_index:
            failures.append(
                Failure(
                    loc=f"{table_loc}.name",
                    problem=f"duplicate table name: {name}",
                    expected="unique table names",
                    impact="DB:<table_name> becomes ambiguous",
                    fix="deduplicate data_model.tables[].name",
                )
            )
            continue
        table_id = table_obj.get("id")
        table_index[name] = table_id if isinstance(table_id, str) else ""
    return table_index


def _validate_landing_tokens(
    tokens: list[Any], loc: str, failures: list[Failure], table_index: dict[str, str]
) -> None:
    if not tokens:
        failures.append(
            Failure(
                loc=loc,
                problem="landing is empty",
                expected="at least 1 landing token or N/A",
                impact="cannot close FP → landing mapping",
                fix=f"add landing tokens under {loc}",
            )
        )
        return
    for index, token in enumerate(tokens):
        token_loc = f"{loc}[{index}]"
        if not isinstance(token, str):
            failures.append(
                Failure(
                    loc=token_loc,
                    problem=f"landing token must be string, got {type(token).__name__}",
                    expected="string token",
                    impact="mapping is invalid",
                    fix=f"rewrite {token_loc} as a string",
                )
            )
            continue
        stripped = token.strip()
        if stripped == "":
            failures.append(
                Failure(
                    loc=token_loc,
                    problem="landing token is empty",
                    expected="non-empty token",
                    impact="mapping is invalid",
                    fix=f"fill {token_loc}",
                )
            )
            continue
        if stripped.upper() == "N/A":
            continue
        if not stripped.startswith(LANDING_PREFIXES):
            failures.append(
                Failure(
                    loc=token_loc,
                    problem=f"invalid landing prefix: {token}",
                    expected="DB:/FILE:/CFG:/EXT: or N/A",
                    impact="mapping is invalid",
                    fix=f"rewrite {token_loc} with a valid prefix",
                )
            )
            continue
        if not stripped.startswith("DB:"):
            continue
        table_ref = stripped.removeprefix("DB:").strip()
        if table_ref == "":
            failures.append(
                Failure(
                    loc=token_loc,
                    problem="DB: token missing table reference",
                    expected="DB:<table_name> or DB:TBL-###",
                    impact="cannot resolve table",
                    fix=f"set {token_loc} to DB:<table_name>",
                )
            )
            continue
        if TBL_ID_RE.match(table_ref):
            if table_ref not in table_index.values():
                failures.append(
                    Failure(
                        loc=token_loc,
                        problem=f"table id not found: {table_ref}",
                        expected="DB:TBL-### must exist in data_model.tables[].id",
                        impact="cannot resolve table",
                        fix=f"add data_model.tables[] entry with id={table_ref}",
                    )
                )
            continue
        if table_ref not in table_index:
            failures.append(
                Failure(
                    loc=token_loc,
                    problem=f"table not found: {table_ref}",
                    expected="every DB:<table_name> must exist in data_model.tables[].name",
                    impact="cannot resolve table",
                    fix=f"add data_model.tables[] entry with name={table_ref}",
                )
            )
