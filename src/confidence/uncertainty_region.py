"""三维高分区不确定性统计与推荐位置规则。

单侧 DAS-like 三维几何下，最高分网格点通常不能被解释为确定地下点。
本模块把 score volume 中接近最高分的候选体统计为三维高分区，并进一步
做 6-neighbor 连通域分析：若存在多个分离高分团块，推荐结果应表达为
候选区集合，而不是一个大盒子或单点。
"""

from __future__ import annotations

from types import SimpleNamespace
from typing import Any

import numpy as np

from src.localization.connected_components import label_high_score_components


def compute_3d_high_score_region(
    score_volume: np.ndarray,
    x_grid: np.ndarray,
    y_grid: np.ndarray,
    depth_grid: np.ndarray,
    threshold_ratio: float,
) -> dict[str, Any]:
    """统计三维 score volume 中的高分候选体。

    参数
    ----
    score_volume:
        shape = ``n_x x n_y x n_depth``。
    x_grid/y_grid/depth_grid:
        与 score volume 三个轴对应的物理坐标，单位 m。
    threshold_ratio:
        高分阈值比例，例如 0.9 表示 ``score >= 0.9 * best_score``。

    返回
    ----
    dict:
        包含 x/y/depth 跨度、等效不确定性盒、连通域数量和各连通域盒。

    限制
    ----
    这是运动学 score volume 的高分区统计，不是概率置信区间，不是工程
    风险边界，也不是真实空洞边界。
    """

    if score_volume.ndim != 3:
        raise ValueError(f"score_volume 维度错误：当前 shape={score_volume.shape}，应为 n_x x n_y x n_depth。")

    best_score = float(np.max(score_volume))
    threshold = float(threshold_ratio * best_score)
    high_mask = score_volume >= threshold
    point_count = int(np.count_nonzero(high_mask))

    if point_count == 0:
        x_min = x_max = y_min = y_max = depth_min = depth_max = None
        x_span = y_span = depth_span = volume_estimate = 0.0
        components = {
            "high_score_component_count": 0,
            "component_boxes": [],
            "largest_component_box": None,
            "multi_region_warning": False,
        }
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
        components = label_high_score_components(high_mask, x_grid, y_grid, depth_grid)

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
        "high_score_component_count": components["high_score_component_count"],
        "component_boxes": components["component_boxes"],
        "largest_component_box": components["largest_component_box"],
        "multi_region_warning": components["multi_region_warning"],
    }


def build_recommended_location(
    params: SimpleNamespace,
    scan_result: dict[str, Any],
    stage3b_warnings: dict[str, Any],
    high_score_region: dict[str, Any],
) -> dict[str, Any]:
    """根据 score 稳定性和三维高分区给出推荐位置表达。

    推荐逻辑
    --------
    1. 若 weighted_best 贴边或与 unweighted_best 明显分歧，不采用 weighted_best；
    2. 若高分区在 y/depth 上很宽，推荐不确定性区间而非单点；
    3. 若高分区由多个分离连通体组成，推荐类型变为 ``multi_region_uncertainty``；
    4. 所有输出都是科研候选表达，不是工程确诊。
    """

    unweighted = scan_result["unweighted_best_location"]
    weighted = scan_result["weighted_best_location"]
    active = scan_result["active_best_location"]
    box = high_score_region["equivalent_uncertainty_box"]
    multi_region_warning = bool(high_score_region.get("multi_region_warning", False))

    unstable = (
        stage3b_warnings["best_depth_at_boundary_warning"]
        or stage3b_warnings["raw_weighted_divergence_warning"]
        or stage3b_warnings["wide_y_high_score_zone_warning"]
        or stage3b_warnings["shallow_bias_warning"]
        or multi_region_warning
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
        recommended_type = "multi_region_uncertainty" if multi_region_warning else "uncertainty_interval"
        recommended_location = {
            "x_m": unweighted["x_m"],
            "y_m": unweighted["y_m"],
            "depth_m": unweighted["depth_m"],
            "x_interval_m": x_interval,
            "y_interval_m": y_interval,
            "depth_interval_m": depth_interval,
            "component_boxes": high_score_region.get("component_boxes", []),
        }
        reason = (
            "weighted_best 受到深度权重影响，或触发边界、宽 y、unweighted-weighted 分歧等 warning；"
            "因此不把 weighted_best 作为单点推荐，而采用 unweighted_best 作为参考点，"
            "并以三维高分区区间表达不确定性。"
        )
        if multi_region_warning:
            reason += " 高分区存在多个分离连通团块，应表达为候选区集合。"
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
        "depth_uncertainty_interval_m": recommended_location.get(
            "depth_interval_m",
            [box["depth_min_m"], box["depth_max_m"]],
        ),
    }

