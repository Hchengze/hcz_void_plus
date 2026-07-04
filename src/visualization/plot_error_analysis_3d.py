"""Stage 5G 三维主线误差分析图。

这里的图用于解释三维定位结果和当前 validation 限制之间的关系。它们不把 2D elastic
结果直接迁移成三维结论，只帮助人工复查 ready_for_2p5d、DAS gauge 与模型错配风险。
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from src.visualization.plot_elastic2d import plot_rayleigh_pick_interpretation, plot_stage5g_status_badge
from src.visualization.plot_style import setup_chinese_matplotlib


def plot_model_mismatch_error_summary_3d(result: dict[str, Any], output_path: Path) -> None:
    """绘制面向三维定位解释的模型错配误差摘要。

    该函数是轻量接口，供测试和后续三维化复用；full_pipeline 当前仍复用 Stage 5A
    的模型错配实验结果。
    """

    setup_chinese_matplotlib()
    cases = result.get("cases", {})
    names = list(cases.keys()) or ["layered"]
    errors = []
    for name in names:
        item = cases.get(name, {})
        error = item.get("truth_error_distance_m") or item.get("distance_m") or item.get("error_m") or 0.0
        errors.append(float(error))
    fig, ax = plt.subplots(figsize=(7.0, 4.2), dpi=150)
    ax.bar(np.arange(len(names)), errors, color="#4e79a7")
    ax.set_xticks(np.arange(len(names)))
    ax.set_xticklabels(names, rotation=25, ha="right", fontsize=8)
    ax.set_ylabel("定位误差 / m")
    ax.set_title("三维定位模型错配误差摘要")
    ax.text(
        0.02,
        0.95,
        "当前速度为分层 Rayleigh 等效速度；不是完整 Vp/Vs/rho 弹性反演。",
        transform=ax.transAxes,
        va="top",
        fontsize=9,
        bbox={"facecolor": "white", "alpha": 0.78, "edgecolor": "0.8"},
    )
    ax.grid(axis="y", alpha=0.25)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(output_path)
    plt.close(fig)


__all__ = [
    "plot_model_mismatch_error_summary_3d",
    "plot_rayleigh_pick_interpretation",
    "plot_stage5g_status_badge",
]
