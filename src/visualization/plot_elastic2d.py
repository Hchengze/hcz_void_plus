"""elastic2d validation 图件。"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from src.forward.elastic2d.das_response import build_elastic_das_response
from src.visualization.plot_style import setup_chinese_matplotlib


def _save(fig: plt.Figure, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(output_path)
    plt.close(fig)


def plot_elastic2d_rayleigh_wavefield_snapshots(result: dict[str, Any], output_path: Path) -> None:
    setup_chinese_matplotlib()
    elastic = result["elastic_result"]
    snapshots = elastic.wavefield_snapshots_vz
    n_snap = snapshots.shape[0]
    n_col = min(2, n_snap)
    n_row = int(np.ceil(n_snap / n_col))
    vmax = max(float(np.max(np.abs(snapshots))), 1.0e-12)
    fig, axes = plt.subplots(n_row, n_col, figsize=(4.2 * n_col, 3.2 * n_row), dpi=150)
    axes = np.atleast_1d(axes).ravel()
    for idx, ax in enumerate(axes):
        if idx >= n_snap:
            ax.axis("off")
            continue
        im = ax.imshow(snapshots[idx], cmap="seismic", vmin=-vmax, vmax=vmax, aspect="auto")
        ax.set_title(f"t={elastic.snapshot_times_s[idx]:.4f} s")
        ax.set_xlabel("x grid")
        ax.set_ylabel("z grid")
        fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    fig.suptitle("elastic2d_prototype vz 快照：局部物理验证，不是工业级 elastic", y=1.02)
    _save(fig, output_path)


def plot_elastic2d_surface_gather(result: dict[str, Any], output_path: Path) -> None:
    setup_chinese_matplotlib()
    elastic = result["elastic_result"]
    gather = elastic.surface_vz_gather
    vmax = max(float(np.max(np.abs(gather))), 1.0e-12)
    fig, ax = plt.subplots(figsize=(7.2, 4.6), dpi=150)
    im = ax.imshow(gather, cmap="seismic", aspect="auto", origin="lower", vmin=-vmax, vmax=vmax)
    ax.set_title("elastic2d surface receiver gather")
    ax.set_xlabel("receiver index")
    ax.set_ylabel("time sample")
    ax.text(
        0.02,
        0.98,
        f"CFL={elastic.cfl_info['cfl_number']:.3f}, stable={elastic.cfl_info['stable']}",
        transform=ax.transAxes,
        va="top",
        fontsize=8,
        bbox={"facecolor": "white", "alpha": 0.75, "edgecolor": "0.8"},
    )
    fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    _save(fig, output_path)


def plot_elastic2d_rayleigh_velocity_check(result: dict[str, Any], output_path: Path) -> None:
    setup_chinese_matplotlib()
    expected = result["expected_rayleigh_like_range_mps"]
    estimated = result["estimated_surface_velocity_mps"]
    fig, ax = plt.subplots(figsize=(6.4, 3.8), dpi=150)
    ax.axvspan(expected[0], expected[1], color="#74c476", alpha=0.3, label="0.85-0.98 Vs sanity range")
    ax.axvline(estimated, color="#e15759", linewidth=2.0, label="estimated")
    ax.set_yticks([])
    ax.set_xlabel("surface apparent velocity / (m/s)")
    ax.set_title("elastic2d Rayleigh-like 表面事件速度 sanity check")
    ax.legend()
    ax.grid(axis="x", alpha=0.25)
    _save(fig, output_path)


def plot_elastic2d_void_scattering_residual(result: dict[str, Any], output_path: Path) -> None:
    setup_chinese_matplotlib()
    residual = result["residual_gather"]
    vmax = max(float(np.max(np.abs(residual))), 1.0e-12)
    fig, ax = plt.subplots(figsize=(7.2, 4.6), dpi=150)
    im = ax.imshow(residual, cmap="seismic", aspect="auto", origin="lower", vmin=-vmax, vmax=vmax)
    ax.set_title("elastic2d void-like residual gather")
    ax.set_xlabel("receiver index")
    ax.set_ylabel("time sample")
    fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    _save(fig, output_path)


def plot_elastic2d_void_diffraction_overlay(result: dict[str, Any], output_path: Path) -> None:
    setup_chinese_matplotlib()
    residual = result["residual_envelope"]
    background = result["background_result"]
    vmax = max(float(np.max(np.abs(residual))), 1.0e-12)
    fig, ax = plt.subplots(figsize=(7.2, 4.6), dpi=150)
    ax.imshow(residual, cmap="magma", aspect="auto", origin="lower", vmin=0.0, vmax=vmax)
    dt = float(background.time_axis_s[1] - background.time_axis_s[0])
    curve_index = result["kinematic_curve_s"] / dt
    ax.plot(np.arange(len(curve_index)), curve_index, color="#00ffff", linewidth=1.5, label="local kinematic curve")
    ax.set_title("elastic residual envelope + kinematic diffraction curve")
    ax.set_xlabel("receiver index")
    ax.set_ylabel("time sample")
    ax.legend()
    _save(fig, output_path)


def plot_elastic2d_das_gauge_response(result: dict[str, Any], gauge_length_m: float, output_path: Path) -> None:
    setup_chinese_matplotlib()
    elastic = result["elastic_result"]
    das = build_elastic_das_response(
        elastic.surface_vx_gather,
        elastic.surface_vz_gather,
        elastic.grid.dx_m,
        gauge_length_m,
    )
    point = das["point_receiver_gather"]
    strain = das["gauge_length_strain_gather"]
    vmax_point = max(float(np.max(np.abs(point))), 1.0e-12)
    vmax_strain = max(float(np.max(np.abs(strain))), 1.0e-12)
    fig, axes = plt.subplots(1, 2, figsize=(10, 4.4), dpi=150, sharey=True)
    axes[0].imshow(point, cmap="seismic", aspect="auto", origin="lower", vmin=-vmax_point, vmax=vmax_point)
    axes[0].set_title("point receiver vz")
    axes[1].imshow(strain, cmap="seismic", aspect="auto", origin="lower", vmin=-vmax_strain, vmax=vmax_strain)
    axes[1].set_title("DAS-like gauge strain")
    for ax in axes:
        ax.set_xlabel("receiver index")
    axes[0].set_ylabel("time sample")
    fig.suptitle("elastic2d point receiver 与 gauge-length strain 对比", y=1.02)
    _save(fig, output_path)


def plot_elastic_vs_kinematic_overlay(result: dict[str, Any], output_path: Path) -> None:
    plot_elastic2d_void_diffraction_overlay(result, output_path)


def plot_elastic_vs_kinematic_residual_energy(result: dict[str, Any], output_path: Path) -> None:
    setup_chinese_matplotlib()
    fig, ax = plt.subplots(figsize=(5.8, 4.0), dpi=150)
    ax.bar([0], [result["curve_energy_ratio"]], color="#4e79a7")
    ax.set_xticks([0])
    ax.set_xticklabels(["curve-window residual energy ratio"])
    ax.set_ylim(0.0, 1.0)
    ax.set_ylabel("ratio")
    ax.set_title("elastic residual 能量沿 kinematic 曲线集中度")
    ax.grid(axis="y", alpha=0.25)
    _save(fig, output_path)
