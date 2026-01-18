from __future__ import annotations

import copy
from typing import Any

from textum.prd_render_i18n_labels_en import LABELS_EN
from textum.prd_render_i18n_labels_zh import LABELS_ZH


SUPPORTED_LANGS = ("zh", "en")


def resolve_render_lang(lang: str, prd_pack: dict[str, Any]) -> str:
    normalized = (lang or "").strip().lower()
    if normalized in ("auto", ""):
        return detect_pack_lang(prd_pack)
    if normalized not in SUPPORTED_LANGS:
        raise ValueError(f"unsupported lang: {lang!r} (expected: auto/zh/en)")
    return normalized


def detect_pack_lang(prd_pack: dict[str, Any]) -> str:
    strings: list[str] = []

    def walk(value: Any) -> None:
        if value is None:
            return
        if isinstance(value, str):
            strings.append(value)
            return
        if isinstance(value, dict):
            for k, v in value.items():
                if isinstance(k, str) and k.lower() == "id":
                    continue
                walk(v)
            return
        if isinstance(value, list):
            for item in value:
                walk(item)
            return

    walk(prd_pack)

    cjk = 0
    latin = 0
    for text in strings:
        for ch in text:
            code = ord(ch)
            if 0x4E00 <= code <= 0x9FFF or 0x3400 <= code <= 0x4DBF:
                cjk += 1
                continue
            if ("A" <= ch <= "Z") or ("a" <= ch <= "z"):
                latin += 1

    if cjk == 0 and latin == 0:
        return "zh"

    total = cjk + latin
    if cjk >= 50 and (cjk / total) >= 0.2:
        return "zh"
    return "en"


def prd_render_labels(lang: str) -> dict[str, Any]:
    if lang not in SUPPORTED_LANGS:
        raise ValueError(f"unsupported lang: {lang!r}")

    if lang == "zh":
        return copy.deepcopy(LABELS_ZH)

    return copy.deepcopy(LABELS_EN)
