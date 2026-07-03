"""轻量 score_method 对比。"""

from __future__ import annotations

from types import SimpleNamespace
from typing import Any

import numpy as np

from src.localization.multishot_scan import run_multishot_scan
from src.model.velocity_model import UniformVelocityModel


def run_score_method_comparison(
    data: np.ndarray,
    time_axis: np.ndarray,
    source_xyz: np.ndarray,
    receiver_xyz: np.ndarray,
    velocity_model: UniformVelocityModel,
    scan_grid: dict[str, Any],
    params: SimpleNamespace,
) -> dict[str, Any]:
    """在同一数据和扫描网格上轻量比较多个 score_method。

    物理意义：
        diffraction_energy_stack 和 normalized_energy_stack 对直达波残余、强道能量
        和局部散射能量的敏感性不同。这里不是大规模鲁棒性扫描，只是同一场景下的
        方法对照，用来判断深度估计是否依赖某一种得分定义。

    注意：
        为了坚持 main.py 是唯一参数中心，待比较的方法来自 params.scan.score_method_list。
        函数内部只临时切换 params.scan.score_method，并在结束时恢复原值。
    """

    original_method = params.scan.score_method
    results: dict[str, Any] = {}
    try:
        for method in params.scan.score_method_list:
            params.scan.score_method = method
            scan_result = run_multishot_scan(
                data,
                time_axis,
                source_xyz,
                receiver_xyz,
                velocity_model,
                scan_grid,
                params,
            )
            results[method] = {
                "score_volume_unweighted": scan_result["score_volume_unweighted"],
                "score_volume_depth_weighted": scan_result["score_volume_depth_weighted"],
                "unweighted_best_location": scan_result["unweighted_best_location"],
                "weighted_best_location": scan_result["weighted_best_location"],
                "unweighted_truth_error": scan_result["unweighted_truth_error"],
                "weighted_truth_error": scan_result["weighted_truth_error"],
                "unweighted_best_score": scan_result["unweighted_best_score"],
                "weighted_best_score": scan_result["weighted_best_score"],
                "weighted_depth_at_boundary": (
                    scan_result["weighted_best_location"]["depth_m"] == params.scan.depth_min_m
                    or scan_result["weighted_best_location"]["depth_m"] == params.scan.depth_max_m
                ),
            }
    finally:
        params.scan.score_method = original_method

    # 简单判断哪种方法深度更接近真值。这里仅用于报告，不作为工程优劣判定。
    best_method = None
    best_depth_error = None
    for method, result in results.items():
        depth_error = abs(result["unweighted_truth_error"]["ddepth_m"])
        if best_depth_error is None or depth_error < best_depth_error:
            best_method = method
            best_depth_error = depth_error

    return {
        "methods": results,
        "depth_stability_reference": {
            "best_unweighted_depth_method": best_method,
            "best_unweighted_depth_abs_error_m": best_depth_error,
            "note": "仅比较当前场景下 unweighted_best 的深度误差，不代表通用优劣。",
        },
    }

