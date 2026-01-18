from __future__ import annotations

from typing import Any

from .textum_json_patch_utils import _container_for_next, _ensure_list_length, _expect_container
from .textum_json_path_parse import parse_json_path


def append_value(document: dict[str, Any], path: str, value: Any, *, create: bool = True) -> bool:
    tokens = parse_json_path(path)
    current: Any = document

    if not tokens:
        raise ValueError("cannot append to root '$' directly")

    for index, token in enumerate(tokens[:-1]):
        next_token = tokens[index + 1]
        if token[0] == "field":
            if not isinstance(current, dict):
                raise ValueError(f"expected object for '{token[1]}', got {type(current).__name__}")
            key = str(token[1])
            if key not in current or current[key] is None:
                if not create:
                    raise ValueError(f"missing field '{key}'")
                current[key] = _container_for_next(next_token)
            child = current[key]
            if child is None:
                if not create:
                    raise ValueError(f"missing field '{key}'")
                current[key] = _container_for_next(next_token)
                child = current[key]
            current = _expect_container(child, next_token)
            continue

        if not isinstance(current, list):
            raise ValueError(f"expected list for index [{token[1]}], got {type(current).__name__}")
        idx = int(token[1])
        if idx >= len(current):
            if not create:
                raise ValueError(f"index out of range: {idx}")
            _ensure_list_length(current, idx)
        if current[idx] is None:
            if not create:
                raise ValueError(f"missing list element at index {idx}")
            current[idx] = _container_for_next(next_token)
        current = _expect_container(current[idx], next_token)

    last = tokens[-1]
    if last[0] == "field":
        if not isinstance(current, dict):
            raise ValueError(f"expected object for '{last[1]}', got {type(current).__name__}")
        key = str(last[1])
        if key not in current or current[key] is None:
            if not create:
                raise ValueError(f"missing field '{key}'")
            current[key] = []
        target = current[key]
    else:
        if not isinstance(current, list):
            raise ValueError(f"expected list for index [{last[1]}], got {type(current).__name__}")
        idx = int(last[1])
        if idx >= len(current):
            if not create:
                raise ValueError(f"index out of range: {idx}")
            _ensure_list_length(current, idx)
        if current[idx] is None:
            if not create:
                raise ValueError(f"missing list element at index {idx}")
            current[idx] = []
        target = current[idx]

    if not isinstance(target, list):
        raise ValueError(f"expected list target, got {type(target).__name__}")
    target.append(value)
    return True

