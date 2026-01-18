from __future__ import annotations

from typing import Any

from .textum_json_path_parse import parse_json_path


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

