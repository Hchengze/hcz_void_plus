"""三维高分区连通域诊断。

本模块只处理离散 scan grid 上的布尔高分区，不涉及真实地下体边界。它的
目的是避免用一个很大的不确定性盒把多个分离的候选高分团块混在一起。
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


def _component_box(indices: np.ndarray, x_grid: np.ndarray, y_grid: np.ndarray, depth_grid: np.ndarray) -> dict[str, Any]:
    """把一个连通分量的离散索引转换为物理坐标盒。"""

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


def label_high_score_components(
    high_mask: np.ndarray,
    x_grid: np.ndarray,
    y_grid: np.ndarray,
    depth_grid: np.ndarray,
) -> dict[str, Any]:
    """对三维高分布尔体做 6-neighbor 连通域标记。

    参数
    ----
    high_mask:
        shape = ``n_x x n_y x n_depth``。True 表示得分超过阈值。

    返回
    ----
    dict:
        包含 component_count、largest_component_box、component_boxes 和
        multi_region_warning。若出现多个分离高分团块，应在推荐结果中表达为
        多候选区，而不是一个确定单点。
    """

    if high_mask.ndim != 3:
        raise ValueError(f"high_mask 维度错误：当前 shape={high_mask.shape}，应为三维。")

    visited = np.zeros_like(high_mask, dtype=bool)
    component_boxes: list[dict[str, Any]] = []
    shape = high_mask.shape

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

        component_boxes.append(_component_box(np.asarray(indices, dtype=int), x_grid, y_grid, depth_grid))

    component_boxes.sort(key=lambda item: item["point_count"], reverse=True)
    component_count = len(component_boxes)
    return {
        "high_score_component_count": component_count,
        "component_boxes": component_boxes,
        "largest_component_box": component_boxes[0] if component_boxes else None,
        "multi_region_warning": component_count > 1,
    }

