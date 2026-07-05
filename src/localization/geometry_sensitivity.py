"""三维观测系统敏感性体。

Stage 5I 开始把单侧 DAS-like 几何导致的 y-depth 耦合从 warning 推进到体属性诊断。
本模块对每个 candidate_xyz 计算孔径/照明指标，输出 ``geometry_resolution_volume``。
"""

from __future__ import annotations

from typing import Any

import numpy as np

from src.localization.aperture_metrics import summarize_aperture


def compute_geometry_resolution_volume(
    source_xyz: np.ndarray,
    receiver_xyz: np.ndarray,
    x_grid: np.ndarray,
    y_grid: np.ndarray,
    depth_grid: np.ndarray,
) -> dict[str, Any]:
    """为整个三维扫描网格计算几何分辨率诊断体。"""

    shape = (len(x_grid), len(y_grid), len(depth_grid))
    resolution = np.zeros(shape, dtype=float)
    lateral = np.zeros(shape, dtype=float)
    depth = np.zeros(shape, dtype=float)
    illumination = np.zeros(shape, dtype=float)
    aperture = np.zeros(shape, dtype=float)

    for ix, x_m in enumerate(x_grid):
        for iy, y_m in enumerate(y_grid):
            for iz, depth_m in enumerate(depth_grid):
                metrics = summarize_aperture(source_xyz, receiver_xyz, np.array([x_m, y_m, depth_m], dtype=float))
                resolution[ix, iy, iz] = metrics["y_depth_resolution_indicator"]
                lateral[ix, iy, iz] = metrics["lateral_ambiguity_index"]
                depth[ix, iy, iz] = metrics["depth_ambiguity_index"]
                illumination[ix, iy, iz] = metrics["candidate_illumination_count"]
                aperture[ix, iy, iz] = metrics["aperture_angle_mean_deg"]

    geometry_class = "single_side_line_das_like"
    summary = {
        "geometry_resolution_status": "computed",
        "source_receiver_geometry_class": geometry_class,
        "geometry_resolution_mean": float(np.mean(resolution)),
        "geometry_resolution_max": float(np.max(resolution)),
        "lateral_ambiguity_index_mean": float(np.mean(lateral)),
        "depth_ambiguity_index_mean": float(np.mean(depth)),
        "candidate_illumination_count_mean": float(np.mean(illumination)),
        "aperture_angle_mean_deg": float(np.mean(aperture)),
        "y_depth_separable": bool(np.mean(resolution) > 0.12),
        "note": "single-sided DAS-like geometry can keep y-depth ambiguity even when x is stable",
    }
    return {
        "geometry_resolution_volume": resolution,
        "lateral_ambiguity_volume": lateral,
        "depth_ambiguity_volume": depth,
        "illumination_count_volume": illumination,
        "aperture_angle_volume": aperture,
        "geometry_resolution_summary": summary,
        **summary,
    }
