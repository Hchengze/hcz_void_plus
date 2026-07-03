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


def analyze_stage3b_scan_warnings(
    score_volume: np.ndarray,
    y_grid: np.ndarray,
    depth_grid: np.ndarray,
    best_index: tuple[int, int, int],
    scan_result: dict[str, Any],
    params: SimpleNamespace,
) -> dict[str, Any]:
    """汇总 Stage 3B 新增的扫描可靠性 warning。

    诊断内容：
        1. best_depth 是否贴在扫描深度边界；
        2. best_x 切片上高分区的 y 跨度是否过宽；
        3. raw_best 与 weighted_best 是否明显分歧；
        4. depth weighting 是否把 best 明显推向浅部。

    这些 warning 直接针对本轮审核发现的问题：Rayleigh depth weighting 可能把深度
    先验过强地注入扫描结果，使最高点贴近 scan_depth_min。它们不是完整置信度体系，
    但会让报告和 latest_stable 明确提示“不能把当前 best 当成可靠深度”。
    """

    best_depth = scan_result["best_location"]["depth_m"]
    tol = 1.0e-9
    at_min = abs(best_depth - float(depth_grid[0])) <= tol
    at_max = abs(best_depth - float(depth_grid[-1])) <= tol
    boundary_warning = bool(at_min or at_max)

    ix = best_index[0]
    threshold = params.confidence.threshold_ratio * float(score_volume[best_index])
    yd_slice = score_volume[ix, :, :]
    high_mask = yd_slice >= threshold
    if np.any(high_mask):
        iy, _ = np.where(high_mask)
        high_y_values = y_grid[iy]
        y_span_m = float(np.max(high_y_values) - np.min(high_y_values))
    else:
        y_span_m = 0.0
    wide_y_warning = y_span_m >= params.confidence.coupling_warning_span_y_m

    diff = scan_result.get("raw_weighted_difference", {})
    depth_diff = float(diff.get("ddepth_m", 0.0))
    distance_diff = float(diff.get("distance_m", 0.0))
    raw_weighted_divergence_warning = distance_diff >= params.confidence.raw_weighted_location_diff_warning_m
    shallow_bias_warning = depth_diff <= -params.confidence.raw_weighted_depth_diff_warning_m
    depth_prior_bias_warning = bool(scan_result.get("depth_prior_bias_warning", False))

    messages = []
    if boundary_warning:
        side = "最小深度边界" if at_min else "最大深度边界"
        messages.append(f"best_depth 位于扫描{side}，深度结果不稳定。")
    if wide_y_warning:
        messages.append("best_x 附近高分区 y 跨度过宽，横向位置存在不确定性。")
    if raw_weighted_divergence_warning:
        messages.append("raw_best 与 weighted_best 三维位置差异较大，深度权重对结果影响显著。")
    if shallow_bias_warning:
        messages.append("weighted_best 明显比 raw_best 更浅，存在 Rayleigh 深度先验浅部偏置。")
    if not messages:
        messages.append("Stage 3B 新增扫描 warning 未触发，但仍需人工检查切片图和走时曲线。")

    return {
        "best_depth_at_boundary_warning": boundary_warning,
        "best_depth_at_min_boundary": bool(at_min),
        "best_depth_at_max_boundary": bool(at_max),
        "wide_y_high_score_zone_warning": bool(wide_y_warning),
        "wide_y_high_score_span_m": y_span_m,
        "raw_weighted_divergence_warning": bool(raw_weighted_divergence_warning),
        "raw_weighted_location_diff_m": distance_diff,
        "raw_weighted_depth_diff_m": depth_diff,
        "depth_prior_bias_warning": bool(depth_prior_bias_warning),
        "shallow_bias_warning": bool(shallow_bias_warning),
        "messages": messages,
    }


def assign_confidence_flag(
    peak_sharpness: float,
    score_contrast: float,
    consistency_cv: float,
    consistency_warning: bool,
    coupling_warning: bool,
    stage3b_warnings: dict[str, Any],
    params: SimpleNamespace,
) -> str:
    """根据规则输出 high / medium-low / medium / low 诊断标志。

    这里的 flag 是科研原型阶段的诊断标签，不是概率意义置信度。规则刻意保守：
    若峰值不尖锐、整体对比度低、多炮一致性差、y-depth 耦合风险明显，或 Stage 3B
    新增的深度边界/浅部偏置/raw-weighted 分歧 warning 触发，则下调等级。
    """

    severe_warning = (
        stage3b_warnings["best_depth_at_boundary_warning"]
        or stage3b_warnings["raw_weighted_divergence_warning"]
        or stage3b_warnings["shallow_bias_warning"]
    )
    moderate_warning = (
        stage3b_warnings["wide_y_high_score_zone_warning"]
        or stage3b_warnings["depth_prior_bias_warning"]
    )
    if severe_warning or coupling_warning or consistency_warning or peak_sharpness < 1.2 or score_contrast < 1.5:
        return "low"
    if moderate_warning:
        return "medium-low"
    if (
        peak_sharpness < 2.0
        or score_contrast < 2.0
        or consistency_cv > 0.5 * params.confidence.consistency_warning_cv_threshold
    ):
        return "medium"
    return "high"
