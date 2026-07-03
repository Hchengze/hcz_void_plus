"""Rayleigh 波物理自检图件。

这些图件用于解释当前运动学近似的物理边界：Rayleigh 波主要沿地表传播并随
深度衰减；异常体等效散射点只用于走时和局部能量属性；路径剖面和走时曲线
不是弹性波方程射线追踪或真实全波场。
"""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from src.features.direct_arrival import predict_direct_arrival_times
from src.localization.travel_time import compute_candidate_diffraction_times
from src.model.velocity_model import UniformVelocityModel
from src.physics.rayleigh import estimate_penetration_depth, rayleigh_depth_weight
from src.visualization.plot_style import setup_chinese_matplotlib


def plot_source_anomaly_receiver_path_section(
    params: SimpleNamespace,
    source_xyz: np.ndarray,
    receiver_xyz: np.ndarray,
    output_path: Path,
) -> None:
    """绘制 source-anomaly-receiver 等效散射路径 x-z 剖面示意。

    物理意义：
        这张图只展示选中震源、异常体和一个代表性接收通道在 x-z 投影中的
        几何关系，说明异常体深度如何进入三维路径距离。

    限制：
        这不是严格射线路径，也不是弹性波场模拟；真实 Rayleigh 波绕射/散射
        机制远比这条折线复杂。
    """

    setup_chinese_matplotlib()
    shot = source_xyz[params.output.wavefield_shot_index]
    receiver_index = int(np.argmin(np.abs(receiver_xyz[:, 0] - params.anomaly.x0_m)))
    receiver = receiver_xyz[receiver_index]
    anomaly = np.array([params.anomaly.x0_m, params.anomaly.y0_m, params.anomaly.depth_m], dtype=float)

    fig, ax = plt.subplots(figsize=(8.5, 4.8), dpi=150)
    ax.axhline(0.0, color="0.2", linewidth=1.5, label="地表 z=0")
    ax.plot([shot[0], anomaly[0], receiver[0]], [shot[2], anomaly[2], receiver[2]], color="#9467bd", linewidth=1.8, label="等效散射路径投影")
    ax.scatter([shot[0]], [shot[2]], marker="^", s=70, color="#d62728", label="选中震源")
    ax.scatter([receiver[0]], [receiver[2]], marker="o", s=45, color="#1f77b4", label="代表性 DAS 通道")
    ax.scatter([anomaly[0]], [anomaly[2]], marker="x", s=85, color="#2ca02c", linewidths=2.0, label="异常体中心")
    ax.text(anomaly[0], anomaly[2], f"  y={anomaly[1]:.1f} m, h={anomaly[2]:.1f} m", color="#2ca02c", fontsize=8)
    x_min = min(shot[0], receiver[0], anomaly[0]) - 8.0
    x_max = max(shot[0], receiver[0], anomaly[0]) + 8.0
    ax.set_xlim(x_min, x_max)
    ax.set_ylim(max(params.scan.depth_max_m, params.anomaly.depth_m + 2.0), -0.5)
    ax.set_xlabel("沿道路方向 x / m")
    ax.set_ylabel("深度 z / m（向下为正）")
    ax.set_title("等效散射路径剖面示意（不是真实射线路径或弹性波场）")
    ax.grid(True, alpha=0.25)
    ax.legend(loc="best", fontsize=8)
    fig.tight_layout()
    fig.savefig(output_path)
    plt.close(fig)


def plot_rayleigh_depth_sensitivity(params: SimpleNamespace, output_path: Path) -> None:
    """绘制 Rayleigh 波简化深度敏感性曲线。"""

    setup_chinese_matplotlib()
    penetration_depth_m = estimate_penetration_depth(params)
    max_depth = max(params.scan.depth_max_m, params.anomaly.depth_m * 1.8)
    depth = np.linspace(0.0, max_depth, 240)
    weight = rayleigh_depth_weight(depth, penetration_depth_m)
    anomaly_weight = float(rayleigh_depth_weight(params.anomaly.depth_m, penetration_depth_m))

    fig, ax = plt.subplots(figsize=(5.6, 5.2), dpi=150)
    ax.plot(weight, depth, color="#2ca02c", linewidth=2.0, label="exp(-h / penetration_depth)")
    ax.scatter([anomaly_weight], [params.anomaly.depth_m], marker="x", s=75, color="#d62728", label="当前异常体深度")
    ax.axhline(params.anomaly.depth_m, color="#d62728", linestyle="--", linewidth=1.0, alpha=0.7)
    ax.set_ylim(max_depth, 0.0)
    ax.set_xlim(0.0, 1.05)
    ax.set_xlabel("相对敏感性 / 深度衰减系数")
    ax.set_ylabel("深度 h / m（向下为正）")
    ax.set_title("Rayleigh 波深度敏感性近似示意")
    ax.text(0.04, max_depth * 0.92, f"估计波长={params.derived.estimated_wavelength_m:.2f} m\n穿透深度={penetration_depth_m:.2f} m", fontsize=8)
    ax.grid(True, alpha=0.25)
    ax.legend(loc="best", fontsize=8)
    fig.tight_layout()
    fig.savefig(output_path)
    plt.close(fig)


def plot_diffraction_travel_time_curves(
    params: SimpleNamespace,
    data: np.ndarray,
    source_xyz: np.ndarray,
    receiver_xyz: np.ndarray,
    velocity_model: UniformVelocityModel,
    best_location: dict[str, float] | None,
    output_path: Path,
) -> None:
    """绘制炮集与理论绕射走时曲线自检图。

    物理意义：
        Rayleigh-wave diffraction 类方法更关注直达面波压制后，残余能量是否沿
        理论绕射走时曲线聚焦。该图比 x-y 地表响应示意更适合检查扫描物理。
    """

    setup_chinese_matplotlib()
    shot_index = params.output.wavefield_shot_index
    gather = data[shot_index, :, :]
    clip = np.percentile(np.abs(gather), 99.0)
    if clip == 0:
        clip = 1.0

    direct_times = predict_direct_arrival_times(params, source_xyz, receiver_xyz, velocity_model)[shot_index]
    truth_candidate = np.array([params.anomaly.x0_m, params.anomaly.y0_m, params.anomaly.depth_m], dtype=float)
    truth_times = compute_candidate_diffraction_times(
        truth_candidate, source_xyz, receiver_xyz, velocity_model, t0_s=params.time.t0_s
    )[shot_index]

    best_times = None
    if best_location is not None:
        best_candidate = np.array([best_location["x_m"], best_location["y_m"], best_location["depth_m"]], dtype=float)
        best_times = compute_candidate_diffraction_times(
            best_candidate, source_xyz, receiver_xyz, velocity_model, t0_s=params.time.t0_s
        )[shot_index]

    fig, ax = plt.subplots(figsize=(8.8, 5.2), dpi=150)
    extent = [
        float(params.derived.channel_x[0]),
        float(params.derived.channel_x[-1]),
        float(params.derived.time_axis[-1]),
        float(params.derived.time_axis[0]),
    ]
    image = ax.imshow(gather, aspect="auto", cmap="seismic", vmin=-clip, vmax=clip, extent=extent)
    ax.plot(params.derived.channel_x, direct_times, color="#111111", linewidth=1.2, label="直达波走时")
    ax.plot(params.derived.channel_x, truth_times, color="#2ca02c", linewidth=1.8, label="真值绕射曲线")
    if best_times is not None:
        ax.plot(params.derived.channel_x, best_times, color="#ff7f0e", linestyle="--", linewidth=1.8, label="最佳点绕射曲线")
    ax.set_xlabel("通道位置 x / m")
    ax.set_ylabel("时间 / s")
    ax.set_title("绕射走时曲线自检：炮集上的理论直达波与绕射事件")
    ax.legend(loc="best", fontsize=8)
    fig.colorbar(image, ax=ax, label="相对振幅")
    fig.tight_layout()
    fig.savefig(output_path)
    plt.close(fig)
