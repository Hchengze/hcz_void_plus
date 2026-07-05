"""三维概率区域连通体工具。

Stage 5I 需要把 posterior-like 高概率区域表达成三维候选体，而不是只给一个最大点。
本模块复用 6-neighbor 连通规则，输出每个连通体的点数、概率质量和 x/y/depth 范围。
"""

from __future__ import annotations

from collections import deque
from typing import Any

import numpy as np


NEIGHBOR_OFFSETS_6 = (
    (1, 0, 0),
    (-1, 0, 0),
    (0, 1, 0),
    (0, -1, 0),
    (0, 0, 1),
    (0, 0, -1),
)


def _box_from_indices(indices: np.ndarray, x_grid: np.ndarray, y_grid: np.ndarray, depth_grid: np.ndarray) -> dict[str, Any]:
    ix = indices[:, 0]
    iy = indices[:, 1]
    iz = indices[:, 2]
    return {
        "point_count": int(indices.shape[0]),
        "x_min_m": float(np.min(x_grid[ix])),
        "x_max_m": float(np.max(x_grid[ix])),
        "y_min_m": float(np.min(y_grid[iy])),
        "y_max_m": float(np.max(y_grid[iy])),
        "depth_min_m": float(np.min(depth_grid[iz])),
        "depth_max_m": float(np.max(depth_grid[iz])),
        "x_span_m": float(np.max(x_grid[ix]) - np.min(x_grid[ix])),
        "y_span_m": float(np.max(y_grid[iy]) - np.min(y_grid[iy])),
        "depth_span_m": float(np.max(depth_grid[iz]) - np.min(depth_grid[iz])),
    }


def label_probability_components(
    mask: np.ndarray,
    x_grid: np.ndarray,
    y_grid: np.ndarray,
    depth_grid: np.ndarray,
) -> dict[str, Any]:
    """对三维高概率布尔体做 6-neighbor 连通标记。"""

    high_mask = np.asarray(mask, dtype=bool)
    if high_mask.ndim != 3:
        raise ValueError(f"mask 必须是三维，当前 shape={high_mask.shape}")
    visited = np.zeros_like(high_mask, dtype=bool)
    shape = high_mask.shape
    components: list[dict[str, Any]] = []

    for start in np.argwhere(high_mask):
        start_tuple = tuple(int(v) for v in start)
        if visited[start_tuple]:
            continue
        queue: deque[tuple[int, int, int]] = deque([start_tuple])
        visited[start_tuple] = True
        indices: list[tuple[int, int, int]] = []
        while queue:
            current = queue.popleft()
            indices.append(current)
            for dx, dy, dz in NEIGHBOR_OFFSETS_6:
                neighbor = (current[0] + dx, current[1] + dy, current[2] + dz)
                if (
                    0 <= neighbor[0] < shape[0]
                    and 0 <= neighbor[1] < shape[1]
                    and 0 <= neighbor[2] < shape[2]
                    and high_mask[neighbor]
                    and not visited[neighbor]
                ):
                    visited[neighbor] = True
                    queue.append(neighbor)
        components.append(_box_from_indices(np.asarray(indices, dtype=int), x_grid, y_grid, depth_grid))

    components.sort(key=lambda item: item["point_count"], reverse=True)
    return {
        "component_count": len(components),
        "component_boxes": components,
        "largest_component_box": components[0] if components else None,
        "multi_peak_warning": len(components) > 1,
    }
