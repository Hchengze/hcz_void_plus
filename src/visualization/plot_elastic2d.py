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


def plot_elastic2d_rayleigh_pick_diagnostics(result: dict[str, Any], output_path: Path) -> None:
    """绘制 Rayleigh-like 拾取点和速度窗。"""

    setup_chinese_matplotlib()
    elastic = result["elastic_result"]
    gather = np.abs(elastic.surface_vz_gather)
    vmax = max(float(np.max(gather)), 1.0e-12)
    fig, ax = plt.subplots(figsize=(7.2, 4.6), dpi=150)
    ax.imshow(gather, cmap="magma", aspect="auto", origin="lower", vmin=0.0, vmax=vmax)
    dt = float(elastic.time_axis_s[1] - elastic.time_axis_s[0])
    offsets = np.asarray(result.get("pick_offset_m", []), dtype=float)
    times = np.asarray(result.get("pick_time_s", []), dtype=float)
    if offsets.size and times.size:
        receiver_index = np.linspace(0, gather.shape[1] - 1, offsets.size)
        ax.scatter(receiver_index, times / dt, s=18, color="#00ffff", label="picked ridge")
    ax.set_title(f"Rayleigh-like pick diagnostics: {result.get('rayleigh_pick_interpretation', '')}")
    ax.set_xlabel("receiver index")
    ax.set_ylabel("time sample")
    ax.legend(loc="upper right")
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


def plot_elastic2d_void_parameter_sensitivity(result: dict[str, Any], output_path: Path) -> None:
    """绘制 void 参数敏感性柱状图。"""

    setup_chinese_matplotlib()
    names = list(result["cases"].keys())
    values = [result["cases"][name]["relative_residual_energy"] for name in names]
    fig, ax = plt.subplots(figsize=(10.0, 4.6), dpi=150)
    ax.bar(np.arange(len(names)), values, color="#4e79a7")
    ax.set_xticks(np.arange(len(names)))
    ax.set_xticklabels(names, rotation=60, ha="right", fontsize=7)
    ax.set_ylabel("relative residual energy")
    ax.set_title(f"void parameter sensitivity, best={result['best_case']}")
    ax.grid(axis="y", alpha=0.25)
    _save(fig, output_path)


def plot_elastic2d_void_residual_energy_map(result: dict[str, Any], output_path: Path) -> None:
    """按 source_type / radius-vs_factor 展示 residual energy。"""

    setup_chinese_matplotlib()
    fig, axes = plt.subplots(1, 2, figsize=(9.5, 4.2), dpi=150, sharey=True)
    for ax, source_type in zip(axes, ["vertical_force", "horizontal_force"]):
        subset = [item for item in result["cases"].values() if item["source_type"] == source_type]
        radii = sorted({item["void_radius_m"] for item in subset})
        factors = sorted({item["void_vs_factor"] for item in subset})
        grid = np.zeros((len(radii), len(factors)), dtype=float)
        for item in subset:
            i = radii.index(item["void_radius_m"])
            j = factors.index(item["void_vs_factor"])
            grid[i, j] = item["relative_residual_energy"]
        im = ax.imshow(grid, origin="lower", aspect="auto", cmap="viridis")
        ax.set_title(source_type)
        ax.set_xticks(np.arange(len(factors)))
        ax.set_xticklabels([str(v) for v in factors])
        ax.set_yticks(np.arange(len(radii)))
        ax.set_yticklabels([str(v) for v in radii])
        ax.set_xlabel("void_vs_factor")
        ax.set_ylabel("void_radius_m")
        fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    _save(fig, output_path)


def plot_elastic2d_das_component_comparison(result: dict[str, Any], output_path: Path) -> None:
    """比较 vx/vz/gauge strain RMS。"""

    setup_chinese_matplotlib()
    labels = []
    vx = []
    vz = []
    strain = []
    for name, item in result["source_cases"].items():
        labels.append(name)
        vx.append(item["vx_rms"])
        vz.append(item["vz_rms"])
        strain.append(item["gauge_strain_rms"])
    x = np.arange(len(labels))
    fig, ax = plt.subplots(figsize=(7.2, 4.2), dpi=150)
    ax.bar(x - 0.24, vx, width=0.24, label="vx")
    ax.bar(x, vz, width=0.24, label="vz")
    ax.bar(x + 0.24, strain, width=0.24, label="gauge strain x")
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_yscale("symlog", linthresh=1.0e-14)
    ax.set_ylabel("RMS")
    ax.set_title("elastic2d DAS-like component response")
    ax.legend()
    ax.grid(axis="y", alpha=0.25)
    _save(fig, output_path)


def plot_elastic2d_das_gauge_length_sensitivity(result: dict[str, Any], output_path: Path) -> None:
    """绘制 gauge length 对 strain RMS 的影响。"""

    setup_chinese_matplotlib()
    items = list(result["gauge_length_cases"].values())
    lengths = [item["gauge_length_m"] for item in items]
    values = [item["gauge_strain_rms"] for item in items]
    fig, ax = plt.subplots(figsize=(6.0, 4.0), dpi=150)
    ax.plot(lengths, values, marker="o", linewidth=2.0)
    ax.set_xlabel("gauge length / m")
    ax.set_ylabel("gauge strain RMS")
    ax.set_title(f"gauge length sensitivity, best={result['best_gauge_length_m']} m")
    ax.grid(alpha=0.25)
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


def plot_elastic_vs_kinematic_energy_partition(result: dict[str, Any], output_path: Path) -> None:
    """绘制 residual 能量近曲线/离曲线分区。"""

    setup_chinese_matplotlib()
    values = [
        result["residual_energy_near_kinematic_curve_ratio"],
        result["residual_energy_off_curve_ratio"],
        result["kinematic_curve_explained_fraction"],
        result["elastic_extra_event_fraction"],
    ]
    labels = ["near curve", "off curve", "best shift explained", "extra events"]
    fig, ax = plt.subplots(figsize=(7.2, 4.2), dpi=150)
    ax.bar(labels, values, color=["#59a14f", "#e15759", "#4e79a7", "#f28e2b"])
    ax.set_ylim(0.0, 1.0)
    ax.set_ylabel("energy fraction")
    ax.set_title(f"elastic vs kinematic energy partition, shift={result['best_time_shift_ms']:.2f} ms")
    ax.grid(axis="y", alpha=0.25)
    _save(fig, output_path)
