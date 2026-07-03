"""几何 QC 绘图。"""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from src.geometry.road_geometry import road_boundary_xy


def plot_geometry(
    params: SimpleNamespace,
    receiver_xyz: np.ndarray,
    source_xyz: np.ndarray,
    scatter_xyz: np.ndarray,
    output_path: Path,
) -> None:
    """绘制道路、光纤、震源和散射点平面几何图。

    输出：
        geometry.png，显示 x-y 平面中的单侧 DAS-like 布设。

    限制：
        图中散射点是运动学等效点，不表示真实空洞边界网格。
    """

    boundary = road_boundary_xy(params)
    fig, ax = plt.subplots(figsize=(9, 4.5), dpi=150)
    ax.plot(boundary[:, 0], boundary[:, 1], color="0.25", linewidth=1.5, label="road boundary")
    ax.scatter(receiver_xyz[:, 0], receiver_xyz[:, 1], s=8, color="#1f77b4", label="DAS-like channels")
    ax.scatter(source_xyz[:, 0], source_xyz[:, 1], s=28, marker="^", color="#d62728", label="sources")
    ax.scatter(scatter_xyz[:, 0], scatter_xyz[:, 1], s=36, marker="x", color="#2ca02c", label="kinematic scatter points")
    ax.set_xlabel("x along road / fiber (m)")
    ax.set_ylabel("y across road (m)")
    ax.set_title("Geometry QC: kinematic approximation + DAS-like approximation")
    ax.set_aspect("equal", adjustable="box")
    ax.grid(True, alpha=0.25)
    ax.legend(loc="best", fontsize=8)
    fig.tight_layout()
    fig.savefig(output_path)
    plt.close(fig)
