"""基础置信度诊断图件。"""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from src.visualization.plot_style import setup_chinese_matplotlib


def plot_confidence_diagnostics(
    params: SimpleNamespace,
    scan_result: dict[str, Any],
    confidence_metrics: dict[str, Any],
    output_path: Path,
) -> None:
    """绘制 Stage 3 基础置信度诊断图。

    图件内容：
        左侧显示 best_x 处的 y-depth 得分切片，用于观察高分区是否呈横向-深度
        拉长带；右侧显示 peak sharpness、score contrast、多炮 CV 和综合 flag。

    限制：
        该图只服务于科研原型阶段的人工检查，不是完整不确定性成像，也不是工程确诊。
    """

    setup_chinese_matplotlib()
    score_volume = scan_result["normalized_score_volume"]
    best_index = tuple(int(v) for v in scan_result["best_index"])
    y_grid = params.derived.scan_y_grid
    depth_grid = params.derived.scan_depth_grid
    yd_slice = score_volume[best_index[0], :, :].T

    fig, (ax_map, ax_text) = plt.subplots(
        1,
        2,
        figsize=(10.5, 4.8),
        dpi=150,
        gridspec_kw={"width_ratios": [1.35, 1.0]},
    )
    image = ax_map.imshow(
        yd_slice,
        extent=[y_grid[0], y_grid[-1], depth_grid[-1], depth_grid[0]],
        aspect="auto",
        cmap="magma",
        vmin=0.0,
        vmax=1.0,
    )
    best = scan_result["best_location"]
    ax_map.scatter([params.anomaly.y0_m], [params.anomaly.depth_m], marker="x", s=65, color="cyan", label="真实异常体")
    ax_map.scatter([best["y_m"]], [best["depth_m"]], marker="o", s=52, facecolors="none", edgecolors="white", label="扫描最佳位置")
    ax_map.set_xlabel("横穿道路方向 y / m")
    ax_map.set_ylabel("埋深 h / m")
    ax_map.set_title("best_x 处 y-depth 高分区检查")
    ax_map.legend(loc="best", fontsize=8)
    fig.colorbar(image, ax=ax_map, label="归一化扫描得分")

    peak = confidence_metrics["peak"]
    contrast = confidence_metrics["contrast"]
    consistency = confidence_metrics["multi_shot_consistency"]
    coupling = confidence_metrics["y_depth_coupling"]
    stage3b = confidence_metrics["stage3b_warnings"]
    diff = confidence_metrics.get("raw_weighted_difference") or {}
    lines = [
        "基础置信度诊断",
        "",
        f"peak sharpness: {peak['peak_sharpness']:.3g}",
        f"score contrast: {contrast['score_contrast']:.3g}",
        f"score percentile: {contrast['score_percentile']:.2f}%",
        f"multi-shot CV: {consistency['coefficient_of_variation']:.3g}",
        f"高分 y 跨度: {coupling['y_span_m']:.3g} m",
        f"高分 depth 跨度: {coupling['depth_span_m']:.3g} m",
        f"y-depth 耦合警告: {coupling['warning']}",
        f"深度边界警告: {stage3b['best_depth_at_boundary_warning']}",
        f"宽 y 高分区警告: {stage3b['wide_y_high_score_zone_warning']}",
        f"raw/weighted 分歧: {stage3b['raw_weighted_divergence_warning']}",
        f"浅部偏置警告: {stage3b['shallow_bias_warning']}",
        f"raw->weighted dh: {diff.get('ddepth_m', 0.0):.3g} m",
        f"confidence flag: {confidence_metrics['low_confidence_flag']}",
        "",
        "说明：规则型科研诊断，非工程确诊。",
    ]
    ax_text.axis("off")
    ax_text.text(
        0.0,
        1.0,
        "\n".join(lines),
        va="top",
        ha="left",
        fontsize=10,
        linespacing=1.45,
    )
    fig.suptitle("基础置信度诊断图：峰值集中性、多炮一致性与 y-depth 耦合风险", fontsize=12)
    fig.tight_layout()
    fig.savefig(output_path)
    plt.close(fig)
