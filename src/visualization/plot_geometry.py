"""几何 QC 与几何自检绘图。"""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import numpy as np

from src.visualization.plot_style import setup_chinese_matplotlib


def _y_limits_for_layout(params: SimpleNamespace) -> tuple[float, float]:
    """给 x-y 平面图留出测线标注边距。"""

    margin_y = max(params.road.width_m * 0.10, 1.0)
    y_min = min(0.0, params.fiber.y_m, params.source.y_m) - margin_y
    y_max = max(params.road.width_m, params.fiber.y_m, params.source.y_m) + margin_y
    return y_min, y_max


def _draw_road_and_lines(ax, params: SimpleNamespace) -> None:
    """绘制道路区域、DAS 光纤测线和震源测线。"""

    road_patch = Rectangle(
        (0.0, 0.0),
        params.road.length_m,
        params.road.width_m,
        facecolor="#f2f2f2",
        edgecolor="0.25",
        linewidth=1.3,
        alpha=0.62,
        label=f"道路区域 0≤y≤W，W={params.road.width_m:.1f} m",
    )
    ax.add_patch(road_patch)
    ax.axhline(params.fiber.y_m, color="#1f77b4", linewidth=2.1, label=f"DAS 光纤测线 y={params.fiber.y_m:.1f} m")
    ax.axhline(params.source.y_m, color="#d62728", linewidth=1.9, linestyle="--", label=f"震源测线 y=W={params.source.y_m:.1f} m")


def plot_geometry(
    params: SimpleNamespace,
    receiver_xyz: np.ndarray,
    source_xyz: np.ndarray,
    scatter_xyz: np.ndarray,
    output_path: Path,
) -> None:
    """绘制道路、光纤、震源和异常体投影的 x-y 平面几何图。

    这张图用于常规几何 QC。异常体深度 h 不画在 y 轴上，只用文字说明；图中
    的散射点是运动学等效散射点在 x-y 平面的投影。
    """

    setup_chinese_matplotlib()
    y_min, y_max = _y_limits_for_layout(params)
    fig, ax = plt.subplots(figsize=(10, 4.8), dpi=150)
    _draw_road_and_lines(ax, params)
    ax.scatter(receiver_xyz[:, 0], receiver_xyz[:, 1], s=8, color="#1f77b4", alpha=0.8, label="DAS-like 通道")
    ax.scatter(source_xyz[:, 0], source_xyz[:, 1], s=28, marker="^", color="#d62728", label="炮点")
    ax.scatter([params.anomaly.x0_m], [params.anomaly.y0_m], s=70, marker="x", color="#2ca02c", linewidths=2.0, label="异常体平面投影")
    ax.scatter(scatter_xyz[:, 0], scatter_xyz[:, 1], s=34, marker="+", color="#006d2c", alpha=0.65, label="等效散射点投影")
    ax.text(
        params.anomaly.x0_m,
        params.anomaly.y0_m,
        f"  h={params.anomaly.depth_m:.1f} m",
        color="#2ca02c",
        fontsize=8,
        va="bottom",
    )
    ax.set_xlim(0.0, params.road.length_m)
    ax.set_ylim(y_min, y_max)
    ax.set_xlabel("沿道路 / 光纤方向 x / m")
    ax.set_ylabel("横穿道路方向 y / m")
    ax.set_title("几何 QC：道路 x-y 平面，深度 h 不作为 y 坐标")
    ax.grid(True, alpha=0.25)
    ax.legend(loc="upper right", fontsize=7, ncol=2)
    fig.tight_layout()
    fig.savefig(output_path)
    plt.close(fig)


def plot_geometry_layout_check(
    params: SimpleNamespace,
    receiver_xyz: np.ndarray,
    source_xyz: np.ndarray,
    scatter_xyz: np.ndarray,
    output_path: Path,
) -> None:
    """绘制道路-光纤-震源-异常体几何自检图。

    自检重点：
        光纤测线是否在 y=fiber_y_m；
        震源测线是否在 y=source_y_m；
        道路主体是否为 0<=y<=W；
        异常体是否以 x0-y0 投影显示，深度 h 只作为文字标注。
    """

    setup_chinese_matplotlib()
    y_min, y_max = _y_limits_for_layout(params)
    fig, ax = plt.subplots(figsize=(10, 4.8), dpi=150)
    _draw_road_and_lines(ax, params)
    ax.scatter(receiver_xyz[:, 0], receiver_xyz[:, 1], s=8, color="#1f77b4", alpha=0.8, label="DAS-like 通道")
    ax.scatter(source_xyz[:, 0], source_xyz[:, 1], s=32, marker="^", color="#d62728", label="全部炮点")
    selected = source_xyz[params.output.wavefield_shot_index]
    ax.scatter([selected[0]], [selected[1]], s=120, marker="*", color="#ff7f0e", edgecolors="black", linewidths=0.4, label="伪波场选中炮点")
    ax.scatter([params.anomaly.x0_m], [params.anomaly.y0_m], s=85, marker="x", color="#2ca02c", linewidths=2.0, label="异常体平面投影")
    ax.scatter(scatter_xyz[:, 0], scatter_xyz[:, 1], s=36, marker="+", color="#006d2c", alpha=0.65, label="等效散射点投影")
    ax.text(
        params.anomaly.x0_m,
        params.anomaly.y0_m,
        f"  异常体投影，h={params.anomaly.depth_m:.1f} m",
        color="#2ca02c",
        fontsize=8,
        va="bottom",
    )
    ax.set_xlim(0.0, params.road.length_m)
    ax.set_ylim(y_min, y_max)
    ax.set_xlabel("沿道路方向 x / m")
    ax.set_ylabel("横穿道路方向 y / m")
    ax.set_title("道路-光纤-震源-异常体几何自检图（x-y 平面，不是 x-depth 剖面）")
    ax.grid(True, alpha=0.25)
    ax.legend(loc="upper right", fontsize=7, ncol=2)
    fig.tight_layout()
    fig.savefig(output_path)
    plt.close(fig)
