"""Stage 5B 正演路线与 forward prototype 图件。"""

from __future__ import annotations

from pathlib import Path
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


def plot_forward_engine_comparison(result: dict[str, Any], output_path: Path) -> None:
    """绘制 F0/F1/F2 正演引擎摘要。

    acoustic2d 的指标只代表数值框架健康度，不和 DAS-like Rayleigh 运动学结果做
    物理等价比较。
    """

    setup_chinese_matplotlib()
    engines = result["engines"]
    names = ["kinematic_baseline", "layered_kinematic"]
    rms_values = [engines[name]["synthetic_rms"] for name in names]
    scatter_values = [engines[name]["scatter_rms"] for name in names]
    residual = result["layered_vs_baseline"]

    fig, axes = plt.subplots(2, 1, figsize=(8.6, 6.2), dpi=150)
    x = np.arange(len(names))
    axes[0].bar(x - 0.18, rms_values, width=0.36, label="synthetic RMS", color="#4e79a7")
    axes[0].bar(x + 0.18, scatter_values, width=0.36, label="scatter RMS", color="#f28e2b")
    axes[0].set_xticks(x)
    axes[0].set_xticklabels(["F0 baseline", "F1 layered"], rotation=0)
    axes[0].set_ylabel("RMS")
    axes[0].set_title("F0/F1 运动学正演炮集幅值摘要")
    axes[0].legend()
    axes[0].grid(axis="y", alpha=0.25)

    labels = ["mean", "RMS", "max abs"]
    values = [
        residual["travel_time_residual_mean_ms"],
        residual["travel_time_residual_rms_ms"],
        residual["travel_time_residual_max_abs_ms"],
    ]
    axes[1].bar(np.arange(3), values, color=["#59a14f", "#76b7b2", "#e15759"])
    axes[1].set_xticks(np.arange(3))
    axes[1].set_xticklabels(labels)
    axes[1].set_ylabel("layered - baseline / ms")
    axes[1].set_title("F1 相对 F0 的理论绕射走时差异")
    axes[1].grid(axis="y", alpha=0.25)
    axes[1].text(
        0.02,
        0.95,
        "active forward: layered_kinematic\nacoustic2d 仅作 validation，不参与主定位",
        transform=axes[1].transAxes,
        va="top",
        fontsize=8,
        bbox={"facecolor": "white", "alpha": 0.78, "edgecolor": "0.8"},
    )
    _save(fig, output_path)


def plot_layered_kinematic_vs_baseline_gather(result: dict[str, Any], output_path: Path) -> None:
    """绘制 F0 与 F1 第一炮炮集对比。"""

    setup_chinese_matplotlib()
    baseline = result["baseline_synthetic_data"][0]
    layered = result["layered_synthetic_data"][0]
    diff = layered - baseline
    vmax = max(float(np.max(np.abs(baseline))), float(np.max(np.abs(layered))), 1.0e-12)
    diff_vmax = max(float(np.max(np.abs(diff))), 1.0e-12)

    fig, axes = plt.subplots(1, 3, figsize=(11.5, 4.2), dpi=150, sharey=True)
    for ax, data, title, limit in [
        (axes[0], baseline, "F0 kinematic_baseline", vmax),
        (axes[1], layered, "F1 layered_kinematic", vmax),
        (axes[2], diff, "F1 - F0", diff_vmax),
    ]:
        im = ax.imshow(data, aspect="auto", cmap="seismic", vmin=-limit, vmax=limit, origin="lower")
        ax.set_title(title)
        ax.set_xlabel("channel")
        fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    axes[0].set_ylabel("time sample")
    fig.suptitle("分层/非均匀 velocity_model 对运动学炮集的影响", y=1.02)
    _save(fig, output_path)


def plot_forward_roadmap_status(result: dict[str, Any], output_path: Path) -> None:
    """绘制 F0-F6 forward roadmap 当前状态。"""

    setup_chinese_matplotlib()
    rows = result["roadmap_status"]
    fig, ax = plt.subplots(figsize=(10.5, 5.8), dpi=150)
    ax.axis("off")
    y_positions = np.linspace(0.92, 0.08, len(rows))
    color_by_status = {
        "implemented_baseline": "#9ecae1",
        "active_forward": "#74c476",
        "implemented_validation": "#fdae6b",
        "designed_next": "#bcbddc",
        "planned": "#d9d9d9",
        "long_term": "#d9d9d9",
        "planned_adapters": "#d9d9d9",
    }
    for y, row in zip(y_positions, rows):
        color = color_by_status.get(row["status"], "#d9d9d9")
        ax.add_patch(plt.Rectangle((0.02, y - 0.045), 0.16, 0.07, color=color, ec="0.35"))
        ax.text(0.10, y - 0.01, row["stage"], ha="center", va="center", fontsize=12, weight="bold")
        ax.text(0.22, y + 0.01, f"{row['name']}  |  {row['status']}", fontsize=10, weight="bold")
        ax.text(0.22, y - 0.025, row["role"], fontsize=9)
    ax.text(
        0.02,
        0.99,
        "Stage 5B forward roadmap：F1 是当前主线，F2 是 validation，F3 是下一步核心。",
        fontsize=11,
        weight="bold",
        va="top",
    )
    _save(fig, output_path)


def plot_acoustic2d_wavefield_snapshots(result: dict[str, Any], output_path: Path) -> None:
    """绘制 acoustic2d prototype 波场快照。"""

    setup_chinese_matplotlib()
    acoustic = result["acoustic2d_result"]
    snapshots = acoustic.wavefield_snapshots
    times = acoustic.snapshot_times_s
    n_snap = snapshots.shape[0]
    n_col = min(3, n_snap)
    n_row = int(np.ceil(n_snap / n_col))
    vmax = max(float(np.max(np.abs(snapshots))), 1.0e-12)
    fig, axes = plt.subplots(n_row, n_col, figsize=(3.4 * n_col, 2.8 * n_row), dpi=150)
    axes = np.atleast_1d(axes).ravel()
    for idx, ax in enumerate(axes):
        if idx >= n_snap:
            ax.axis("off")
            continue
        im = ax.imshow(snapshots[idx], cmap="seismic", vmin=-vmax, vmax=vmax, origin="upper", aspect="auto")
        ax.set_title(f"t={times[idx]:.4f} s")
        ax.set_xlabel("x grid")
        ax.set_ylabel("z grid")
        fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    fig.suptitle("acoustic2d_prototype 波场快照：声学框架验证，不代表 Rayleigh 波", y=1.02)
    _save(fig, output_path)


def plot_acoustic2d_shot_gather(result: dict[str, Any], output_path: Path) -> None:
    """绘制 acoustic2d prototype 接收炮集。"""

    setup_chinese_matplotlib()
    acoustic = result["acoustic2d_result"]
    gather = acoustic.shot_gather
    vmax = max(float(np.max(np.abs(gather))), 1.0e-12)
    fig, ax = plt.subplots(figsize=(7.2, 4.6), dpi=150)
    im = ax.imshow(gather, aspect="auto", cmap="seismic", vmin=-vmax, vmax=vmax, origin="lower")
    ax.set_xlabel("receiver index")
    ax.set_ylabel("time sample")
    ax.set_title("acoustic2d_prototype shot gather")
    ax.text(
        0.02,
        0.98,
        f"CFL={acoustic.cfl_info['cfl_number']:.3f}, stable={acoustic.cfl_info['stable']}\n不是 Rayleigh/free-surface/void scattering 正演",
        transform=ax.transAxes,
        va="top",
        fontsize=8,
        bbox={"facecolor": "white", "alpha": 0.78, "edgecolor": "0.8"},
    )
    fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    _save(fig, output_path)
