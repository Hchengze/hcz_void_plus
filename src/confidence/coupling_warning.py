"""单侧 DAS-like 几何下的 y-depth 耦合风险提示。"""

from __future__ import annotations

from types import SimpleNamespace
from typing import Any

import numpy as np


def analyze_y_depth_coupling(
    score_volume: np.ndarray,
    x_grid: np.ndarray,
    y_grid: np.ndarray,
    depth_grid: np.ndarray,
    best_index: tuple[int, int, int],
    params: SimpleNamespace,
) -> dict[str, Any]:
    """在 best_x 附近检查 y-depth 高分区是否拉长。

    物理意义：
        单侧 DAS-like 几何中，接收线和震源线都在地表道路两侧，候选点的 y 坐标和
        埋深 h 可能产生相似的走时变化。若 best_x 切片上的高分区同时沿 y 和 depth
        展开，说明定位结果可能不是一个孤立尖峰，而是一条耦合高分带。

    判别方法：
        取 ix=best_ix 的 y-depth 切片，统计得分 >= threshold_ratio * best_score
        的候选点集合，计算其 y 方向跨度和 depth 方向跨度。两个跨度同时超过阈值时
        触发 warning。

    限制：
        这是 Stage 3 的规则型诊断，不是完整不确定性反演或置信区间估计。
    """

    if score_volume.ndim != 3:
        raise ValueError(f"score_volume 维度错误：当前 shape={score_volume.shape}，应为 n_x × n_y × n_depth。")
    ix = best_index[0]
    best_score = float(score_volume[best_index])
    threshold = params.confidence.threshold_ratio * best_score
    yd_slice = score_volume[ix, :, :]
    high_mask = yd_slice >= threshold
    high_count = int(np.count_nonzero(high_mask))

    if high_count == 0:
        y_span_m = 0.0
        depth_span_m = 0.0
        high_y_values = np.array([], dtype=float)
        high_depth_values = np.array([], dtype=float)
    else:
        iy, iz = np.where(high_mask)
        high_y_values = y_grid[iy]
        high_depth_values = depth_grid[iz]
        y_span_m = float(np.max(high_y_values) - np.min(high_y_values))
        depth_span_m = float(np.max(high_depth_values) - np.min(high_depth_values))

    warning = (
        y_span_m >= params.confidence.coupling_warning_span_y_m
        and depth_span_m >= params.confidence.coupling_warning_span_depth_m
    )
    message = (
        "y-depth 高分区同时沿横向和深度方向展开，单侧 DAS-like 几何耦合风险较高。"
        if warning
        else "当前 best_x 切片未触发 y-depth 耦合跨度阈值，但仍需结合图件人工检查。"
    )
    return {
        "best_x_m": float(x_grid[ix]),
        "threshold": float(threshold),
        "threshold_ratio": params.confidence.threshold_ratio,
        "high_score_point_count": high_count,
        "y_span_m": y_span_m,
        "depth_span_m": depth_span_m,
        "warning": bool(warning),
        "message": message,
        "span_y_threshold_m": params.confidence.coupling_warning_span_y_m,
        "span_depth_threshold_m": params.confidence.coupling_warning_span_depth_m,
    }


def assign_confidence_flag(
    peak_sharpness: float,
    score_contrast: float,
    consistency_cv: float,
    consistency_warning: bool,
    coupling_warning: bool,
    params: SimpleNamespace,
) -> str:
    """根据规则输出 high / medium / low 三档基础置信度标志。

    这里的 flag 是科研原型阶段的诊断标签，不是概率意义置信度。规则刻意保守：
    若峰值不尖锐、整体对比度低、多炮一致性差或 y-depth 耦合风险明显，则下调等级。
    """

    if coupling_warning or consistency_warning or peak_sharpness < 1.2 or score_contrast < 1.5:
        return "low"
    if (
        peak_sharpness < 2.0
        or score_contrast < 2.0
        or consistency_cv > 0.5 * params.confidence.consistency_warning_cv_threshold
    ):
        return "medium"
    return "high"

