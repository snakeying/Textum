from __future__ import annotations

from typing import Any

from .textum_json_path_parse import JsonPathToken


def _container_for_next(next_token: JsonPathToken) -> Any:
    return {} if next_token[0] == "field" else []


def _ensure_list_length(items: list[Any], index: int) -> None:
    while len(items) <= index:
        items.append(None)


def _expect_container(value: Any, next_token: JsonPathToken) -> Any:
    if next_token[0] == "field":
        if not isinstance(value, dict):
            raise ValueError(f"expected object, got {type(value).__name__}")
        return value
    if not isinstance(value, list):
        raise ValueError(f"expected list, got {type(value).__name__}")
    return value

