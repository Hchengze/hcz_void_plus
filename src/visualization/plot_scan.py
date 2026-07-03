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


def plot_raw_vs_weighted_best_location(
    params: SimpleNamespace,
    source_xyz: np.ndarray,
    receiver_xyz: np.ndarray,
    scan_result: dict[str, object],
    output_path: Path,
) -> None:
    """绘制 raw_best 与 weighted_best 的平面位置对比图。

    物理意义：
        depth weighting 是 Rayleigh 波浅层敏感性的简化先验，它可能改变最佳候选位置。
        本图把不加深度权重的 raw_best 和加权后的 weighted_best 同时画出，避免用户只
        看到一个主 best_location 而忽略深度先验造成的偏移。
    """

    setup_chinese_matplotlib()
    boundary = road_boundary_xy(params)
    raw_best = scan_result["raw_best_location"]
    weighted_best = scan_result["weighted_best_location"]
    fig, ax = plt.subplots(figsize=(9, 4.8), dpi=150)
    ax.plot(boundary[:, 0], boundary[:, 1], color="0.25", linewidth=1.5, label="道路范围")
    ax.scatter(receiver_xyz[:, 0], receiver_xyz[:, 1], s=7, color="#1f77b4", label="DAS-like 光纤通道")
    ax.scatter(source_xyz[:, 0], source_xyz[:, 1], s=26, marker="^", color="#d62728", label="震源点")
    ax.scatter([params.anomaly.x0_m], [params.anomaly.y0_m], marker="x", s=70, color="#2ca02c", label="真实异常体")
    ax.scatter([raw_best["x_m"]], [raw_best["y_m"]], marker="s", s=55, facecolors="none", edgecolors="white", linewidths=1.8, label="raw_best")
    ax.scatter([weighted_best["x_m"]], [weighted_best["y_m"]], marker="o", s=58, facecolors="none", edgecolors="red", linewidths=1.8, label="weighted_best")
    ax.set_xlabel("沿道路方向 x / m")
    ax.set_ylabel("横穿道路方向 y / m")
    ax.set_title("raw 与 depth-weighted 最佳位置对比（非工程确诊）")
    ax.set_aspect("equal", adjustable="box")
    ax.grid(True, alpha=0.25)
    ax.legend(loc="best", fontsize=8)
    fig.tight_layout()
    fig.savefig(output_path)
    plt.close(fig)


def plot_raw_vs_weighted_x_depth_slice(
    params: SimpleNamespace,
    scan_result: dict[str, object],
    output_path: Path,
) -> None:
    """绘制 raw 与 depth-weighted x-depth 得分切片对比。

    固定 y 为 weighted_best_y。左图显示 raw score，右图显示 depth-weighted score。
    若右图最高点贴近 scan_depth_min，而左图峰带更深或更宽，则说明深度权重可能
    正在把候选位置推向浅部，需要结合报告中的 shallow_bias_warning 人工判断。
    """

    setup_chinese_matplotlib()
    x_grid = params.derived.scan_x_grid
    y_grid = params.derived.scan_y_grid
    depth_grid = params.derived.scan_depth_grid
    weighted_best = scan_result["weighted_best_location"]
    raw_best = scan_result["raw_best_location"]
    iy = _nearest_index(y_grid, weighted_best["y_m"])
    raw_slice = scan_result["normalized_score_volume_raw"][:, iy, :].T
    weighted_slice = scan_result["normalized_score_volume_depth_weighted"][:, iy, :].T

    fig, axes = plt.subplots(1, 2, figsize=(11, 4.8), dpi=150, sharey=True)
    for ax, data, title in [
        (axes[0], raw_slice, "raw score x-depth 切片"),
        (axes[1], weighted_slice, "depth-weighted score x-depth 切片"),
    ]:
        image = ax.imshow(
            data,
            extent=[x_grid[0], x_grid[-1], depth_grid[-1], depth_grid[0]],
            aspect="auto",
            cmap="viridis",
            vmin=0.0,
            vmax=1.0,
        )
        ax.scatter([params.anomaly.x0_m], [params.anomaly.depth_m], marker="x", s=60, color="white", label="真实异常体")
        ax.scatter([raw_best["x_m"]], [raw_best["depth_m"]], marker="s", s=42, facecolors="none", edgecolors="cyan", label="raw_best")
        ax.scatter([weighted_best["x_m"]], [weighted_best["depth_m"]], marker="o", s=42, facecolors="none", edgecolors="red", label="weighted_best")
        ax.set_xlabel("沿道路方向 x / m")
        ax.set_title(title)
        ax.legend(loc="best", fontsize=7)
        fig.colorbar(image, ax=ax, label="归一化得分")
    axes[0].set_ylabel("埋深 h / m")
    fig.suptitle("raw 与 depth-weighted 扫描得分对比：检查浅部偏置", fontsize=12)
    fig.tight_layout()
    fig.savefig(output_path)
    plt.close(fig)


def plot_y_high_score_width_check(
    params: SimpleNamespace,
    scan_result: dict[str, object],
    confidence_metrics: dict[str, object],
    output_path: Path,
) -> None:
    """绘制 best_x 处 y-depth 高分区宽度检查图。

    图中用等值线标出 confidence_threshold_ratio * best_score 的高分区阈值。若高分区
    沿 y 方向很宽，说明单侧 DAS-like 几何下横向定位不够稳定，即使 y-depth coupling
    的“同时宽”条件没有触发，也应报告 wide_y_high_score_zone_warning。
    """

    setup_chinese_matplotlib()
    best_index = tuple(int(v) for v in scan_result["best_index"])
    y_grid = params.derived.scan_y_grid
    depth_grid = params.derived.scan_depth_grid
    yd_slice = scan_result["normalized_score_volume"][best_index[0], :, :].T
    stage3b = confidence_metrics["stage3b_warnings"]

    fig, ax = plt.subplots(figsize=(7.2, 5), dpi=150)
    image = ax.imshow(
        yd_slice,
        extent=[y_grid[0], y_grid[-1], depth_grid[-1], depth_grid[0]],
        aspect="auto",
        cmap="magma",
        vmin=0.0,
        vmax=1.0,
    )
    if np.max(yd_slice) > 0:
        ax.contour(
            y_grid,
            depth_grid,
            yd_slice,
            levels=[params.confidence.threshold_ratio],
            colors="cyan",
            linewidths=1.2,
        )
    best = scan_result["best_location"]
    ax.scatter([params.anomaly.y0_m], [params.anomaly.depth_m], marker="x", s=65, color="white", label="真实异常体")
    ax.scatter([best["y_m"]], [best["depth_m"]], marker="o", s=52, facecolors="none", edgecolors="red", label="主 best")
    ax.set_xlabel("横穿道路方向 y / m")
    ax.set_ylabel("埋深 h / m")
    ax.set_title(
        "高分区 y 宽度检查："
        f"span={stage3b['wide_y_high_score_span_m']:.2f} m, warning={stage3b['wide_y_high_score_zone_warning']}"
    )
    ax.legend(loc="best", fontsize=8)
    fig.colorbar(image, ax=ax, label="归一化扫描得分")
    fig.tight_layout()
    fig.savefig(output_path)
    plt.close(fig)
