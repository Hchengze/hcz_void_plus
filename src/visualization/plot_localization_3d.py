"""三维定位结果可视化。

Stage 5G 将人工主视图拉回 source_xyz / receiver_xyz / candidate_xyz 和 x-y-depth
定位空间。本模块只表达三维运动学扫描结果，不把 elastic2d validation 解释成三维波场。
"""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from src.visualization.plot_style import setup_chinese_matplotlib


def _save(fig: plt.Figure, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(output_path)
    plt.close(fig)


def _location_array(location: dict[str, Any], fallback: np.ndarray) -> np.ndarray:
    if not location:
        return fallback
    return np.array(
        [
            float(location.get("x_m", fallback[0])),
            float(location.get("y_m", fallback[1])),
            float(location.get("depth_m", fallback[2])),
        ],
        dtype=float,
    )


def _high_score_points(params: SimpleNamespace, score_volume: np.ndarray, threshold_ratio: float) -> tuple[np.ndarray, np.ndarray]:
    """从三维 score volume 中抽取受控数量的高分候选点。"""

    volume = np.asarray(score_volume, dtype=float)
    finite = volume[np.isfinite(volume)]
    if finite.size == 0:
        return np.empty((0, 3)), np.empty((0,))
    threshold = float(np.max(finite)) * float(threshold_ratio)
    mask = volume >= threshold
    indices = np.argwhere(mask)
    if indices.shape[0] > 900:
        order = np.argsort(volume[mask])[-900:]
        indices = indices[order]
    points = np.column_stack(
        [
            params.derived.scan_x_grid[indices[:, 0]],
            params.derived.scan_y_grid[indices[:, 1]],
            params.derived.scan_depth_grid[indices[:, 2]],
        ]
    )
    values = volume[indices[:, 0], indices[:, 1], indices[:, 2]]
    return points, values


def plot_3d_high_score_region(
    params: SimpleNamespace,
    score_volume: np.ndarray,
    confidence_metrics: dict[str, Any],
    scan_result: dict[str, Any],
    output_path: Path,
) -> None:
    """绘制三维高分候选体/点云。"""

    setup_chinese_matplotlib()
    high_region = confidence_metrics.get("high_score_region", {})
    threshold = float(high_region.get("threshold_ratio", params.confidence.threshold_ratio))
    points, values = _high_score_points(params, score_volume, threshold)
    truth = np.array([params.anomaly.x0_m, params.anomaly.y0_m, params.anomaly.depth_m], dtype=float)
    recommended = _location_array(confidence_metrics.get("recommended_location") or scan_result.get("best_location"), truth)

    fig = plt.figure(figsize=(8.8, 6.0), dpi=150)
    ax = fig.add_subplot(111, projection="3d")
    if points.size:
        scatter = ax.scatter(points[:, 0], points[:, 1], points[:, 2], c=values, cmap="viridis", s=18, alpha=0.72, label="高分候选点")
        fig.colorbar(scatter, ax=ax, fraction=0.04, pad=0.06, label="score")
    ax.scatter([truth[0]], [truth[1]], [truth[2]], marker="x", s=90, color="black", linewidths=2.0, label="真值位置")
    ax.scatter([recommended[0]], [recommended[1]], [recommended[2]], marker="o", s=90, facecolors="none", edgecolors="#e15759", linewidths=2.0, label="推荐/最佳位置")
    ax.text2D(
        0.02,
        0.02,
        "说明：这是三维运动学定位点云，不代表当前 elastic2d 已是三维弹性正演。",
        transform=ax.transAxes,
        fontsize=8.5,
        color="#e15759",
    )
    ax.set_xlabel("x / m")
    ax.set_ylabel("y / m")
    ax.set_zlabel("埋深 h / m")
    ax.invert_zaxis()
    ax.set_title("三维高分候选区：运动学 x-y-depth 扫描结果")
    ax.view_init(elev=24, azim=-58)
    ax.legend(loc="upper left", fontsize=8)
    _save(fig, output_path)


def plot_recommended_location_3d(
    params: SimpleNamespace,
    confidence_metrics: dict[str, Any],
    scan_result: dict[str, Any],
    output_path: Path,
) -> None:
    """绘制三维推荐位置与真值位置。"""

    setup_chinese_matplotlib()
    truth = np.array([params.anomaly.x0_m, params.anomaly.y0_m, params.anomaly.depth_m], dtype=float)
    best = _location_array(scan_result.get("best_location"), truth)
    recommended = _location_array(confidence_metrics.get("recommended_location"), best)
    distance = float(np.linalg.norm(recommended - truth))
    fig = plt.figure(figsize=(7.6, 5.6), dpi=150)
    ax = fig.add_subplot(111, projection="3d")
    ax.scatter([truth[0]], [truth[1]], [truth[2]], marker="x", s=110, color="black", linewidths=2.2, label="真值位置")
    ax.scatter([best[0]], [best[1]], [best[2]], marker="s", s=72, color="#4e79a7", label="扫描最佳点")
    ax.scatter([recommended[0]], [recommended[1]], [recommended[2]], marker="o", s=96, facecolors="none", edgecolors="#e15759", linewidths=2.0, label="推荐参考点")
    ax.plot([truth[0], recommended[0]], [truth[1], recommended[1]], [truth[2], recommended[2]], color="#e15759", linestyle="--", label="推荐误差向量")
    ax.set_xlabel("x / m")
    ax.set_ylabel("y / m")
    ax.set_zlabel("埋深 h / m")
    ax.invert_zaxis()
    ax.set_title("三维推荐位置：科研候选，不是工程确诊")
    ax.text2D(
        0.02,
        0.02,
        f"推荐-真值距离约 {distance:.2f} m；三维表达不代表 3D elastic 正演。",
        transform=ax.transAxes,
        fontsize=8.5,
        color="#e15759",
    )
    ax.legend(loc="upper left", fontsize=8)
    _save(fig, output_path)


def plot_3d_uncertainty_box(
    params: SimpleNamespace,
    confidence_metrics: dict[str, Any],
    output_path: Path,
) -> None:
    """绘制三维不确定性盒子，显示 x/y/depth span。"""

    setup_chinese_matplotlib()
    high = confidence_metrics.get("high_score_region", {})
    box = high.get("equivalent_uncertainty_box") or {}
    center = _location_array(confidence_metrics.get("recommended_location"), np.array([params.anomaly.x0_m, params.anomaly.y0_m, params.anomaly.depth_m], dtype=float))
    spans = np.array(
        [
            float(high.get("x_span_m", box.get("x_span_m", 0.0))),
            float(high.get("y_span_m", box.get("y_span_m", 0.0))),
            float(high.get("depth_span_m", box.get("depth_span_m", 0.0))),
        ],
        dtype=float,
    )
    half = np.maximum(spans / 2.0, 0.05)
    corners = np.array(
        [
            [center[0] - half[0], center[1] - half[1], center[2] - half[2]],
            [center[0] + half[0], center[1] - half[1], center[2] - half[2]],
            [center[0] + half[0], center[1] + half[1], center[2] - half[2]],
            [center[0] - half[0], center[1] + half[1], center[2] - half[2]],
            [center[0] - half[0], center[1] - half[1], center[2] + half[2]],
            [center[0] + half[0], center[1] - half[1], center[2] + half[2]],
            [center[0] + half[0], center[1] + half[1], center[2] + half[2]],
            [center[0] - half[0], center[1] + half[1], center[2] + half[2]],
        ]
    )
    edges = [(0, 1), (1, 2), (2, 3), (3, 0), (4, 5), (5, 6), (6, 7), (7, 4), (0, 4), (1, 5), (2, 6), (3, 7)]
    fig = plt.figure(figsize=(7.8, 5.8), dpi=150)
    ax = fig.add_subplot(111, projection="3d")
    for a, b in edges:
        ax.plot(corners[[a, b], 0], corners[[a, b], 1], corners[[a, b], 2], color="#4e79a7", linewidth=1.6)
    ax.scatter([center[0]], [center[1]], [center[2]], marker="o", s=82, color="#e15759", label="推荐参考点")
    ax.set_xlabel("x / m")
    ax.set_ylabel("y / m")
    ax.set_zlabel("埋深 h / m")
    ax.invert_zaxis()
    ax.set_title(f"三维不确定性盒子：x={spans[0]:.2f} m, y={spans[1]:.2f} m, h={spans[2]:.2f} m")
    ax.text2D(
        0.02,
        0.02,
        "深度向下为正；盒子来自 x-y-depth 运动学高分区。",
        transform=ax.transAxes,
        fontsize=8.5,
        color="#e15759",
    )
    ax.legend(loc="upper left", fontsize=8)
    _save(fig, output_path)
