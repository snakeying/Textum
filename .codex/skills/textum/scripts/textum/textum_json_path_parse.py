from __future__ import annotations

from typing import Literal

JsonPathToken = tuple[Literal["field", "index"], str | int]


def parse_json_path(path: str) -> list[JsonPathToken]:
    if not path or not path.startswith("$"):
        raise ValueError("path must start with '$'")

    tokens: list[JsonPathToken] = []
    i = 1
    while i < len(path):
        char = path[i]
        if char == ".":
            i += 1
            if i >= len(path):
                raise ValueError("unexpected end of path after '.'")
            start = i
            while i < len(path) and path[i] not in ".[":
                i += 1
            field = path[start:i]
            if not field:
                raise ValueError("empty field name after '.'")
            tokens.append(("field", field))
            continue

        if char == "[":
            close = path.find("]", i + 1)
            if close == -1:
                raise ValueError("missing closing ']'")
            inner = path[i + 1 : close].strip()
            if not inner:
                raise ValueError("empty bracket selector")
            if inner[0] in ("'", '"'):
                quote = inner[0]
                if len(inner) < 2 or inner[-1] != quote:
                    raise ValueError("unterminated quoted key in brackets")
                tokens.append(("field", inner[1:-1]))
            else:
                try:
                    index = int(inner)
                except ValueError as exc:
                    raise ValueError(f"invalid list index: {inner}") from exc
                if index < 0:
                    raise ValueError("negative list indices are not supported")
                tokens.append(("index", index))
            i = close + 1
            continue

        raise ValueError(f"unexpected character '{char}' in path")

    return tokens

