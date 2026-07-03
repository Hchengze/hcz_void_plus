"""Stage 4B 验证实验的公共工具。"""

from __future__ import annotations

import copy
from types import SimpleNamespace
from typing import Any

import numpy as np

from src.confidence.uncertainty_region import compute_3d_high_score_region


def clone_params(params: SimpleNamespace) -> SimpleNamespace:
    """深拷贝 params，保证消融实验不会改动主流程参数对象。"""

    return copy.deepcopy(params)


def normalize_volume(volume: np.ndarray) -> np.ndarray:
    """把 score volume 归一化到 0-1，用于属性组合和绘图。"""

    vmin = float(np.min(volume))
    vmax = float(np.max(volume))
    if vmax <= vmin:
        return np.zeros_like(volume, dtype=float)
    return (volume - vmin) / (vmax - vmin)


def best_from_volume(
    volume: np.ndarray,
    x_grid: np.ndarray,
    y_grid: np.ndarray,
    depth_grid: np.ndarray,
    truth_xyz: np.ndarray,
) -> dict[str, Any]:
    """从任意三维 score volume 中提取 best 和真值误差。"""

    best_index = np.unravel_index(int(np.argmax(volume)), volume.shape)
    best_location = {
        "x_m": float(x_grid[best_index[0]]),
        "y_m": float(y_grid[best_index[1]]),
        "depth_m": float(depth_grid[best_index[2]]),
    }
    best_xyz = np.array([best_location["x_m"], best_location["y_m"], best_location["depth_m"]], dtype=float)
    error_vec = best_xyz - truth_xyz
    return {
        "best_index": tuple(int(v) for v in best_index),
        "best_location": best_location,
        "best_score": float(volume[best_index]),
        "truth_error": {
            "dx_m": float(error_vec[0]),
            "dy_m": float(error_vec[1]),
            "ddepth_m": float(error_vec[2]),
            "distance_m": float(np.linalg.norm(error_vec)),
        },
    }


def make_diagnostic_scan_grid(params: SimpleNamespace, max_points: int = 4500) -> dict[str, np.ndarray]:
    """构建轻量三维诊断网格。

    Stage 4B 的消融实验需要多次扫描。为了保持本地快速可跑，消融默认在
    原 scan grid 的三维子采样网格上运行，并强制保留真值附近坐标。主流程
    的正式 score volume 仍使用完整 params.derived.scan_*_grid。
    """

    x_grid = np.asarray(params.derived.scan_x_grid, dtype=float)
    y_grid = np.asarray(params.derived.scan_y_grid, dtype=float)
    depth_grid = np.asarray(params.derived.scan_depth_grid, dtype=float)
    current_points = len(x_grid) * len(y_grid) * len(depth_grid)
    if current_points <= max_points:
        return {"x_grid": x_grid, "y_grid": y_grid, "depth_grid": depth_grid}

    scale = (current_points / max_points) ** (1.0 / 3.0)
    stride = max(1, int(np.ceil(scale)))
    x_sub = x_grid[::stride]
    y_sub = y_grid[::stride]
    depth_sub = depth_grid[::stride]

    def with_nearest(grid: np.ndarray, value: float) -> np.ndarray:
        nearest = grid[int(np.argmin(np.abs(grid - value)))]
        return np.unique(np.concatenate([grid[::stride], np.asarray([nearest], dtype=float)]))

    x_sub = with_nearest(x_grid, params.anomaly.x0_m)
    y_sub = with_nearest(y_grid, params.anomaly.y0_m)
    depth_sub = with_nearest(depth_grid, params.anomaly.depth_m)
    return {"x_grid": x_sub, "y_grid": y_sub, "depth_grid": depth_sub}


def summarize_volume(
    params: SimpleNamespace,
    volume: np.ndarray,
    scan_grid: dict[str, np.ndarray] | None = None,
) -> dict[str, Any]:
    """生成消融实验通用指标。"""

    grid = scan_grid or {
        "x_grid": params.derived.scan_x_grid,
        "y_grid": params.derived.scan_y_grid,
        "depth_grid": params.derived.scan_depth_grid,
    }
    truth = np.array([params.anomaly.x0_m, params.anomaly.y0_m, params.anomaly.depth_m], dtype=float)
    best = best_from_volume(volume, grid["x_grid"], grid["y_grid"], grid["depth_grid"], truth)
    high_region = compute_3d_high_score_region(
        volume,
        grid["x_grid"],
        grid["y_grid"],
        grid["depth_grid"],
        params.confidence.threshold_ratio,
    )
    return {
        **best,
        "x_span_m": high_region["x_span_m"],
        "y_span_m": high_region["y_span_m"],
        "depth_span_m": high_region["depth_span_m"],
        "high_score_region_point_count": high_region["high_score_region_point_count"],
        "high_score_component_count": high_region["high_score_component_count"],
        "multi_region_warning": high_region["multi_region_warning"],
        "high_score_region": high_region,
    }

