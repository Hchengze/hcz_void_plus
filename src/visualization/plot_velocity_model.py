"""当前速度模型可视化。

这些图用于 Stage 5D 的人工审计：用户必须能直观看到当前 active velocity model
是不是 layered，以及 layered 与 uniform 在实际 source-scatter-receiver 路径上
会产生多大的走时差异。
"""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from src.model.velocity_model import UniformVelocityModel, build_velocity_model, compute_kinematic_travel_time
from src.visualization.plot_style import setup_chinese_matplotlib


def _save(fig: plt.Figure, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(output_path)
    plt.close(fig)


def _depth_velocity_profile(params: SimpleNamespace) -> tuple[np.ndarray, np.ndarray]:
    """生成分层速度阶梯曲线。"""

    depths = np.asarray([0.0, *params.velocity.layer_depths_m], dtype=float)
    velocities = np.asarray(params.velocity.layer_rayleigh_velocities_mps, dtype=float)
    z = []
    v = []
    for i, vel in enumerate(velocities):
        top = depths[i]
        bottom = depths[i + 1] if i + 1 < len(depths) else depths[-1] + 1.0
        z.extend([top, bottom])
        v.extend([vel, vel])
    return np.asarray(z), np.asarray(v)


def plot_velocity_model_profile_current(params: SimpleNamespace, output_path: Path) -> None:
    """绘制当前 layered velocity profile。"""

    setup_chinese_matplotlib()
    depth, velocity = _depth_velocity_profile(params)
    fig, ax = plt.subplots(figsize=(5.2, 5.0), dpi=150)
    ax.plot(velocity, depth, drawstyle="steps-post", linewidth=2.4, color="#4e79a7")
    ax.invert_yaxis()
    ax.set_xlabel("Rayleigh equivalent velocity / (m/s)")
    ax.set_ylabel("depth h / m")
    ax.set_title(f"当前速度模型 profile：{params.velocity.model_type}")
    for d in params.velocity.layer_depths_m:
        ax.axhline(d, color="0.7", linestyle="--", linewidth=0.8)
    ax.grid(alpha=0.25)
    _save(fig, output_path)


def plot_velocity_model_2d_slice_current(params: SimpleNamespace, output_path: Path) -> None:
    """绘制 x-z 速度切片。

    当前 layered 模型主要随深度变化；若以后启用 lateral_gradient 或 localized low velocity，
    同一函数仍可通过 velocity_at 显示横向变化。
    """

    setup_chinese_matplotlib()
    model = build_velocity_model(params)
    x = np.linspace(0.0, params.road.length_m, 120)
    z = np.linspace(0.0, max(params.scan.depth_max_m, max(params.velocity.layer_depths_m)), 80)
    xx, zz = np.meshgrid(x, z)
    yy = np.full_like(xx, 0.5 * params.road.width_m)
    xyz = np.stack([xx, yy, zz], axis=-1)
    velocity = model.velocity_at(xyz)
    fig, ax = plt.subplots(figsize=(7.0, 4.2), dpi=150)
    im = ax.imshow(
        velocity,
        extent=[x.min(), x.max(), z.max(), z.min()],
        aspect="auto",
        cmap="viridis",
    )
    ax.set_xlabel("x / m")
    ax.set_ylabel("depth h / m")
    ax.set_title(f"x-z 速度剖面：{params.velocity.model_type}")
    fig.colorbar(im, ax=ax, label="m/s")
    _save(fig, output_path)


def _sample_polyline(start: np.ndarray, mid: np.ndarray, end: np.ndarray, n_each: int = 40) -> np.ndarray:
    """沿 source-scatter-receiver 折线路径采样。"""

    a = np.linspace(0.0, 1.0, n_each, endpoint=False)[:, None]
    b = np.linspace(0.0, 1.0, n_each)[:, None]
    first = start[None, :] + a * (mid[None, :] - start[None, :])
    second = mid[None, :] + b * (end[None, :] - mid[None, :])
    return np.vstack([first, second])


def plot_velocity_sampling_paths_current(
    params: SimpleNamespace,
    source_xyz: np.ndarray,
    receiver_xyz: np.ndarray,
    scatter_xyz: np.ndarray,
    output_path: Path,
) -> dict[str, Any]:
    """显示典型 source-scatter-receiver 路径上的速度采样。"""

    setup_chinese_matplotlib()
    model = build_velocity_model(params)
    source = np.asarray(source_xyz[len(source_xyz) // 2], dtype=float)
    receiver = np.asarray(receiver_xyz[len(receiver_xyz) // 2], dtype=float)
    scatter = np.asarray(scatter_xyz[0], dtype=float)
    samples = _sample_polyline(source, scatter, receiver)
    velocity = model.velocity_at(samples)
    distance = np.concatenate([[0.0], np.cumsum(np.linalg.norm(np.diff(samples, axis=0), axis=1))])
    fig, axes = plt.subplots(1, 2, figsize=(10.0, 4.2), dpi=150)
    sc = axes[0].scatter(samples[:, 0], samples[:, 2], c=velocity, cmap="viridis", s=22)
    axes[0].invert_yaxis()
    axes[0].set_xlabel("x / m")
    axes[0].set_ylabel("depth h / m")
    axes[0].set_title("source-scatter-receiver 采样路径")
    fig.colorbar(sc, ax=axes[0], label="m/s")
    axes[1].plot(distance, velocity, color="#e15759", linewidth=2.0)
    axes[1].set_xlabel("path distance / m")
    axes[1].set_ylabel("sampled velocity / (m/s)")
    axes[1].set_title("路径采样速度")
    axes[1].grid(alpha=0.25)
    _save(fig, output_path)
    return {
        "sample_count": int(len(samples)),
        "velocity_min_mps": float(np.min(velocity)),
        "velocity_max_mps": float(np.max(velocity)),
        "velocity_mean_mps": float(np.mean(velocity)),
    }


def plot_uniform_vs_layered_travel_time_difference(
    params: SimpleNamespace,
    source_xyz: np.ndarray,
    receiver_xyz: np.ndarray,
    output_path: Path,
) -> dict[str, Any]:
    """绘制 uniform 与当前 active model 的直达走时差异。"""

    setup_chinese_matplotlib()
    active_model = build_velocity_model(params)
    uniform = UniformVelocityModel(params.velocity.rayleigh_velocity_mps)
    source = np.asarray(source_xyz, dtype=float)
    receiver = np.asarray(receiver_xyz, dtype=float)
    active_t = compute_kinematic_travel_time(source[:, None, :], receiver[None, :, :], active_model)
    uniform_t = compute_kinematic_travel_time(source[:, None, :], receiver[None, :, :], uniform)
    diff_ms = 1000.0 * (active_t - uniform_t)
    fig, ax = plt.subplots(figsize=(7.2, 4.4), dpi=150)
    im = ax.imshow(diff_ms, aspect="auto", cmap="coolwarm")
    ax.set_xlabel("receiver index")
    ax.set_ylabel("shot index")
    ax.set_title("uniform vs active velocity model 直达走时差异 / ms")
    fig.colorbar(im, ax=ax, label="ms")
    _save(fig, output_path)
    return {
        "direct_diff_mean_ms": float(np.mean(diff_ms)),
        "direct_diff_rms_ms": float(np.sqrt(np.mean(diff_ms**2))),
        "direct_diff_max_abs_ms": float(np.max(np.abs(diff_ms))),
    }


def plot_velocity_model_active_badge(params: SimpleNamespace, audit: dict[str, Any], output_path: Path) -> None:
    """用醒目的单页图件标明当前 active velocity model。"""

    setup_chinese_matplotlib()
    fig, ax = plt.subplots(figsize=(6.2, 3.8), dpi=150)
    ax.axis("off")
    is_layered = audit.get("is_layered_default")
    color = "#59a14f" if is_layered else "#e15759"
    ax.text(
        0.5,
        0.68,
        f"当前 active velocity model\n{params.velocity.model_type}",
        ha="center",
        va="center",
        fontsize=18,
        fontweight="bold",
        color=color,
    )
    ax.text(
        0.5,
        0.35,
        "layered_kinematic 使用 Rayleigh equivalent velocity\n"
        "elastic2d 使用独立 Vp/Vs/rho validation 参数",
        ha="center",
        va="center",
        fontsize=10,
    )
    ax.text(
        0.5,
        0.12,
        f"direct={audit['velocity_model_used_by_direct']}  "
        f"scatter={audit['velocity_model_used_by_scatter']}  "
        f"scan={audit['velocity_model_used_by_scan']}",
        ha="center",
        va="center",
        fontsize=9,
    )
    _save(fig, output_path)
