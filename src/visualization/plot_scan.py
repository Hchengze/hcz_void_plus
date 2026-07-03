"""基础扫描定位结果绘图。"""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from src.geometry.road_geometry import road_boundary_xy
from src.visualization.plot_style import setup_chinese_matplotlib


def _nearest_index(grid: np.ndarray, value: float) -> int:
    return int(np.argmin(np.abs(grid - value)))


def plot_scan_x_depth_slice(
    params: SimpleNamespace,
    normalized_score_volume: np.ndarray,
    best_location: dict[str, float],
    output_path: Path,
) -> None:
    """绘制固定 y 的 x-depth 扫描得分切片。"""

    setup_chinese_matplotlib()
    y_grid = params.derived.scan_y_grid
    depth_grid = params.derived.scan_depth_grid
    x_grid = params.derived.scan_x_grid
    iy = _nearest_index(y_grid, best_location["y_m"])
    slice_data = normalized_score_volume[:, iy, :].T

    fig, ax = plt.subplots(figsize=(8.5, 5), dpi=150)
    image = ax.imshow(
        slice_data,
        extent=[x_grid[0], x_grid[-1], depth_grid[-1], depth_grid[0]],
        aspect="auto",
        cmap="viridis",
        vmin=0.0,
        vmax=1.0,
    )
    ax.scatter([params.anomaly.x0_m], [params.anomaly.depth_m], marker="x", s=60, color="white", label="真实异常体")
    ax.scatter([best_location["x_m"]], [best_location["depth_m"]], marker="o", s=38, facecolors="none", edgecolors="red", label="扫描最佳位置")
    ax.set_xlabel("沿道路方向 x / m")
    ax.set_ylabel("埋深 h / m")
    ax.set_title("多炮扫描得分 x-depth 切片")
    ax.legend(loc="best", fontsize=8)
    fig.colorbar(image, ax=ax, label="归一化扫描得分")
    fig.tight_layout()
    fig.savefig(output_path)
    plt.close(fig)


def plot_scan_x_y_slice(
    params: SimpleNamespace,
    normalized_score_volume: np.ndarray,
    best_location: dict[str, float],
    output_path: Path,
) -> None:
    """绘制固定 depth 的 x-y 扫描得分切片。"""

    setup_chinese_matplotlib()
    x_grid = params.derived.scan_x_grid
    y_grid = params.derived.scan_y_grid
    depth_grid = params.derived.scan_depth_grid
    iz = _nearest_index(depth_grid, best_location["depth_m"])
    slice_data = normalized_score_volume[:, :, iz].T

    fig, ax = plt.subplots(figsize=(8.5, 4.8), dpi=150)
    image = ax.imshow(
        slice_data,
        extent=[x_grid[0], x_grid[-1], y_grid[-1], y_grid[0]],
        aspect="auto",
        cmap="viridis",
        vmin=0.0,
        vmax=1.0,
    )
    ax.scatter([params.anomaly.x0_m], [params.anomaly.y0_m], marker="x", s=60, color="white", label="真实异常体")
    ax.scatter([best_location["x_m"]], [best_location["y_m"]], marker="o", s=38, facecolors="none", edgecolors="red", label="扫描最佳位置")
    ax.set_xlabel("沿道路方向 x / m")
    ax.set_ylabel("横穿道路方向 y / m")
    ax.set_title("多炮扫描得分 x-y 切片")
    ax.legend(loc="best", fontsize=8)
    fig.colorbar(image, ax=ax, label="归一化扫描得分")
    fig.tight_layout()
    fig.savefig(output_path)
    plt.close(fig)


def plot_best_location_map(
    params: SimpleNamespace,
    source_xyz: np.ndarray,
    receiver_xyz: np.ndarray,
    best_location: dict[str, float],
    output_path: Path,
) -> None:
    """绘制平面定位图：道路、光纤线、震源线、真值和最佳位置。"""

    setup_chinese_matplotlib()
    boundary = road_boundary_xy(params)
    fig, ax = plt.subplots(figsize=(9, 4.8), dpi=150)
    ax.plot(boundary[:, 0], boundary[:, 1], color="0.25", linewidth=1.5, label="道路范围")
    ax.scatter(receiver_xyz[:, 0], receiver_xyz[:, 1], s=7, color="#1f77b4", label="DAS-like 光纤通道")
    ax.scatter(source_xyz[:, 0], source_xyz[:, 1], s=26, marker="^", color="#d62728", label="震源点")
    ax.scatter([params.anomaly.x0_m], [params.anomaly.y0_m], marker="x", s=70, color="#2ca02c", label="真实异常体")
    ax.scatter([best_location["x_m"]], [best_location["y_m"]], marker="o", s=55, facecolors="none", edgecolors="red", label="扫描最佳位置")
    ax.set_xlabel("沿道路方向 x / m")
    ax.set_ylabel("横穿道路方向 y / m")
    ax.set_title("基础多炮扫描平面定位图（非工程确诊）")
    ax.set_aspect("equal", adjustable="box")
    ax.grid(True, alpha=0.25)
    ax.legend(loc="best", fontsize=8)
    fig.tight_layout()
    fig.savefig(output_path)
    plt.close(fig)
