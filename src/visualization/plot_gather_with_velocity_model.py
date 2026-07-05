"""带速度模型上下文的炮集图。"""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from src.model.velocity_model import (
    KinematicVelocityModel,
    UniformVelocityModel,
    compute_kinematic_travel_time,
    compute_scatter_travel_time,
)
from src.visualization.plot_style import setup_chinese_matplotlib


def _save(fig: plt.Figure, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(output_path)
    plt.close(fig)


def _gather_extent(params: SimpleNamespace) -> list[float]:
    return [
        float(params.derived.channel_x[0]),
        float(params.derived.channel_x[-1]),
        float(params.derived.time_axis[-1]),
        float(params.derived.time_axis[0]),
    ]


def _arrival_curves(
    params: SimpleNamespace,
    source_xyz: np.ndarray,
    receiver_xyz: np.ndarray,
    scatter_xyz: np.ndarray,
    velocity_model: KinematicVelocityModel,
    shot_index: int,
) -> dict[str, np.ndarray]:
    """计算 direct/scatter 理论到时曲线，全部来自 velocity_model 路径积分接口。"""

    shot = np.asarray(source_xyz[shot_index : shot_index + 1], dtype=float)
    direct = params.time.t0_s + compute_kinematic_travel_time(shot[:, None, :], receiver_xyz[None, :, :], velocity_model)[0]
    scatter = params.time.t0_s + compute_scatter_travel_time(
        shot,
        np.asarray(scatter_xyz[:1], dtype=float),
        receiver_xyz,
        velocity_model,
    )[0, 0]
    return {"direct": direct, "scatter": scatter}


def _plot_gather_background(ax, params: SimpleNamespace, gather: np.ndarray) -> None:
    clip = float(np.percentile(np.abs(gather), 99.0)) or 1.0
    ax.imshow(
        gather,
        aspect="auto",
        cmap="seismic",
        vmin=-clip,
        vmax=clip,
        extent=_gather_extent(params),
    )
    ax.set_xlabel("通道位置 x / m")
    ax.set_ylabel("时间 / s")


def plot_shot_gather_with_velocity_model(
    params: SimpleNamespace,
    data: np.ndarray,
    shot_index: int,
    source_xyz: np.ndarray,
    receiver_xyz: np.ndarray,
    scatter_xyz: np.ndarray,
    velocity_model: KinematicVelocityModel,
    output_path: Path,
) -> dict[str, Any]:
    """绘制 active velocity model 炮集，并叠加 direct/scatter 到时曲线。"""

    setup_chinese_matplotlib()
    gather = data[shot_index]
    active = _arrival_curves(params, source_xyz, receiver_xyz, scatter_xyz, velocity_model, shot_index)
    x = params.derived.channel_x
    fig, ax = plt.subplots(figsize=(8.4, 5.2), dpi=150)
    _plot_gather_background(ax, params, gather)
    ax.plot(x, active["direct"], color="#ffd166", linewidth=2.0, label="direct 到时：active layered path integration")
    ax.plot(x, active["scatter"], color="#06d6a0", linewidth=2.0, label="scatter 到时：source-scatter-receiver")
    ax.set_title("炮集 + active velocity model 上下文（layered，路径积分）")
    ax.legend(loc="upper right", fontsize=8)
    fig.colorbar(ax.images[0], ax=ax, label="相对振幅")
    _save(fig, output_path)
    return {
        "shot_gather_velocity_overlay_available": True,
        "active_velocity_model": params.velocity.model_type,
        "direct_curve_uses_path_integration": True,
        "scatter_curve_uses_path_integration": True,
    }


def plot_shot_gather_uniform_vs_layered_overlay(
    params: SimpleNamespace,
    data: np.ndarray,
    shot_index: int,
    source_xyz: np.ndarray,
    receiver_xyz: np.ndarray,
    scatter_xyz: np.ndarray,
    velocity_model: KinematicVelocityModel,
    output_path: Path,
) -> dict[str, float]:
    """叠加 uniform 与 active layered 到时，显示速度模型差异。"""

    setup_chinese_matplotlib()
    gather = data[shot_index]
    active = _arrival_curves(params, source_xyz, receiver_xyz, scatter_xyz, velocity_model, shot_index)
    uniform_model = UniformVelocityModel(params.velocity.rayleigh_velocity_mps)
    uniform = _arrival_curves(params, source_xyz, receiver_xyz, scatter_xyz, uniform_model, shot_index)
    x = params.derived.channel_x
    direct_diff_ms = 1000.0 * (active["direct"] - uniform["direct"])
    scatter_diff_ms = 1000.0 * (active["scatter"] - uniform["scatter"])

    fig, axes = plt.subplots(1, 2, figsize=(12.0, 4.8), dpi=150)
    _plot_gather_background(axes[0], params, gather)
    axes[0].plot(x, active["scatter"], color="#06d6a0", linewidth=2.0, label="layered scatter")
    axes[0].plot(x, uniform["scatter"], color="#ef476f", linewidth=1.5, linestyle="--", label="uniform scatter")
    axes[0].plot(x, active["direct"], color="#ffd166", linewidth=1.5, label="layered direct")
    axes[0].plot(x, uniform["direct"], color="white", linewidth=1.0, linestyle=":", label="uniform direct")
    axes[0].set_title("uniform vs layered 到时叠加")
    axes[0].legend(fontsize=7)

    axes[1].plot(x, direct_diff_ms, label="direct 差异", color="#4e79a7")
    axes[1].plot(x, scatter_diff_ms, label="scatter 差异", color="#e15759")
    axes[1].axhline(0.0, color="0.45", linewidth=0.8)
    axes[1].set_xlabel("通道位置 x / m")
    axes[1].set_ylabel("layered - uniform / ms")
    axes[1].set_title("速度模型路径积分导致的到时差异")
    axes[1].grid(alpha=0.25)
    axes[1].legend()
    _save(fig, output_path)
    return {
        "direct_uniform_vs_layered_rms_ms": float(np.sqrt(np.mean(direct_diff_ms**2))),
        "scatter_uniform_vs_layered_rms_ms": float(np.sqrt(np.mean(scatter_diff_ms**2))),
        "scatter_uniform_vs_layered_max_abs_ms": float(np.max(np.abs(scatter_diff_ms))),
    }


def plot_shot_gather_attenuation_comparison(
    params: SimpleNamespace,
    attenuated_data: np.ndarray,
    no_attenuation_data: np.ndarray | None,
    shot_index: int,
    output_path: Path,
) -> dict[str, float | bool]:
    """绘制 attenuation 启用前后的炮集差异。"""

    setup_chinese_matplotlib()
    if no_attenuation_data is None:
        no_attenuation_data = attenuated_data.copy()
    attenuated = attenuated_data[shot_index]
    reference = no_attenuation_data[shot_index]
    diff = attenuated - reference
    clip = float(np.percentile(np.abs(reference), 99.0)) or 1.0
    diff_clip = float(np.percentile(np.abs(diff), 99.0)) or 1.0
    rms_diff = float(np.sqrt(np.mean(diff * diff)))
    ref_rms = float(np.sqrt(np.mean(reference * reference)))

    fig, axes = plt.subplots(1, 3, figsize=(13.5, 4.4), dpi=150)
    for ax, gather, title, cmap, vmax in [
        (axes[0], reference, "未启用 Q attenuation", "seismic", clip),
        (axes[1], attenuated, "启用 Q attenuation", "seismic", clip),
        (axes[2], diff, "差异：attenuated - reference", "coolwarm", diff_clip),
    ]:
        im = ax.imshow(gather, aspect="auto", cmap=cmap, vmin=-vmax, vmax=vmax, extent=_gather_extent(params))
        ax.set_title(title)
        ax.set_xlabel("通道位置 x / m")
        ax.set_ylabel("时间 / s")
        fig.colorbar(im, ax=ax, shrink=0.78)
    fig.suptitle(f"路径相关 Q attenuation 对炮集振幅的影响，RMS 差异={rms_diff:.3e}")
    _save(fig, output_path)
    return {
        "attenuation_comparison_available": True,
        "shot_gather_attenuation_rms_difference": rms_diff,
        "shot_gather_attenuation_relative_rms_difference": float(rms_diff / max(ref_rms, 1.0e-12)),
    }
