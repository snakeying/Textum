from __future__ import annotations

from typing import Any

from textum_json_path_parse import JsonPathToken, parse_json_path


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


def set_value(document: dict[str, Any], path: str, value: Any, *, create: bool = True) -> bool:
    tokens = parse_json_path(path)
    if not tokens:
        raise ValueError("cannot set root '$' directly")

    current: Any = document
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

    last_token = tokens[-1]
    if last_token[0] == "field":
        if not isinstance(current, dict):
            raise ValueError(f"expected object for '{last_token[1]}', got {type(current).__name__}")
        key = str(last_token[1])
        changed = current.get(key) != value
        current[key] = value
        return changed

    if not isinstance(current, list):
        raise ValueError(f"expected list for index [{last_token[1]}], got {type(current).__name__}")
    idx = int(last_token[1])
    if idx >= len(current):
        if not create:
            raise ValueError(f"index out of range: {idx}")
        _ensure_list_length(current, idx)
    changed = current[idx] != value
    current[idx] = value
    return changed


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


def delete_value(document: dict[str, Any], path: str, *, missing_ok: bool = False) -> bool:
    tokens = parse_json_path(path)
    if not tokens:
        raise ValueError("cannot delete root '$' directly")

    current: Any = document
    for token in tokens[:-1]:
        if token[0] == "field":
            if not isinstance(current, dict):
                raise ValueError(f"expected object for '{token[1]}', got {type(current).__name__}")
            key = str(token[1])
            if key not in current or current[key] is None:
                if missing_ok:
                    return False
                raise ValueError(f"missing field '{key}'")
            current = current[key]
            continue

        if not isinstance(current, list):
            raise ValueError(f"expected list for index [{token[1]}], got {type(current).__name__}")
        idx = int(token[1])
        if idx < 0 or idx >= len(current) or current[idx] is None:
            if missing_ok:
                return False
            raise ValueError(f"index out of range: {idx}")
        current = current[idx]

    last = tokens[-1]
    if last[0] == "field":
        if not isinstance(current, dict):
            raise ValueError(f"expected object for '{last[1]}', got {type(current).__name__}")
        key = str(last[1])
        if key not in current:
            if missing_ok:
                return False
            raise ValueError(f"missing field '{key}'")
        del current[key]
        return True

    if not isinstance(current, list):
        raise ValueError(f"expected list for index [{last[1]}], got {type(current).__name__}")
    idx = int(last[1])
    if idx < 0 or idx >= len(current):
        if missing_ok:
            return False
        raise ValueError(f"index out of range: {idx}")
    current.pop(idx)
    return True

