"""三维高分区不确定性统计与推荐位置规则。"""

from __future__ import annotations

from types import SimpleNamespace
from typing import Any

import numpy as np


def compute_3d_high_score_region(
    score_volume: np.ndarray,
    x_grid: np.ndarray,
    y_grid: np.ndarray,
    depth_grid: np.ndarray,
    threshold_ratio: float,
) -> dict[str, Any]:
    """统计三维 score volume 中的高分候选体。

    物理意义：
        单侧 DAS-like 几何下，最高点只是一个离散网格点；更诚实的表达是“哪些三维
        候选点的得分接近最高点”。本函数用 threshold_ratio * best_score 定义高分区，
        统计 x/y/depth 跨度、点数和等效体积，作为三维不确定性区域的基础。

    输入：
        score_volume：shape = n_x × n_y × n_depth；
        x_grid/y_grid/depth_grid：对应坐标网格，单位 m；
        threshold_ratio：高分区阈值比例，例如 0.9。

    输出：
        dict，包含 high_score_region_point_count、x/y/depth span、等效不确定性盒等。

    限制：
        这不是概率置信区间，也不是工程风险边界，只是运动学扫描得分体的高分区统计。
    """

    if score_volume.ndim != 3:
        raise ValueError(f"score_volume 维度错误：当前 shape={score_volume.shape}，应为 n_x × n_y × n_depth。")
    best_score = float(np.max(score_volume))
    threshold = float(threshold_ratio * best_score)
    high_mask = score_volume >= threshold
    point_count = int(np.count_nonzero(high_mask))
    if point_count == 0:
        x_min = x_max = y_min = y_max = depth_min = depth_max = None
        x_span = y_span = depth_span = volume_estimate = 0.0
    else:
        ix, iy, iz = np.where(high_mask)
        high_x = x_grid[ix]
        high_y = y_grid[iy]
        high_depth = depth_grid[iz]
        x_min, x_max = float(np.min(high_x)), float(np.max(high_x))
        y_min, y_max = float(np.min(high_y)), float(np.max(high_y))
        depth_min, depth_max = float(np.min(high_depth)), float(np.max(high_depth))
        x_span = float(x_max - x_min)
        y_span = float(y_max - y_min)
        depth_span = float(depth_max - depth_min)
        dx = float(np.median(np.diff(x_grid))) if len(x_grid) > 1 else 1.0
        dy = float(np.median(np.diff(y_grid))) if len(y_grid) > 1 else 1.0
        dz = float(np.median(np.diff(depth_grid))) if len(depth_grid) > 1 else 1.0
        volume_estimate = float(point_count * dx * dy * dz)
    return {
        "threshold_ratio": threshold_ratio,
        "threshold": threshold,
        "best_score": best_score,
        "high_score_region_point_count": point_count,
        "x_span_m": x_span,
        "y_span_m": y_span,
        "depth_span_m": depth_span,
        "high_score_region_volume_estimate_m3": volume_estimate,
        "equivalent_uncertainty_box": {
            "x_min_m": x_min,
            "x_max_m": x_max,
            "y_min_m": y_min,
            "y_max_m": y_max,
            "depth_min_m": depth_min,
            "depth_max_m": depth_max,
        },
    }


def build_recommended_location(
    params: SimpleNamespace,
    scan_result: dict[str, Any],
    stage3b_warnings: dict[str, Any],
    high_score_region: dict[str, Any],
) -> dict[str, Any]:
    """根据 raw/weighted 分歧和三维高分区给出推荐位置表达。

    推荐规则：
        1. 若 weighted_best 贴深度边界且 raw/weighted 分歧明显，不采用 weighted_best；
        2. 若 raw_best 与 weighted_best 接近，且无边界、宽 y、分歧 warning，可采用 weighted_best；
        3. 若结果不稳定，输出 uncertainty_interval / unstable_candidate，并给出三维区间；
        4. recommended_location 始终是科研候选表达，不是工程确诊点。
    """

    unweighted = scan_result["unweighted_best_location"]
    weighted = scan_result["weighted_best_location"]
    active = scan_result["active_best_location"]
    box = high_score_region["equivalent_uncertainty_box"]
    unstable = (
        stage3b_warnings["best_depth_at_boundary_warning"]
        or stage3b_warnings["raw_weighted_divergence_warning"]
        or stage3b_warnings["wide_y_high_score_zone_warning"]
        or stage3b_warnings["shallow_bias_warning"]
    )
    if unstable:
        x_interval = [
            min(value for value in [box["x_min_m"], unweighted["x_m"], weighted["x_m"]] if value is not None),
            max(value for value in [box["x_max_m"], unweighted["x_m"], weighted["x_m"]] if value is not None),
        ]
        y_interval = [
            min(value for value in [box["y_min_m"], unweighted["y_m"], weighted["y_m"]] if value is not None),
            max(value for value in [box["y_max_m"], unweighted["y_m"], weighted["y_m"]] if value is not None),
        ]
        depth_interval = [
            min(value for value in [box["depth_min_m"], unweighted["depth_m"], weighted["depth_m"]] if value is not None),
            max(value for value in [box["depth_max_m"], unweighted["depth_m"], weighted["depth_m"]] if value is not None),
        ]
        recommended_type = "uncertainty_interval"
        recommended_location = {
            "x_m": unweighted["x_m"],
            "y_m": unweighted["y_m"],
            "depth_m": unweighted["depth_m"],
            "x_interval_m": x_interval,
            "y_interval_m": y_interval,
            "depth_interval_m": depth_interval,
        }
        reason = (
            "weighted_best 受到深度权重影响且触发边界/宽 y/unweighted-weighted 分歧等 warning；"
            "因此不把 weighted_best 作为单点推荐，而采用 unweighted_best 作为参考点，"
            "并以三维高分区区间表达不确定性。"
        )
    elif params.scan.use_depth_weight:
        recommended_type = "weighted_best"
        recommended_location = dict(weighted)
        reason = "unweighted_best 与 weighted_best 接近，且未触发主要不稳定 warning，可采用 weighted_best 作为科研候选点。"
    else:
        recommended_type = "unweighted_best"
        recommended_location = dict(active)
        reason = "当前未启用 depth weighting，采用 active/unweighted best 作为科研候选点。"
    return {
        "recommended_location": recommended_location,
        "recommended_location_type": recommended_type,
        "recommended_location_reason": reason,
        "depth_uncertainty_interval_m": recommended_location.get("depth_interval_m", [box["depth_min_m"], box["depth_max_m"]]),
    }
