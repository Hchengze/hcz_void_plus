"""Matplotlib 中文绘图样式。"""

from __future__ import annotations

import matplotlib
from matplotlib import font_manager


def setup_chinese_matplotlib() -> dict[str, object]:
    """尝试设置中文字体，并处理负号显示。

    物理和科研含义：
        Stage 2 的图件面向中文科研记录，因此标题、坐标轴、图例和色标默认使用
        中文。不同机器上的中文字体可能不同，本函数按常见字体顺序尝试，找不到
        时不让流程崩溃，而是返回 warning，由 pipeline 写入 metadata 或报告。

    输出：
        dict，包含 font_available、font_name 和 warning。
    """

    preferred_fonts = [
        "Microsoft YaHei",
        "SimHei",
        "Noto Sans CJK SC",
        "Source Han Sans SC",
        "WenQuanYi Micro Hei",
        "Arial Unicode MS",
    ]
    installed = {font.name for font in font_manager.fontManager.ttflist}
    selected = next((name for name in preferred_fonts if name in installed), None)

    matplotlib.rcParams["axes.unicode_minus"] = False
    if selected is not None:
        matplotlib.rcParams["font.sans-serif"] = [selected, "DejaVu Sans"]
        return {"font_available": True, "font_name": selected, "warning": None}

    matplotlib.rcParams["font.sans-serif"] = ["DejaVu Sans"]
    return {
        "font_available": False,
        "font_name": None,
        "warning": "未检测到常见中文字体，图件中的中文可能无法正常显示，但主流程不会中断。",
    }
