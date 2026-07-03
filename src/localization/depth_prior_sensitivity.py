"""Depth prior 强度轻量敏感性诊断。"""

from __future__ import annotations

from types import SimpleNamespace
from typing import Any

import numpy as np

from src.physics.rayleigh import rayleigh_depth_weight


def run_depth_prior_sensitivity(score_volume_unweighted: np.ndarray, params: SimpleNamespace) -> dict[str, Any]:
    """基于 unweighted score volume 快速比较不同 depth prior 强度。

    factor=off 表示不加深度权重。其它 factor 使用 penetration_depth =
    factor * wavelength。该诊断不重新计算走时，只评估深度先验对已有 score volume
    的影响。
    """

    results: dict[str, Any] = {}
    x_grid = params.derived.scan_x_grid
    y_grid = params.derived.scan_y_grid
    depth_grid = params.derived.scan_depth_grid
    for token in params.scan.depth_prior_factor_list:
        if token.lower() == "off":
            volume = score_volume_unweighted
            penetration_depth = None
        else:
            factor = float(token)
            penetration_depth = factor * params.derived.estimated_wavelength_m
            volume = score_volume_unweighted * rayleigh_depth_weight(depth_grid, penetration_depth)[None, None, :]
        best_index = np.unravel_index(int(np.argmax(volume)), volume.shape)
        results[token] = {
            "penetration_depth_m": penetration_depth,
            "best_location": {
                "x_m": float(x_grid[best_index[0]]),
                "y_m": float(y_grid[best_index[1]]),
                "depth_m": float(depth_grid[best_index[2]]),
            },
            "best_score": float(volume[best_index]),
            "best_depth_at_boundary": bool(depth_grid[best_index[2]] in {depth_grid[0], depth_grid[-1]}),
        }
    return {"factors": results}

