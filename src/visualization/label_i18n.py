"""Stage 5H 图件标签中文化工具。

本模块只负责把内部稳定 key 转换成中文展示标签。算法和 metadata 仍保留英文 key，
便于测试、复现实验和后续脚本引用；进入 latest_stable 的标题、坐标轴、图例和 case
label 则尽量使用中文，避免人工复查时把内部枚举误认为科研结论。
"""

from __future__ import annotations

from collections.abc import Iterable


CASE_LABEL_ZH: dict[str, str] = {
    "collocated_vertical": "共点网格-垂向力源",
    "collocated_horizontal": "共点网格-水平力源",
    "staggered_vertical": "错格网格-垂向力源",
    "staggered_horizontal": "错格网格-水平力源",
    "staggered_traction_variant": "错格网格-自由面变体",
    "sponge_weak": "弱海绵边界",
    "sponge_medium": "中等海绵边界",
    "sponge_strong": "强海绵边界",
    "stress_zero_variant": "应力置零自由面",
    "horizontal_force": "水平力源",
    "vertical_force": "垂向力源",
    "explosive": "爆炸源近似",
    "collocated": "共点网格",
    "staggered": "错格网格",
    "approximate": "近似自由面",
    "stress_zero": "应力置零",
    "traction_free": "近似零牵引",
    "medium": "中等",
    "weak": "弱",
    "strong": "强",
}

ALLOWED_LATIN_TERMS = {
    "DAS",
    "Rayleigh",
    "Vp",
    "Vs",
    "CFL",
    "PML",
    "RMS",
    "x",
    "y",
    "z",
    "gauge length",
}


def zh_label(value: object) -> str:
    """把内部 key 转为中文标签；未知 key 保留原文以便暴露缺口。

    保留未知 key 是有意设计：如果新 case 没有登记中文映射，label audit 会把它列入
    warning，促使开发者补齐，而不是悄悄生成一张全英文图。
    """

    text = str(value)
    return CASE_LABEL_ZH.get(text, text)


def zh_labels(values: Iterable[object]) -> list[str]:
    """批量转换 case labels。"""

    return [zh_label(value) for value in values]


def find_untranslated_case_labels(values: Iterable[object]) -> list[str]:
    """返回仍未中文化的 case label key。"""

    missing: list[str] = []
    for value in values:
        text = str(value)
        if text not in CASE_LABEL_ZH:
            missing.append(text)
    return missing
