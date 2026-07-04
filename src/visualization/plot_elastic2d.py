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


def plot_stage5e_status_badge(summary: dict[str, Any], output_path: Path) -> None:
    """绘制 Stage 5E 当前状态徽章图。"""

    setup_chinese_matplotlib()
    fig, ax = plt.subplots(figsize=(7.0, 4.0), dpi=150)
    ax.axis("off")
    rayleigh = summary.get("rayleigh_like_event_detected")
    gauge = summary.get("das_gauge_nonzero_status")
    ready = summary.get("elastic2d_ready_for_2p5d")
    ax.text(0.5, 0.78, "Stage 5E Status", ha="center", va="center", fontsize=20, fontweight="bold")
    ax.text(
        0.5,
        0.52,
        "active forward: layered_kinematic\n"
        "elastic2d: validation prototype\n"
        f"Rayleigh-like detected: {rayleigh}\n"
        f"DAS gauge status: {gauge}\n"
        f"ready for 2.5D: {ready}",
        ha="center",
        va="center",
        fontsize=12,
    )
    ax.text(
        0.5,
        0.12,
        "未通过 Rayleigh/free-surface 基础验证前，不建议进入 2.5D 或局部 3D elastic。",
        ha="center",
        va="center",
        fontsize=10,
        color="#e15759",
    )
    _save(fig, output_path)


def plot_elastic2d_numerical_sensitivity_summary(result: dict[str, Any], output_path: Path) -> None:
    """绘制 elastic2d 数值敏感性汇总。"""

    setup_chinese_matplotlib()
    names = list(result["cases"].keys())
    velocities = [result["cases"][name]["estimated_surface_velocity_mps"] for name in names]
    detected = [result["cases"][name]["rayleigh_like_event_detected"] for name in names]
    fig, ax = plt.subplots(figsize=(10.5, 4.8), dpi=150)
    colors = ["#59a14f" if flag else "#e15759" for flag in detected]
    ax.bar(np.arange(len(names)), velocities, color=colors)
    best = result["best_case_metrics"]
    lo, hi = best["expected_rayleigh_like_range_mps"]
    ax.axhspan(lo, hi, color="#59a14f", alpha=0.15, label="expected Rayleigh-like range")
    ax.set_xticks(np.arange(len(names)))
    ax.set_xticklabels(names, rotation=35, ha="right", fontsize=8)
    ax.set_ylabel("estimated surface velocity / (m/s)")
    ax.set_title(f"elastic2d numerical sensitivity, best={result['best_case']}")
    ax.legend()
    ax.grid(axis="y", alpha=0.25)
    _save(fig, output_path)


def plot_elastic2d_rayleigh_pick_case_comparison(result: dict[str, Any], output_path: Path) -> None:
    """比较各 case 的 body leakage 与 boundary reflection。"""

    setup_chinese_matplotlib()
    names = list(result["cases"].keys())
    body = [result["cases"][name]["body_wave_leakage_indicator"] for name in names]
    boundary = [result["cases"][name]["boundary_reflection_indicator"] for name in names]
    x = np.arange(len(names))
    fig, ax = plt.subplots(figsize=(10.5, 4.6), dpi=150)
    ax.plot(x, body, marker="o", label="body/near-source leakage")
    ax.plot(x, boundary, marker="s", label="late boundary/coda")
    ax.set_xticks(x)
    ax.set_xticklabels(names, rotation=35, ha="right", fontsize=8)
    ax.set_ylim(0.0, 1.0)
    ax.set_ylabel("energy ratio")
    ax.set_title("Rayleigh pick case diagnostics")
    ax.legend()
    ax.grid(alpha=0.25)
    _save(fig, output_path)


def plot_elastic2d_das_response_nonzero_check(result: dict[str, Any], output_path: Path) -> None:
    """绘制 DAS-like gauge 非零检查。"""

    setup_chinese_matplotlib()
    names = list(result["cases"].keys())
    velocity = [result["cases"][name]["velocity_gauge_strain_rms"] for name in names]
    displacement = [result["cases"][name]["displacement_gauge_strain_rms"] for name in names]
    x = np.arange(len(names))
    fig, ax = plt.subplots(figsize=(10.5, 4.6), dpi=150)
    ax.plot(x, velocity, marker="o", label="velocity gauge strain")
    ax.plot(x, displacement, marker="s", label="ux-like gauge strain")
    ax.set_yscale("symlog", linthresh=1.0e-20)
    ax.set_xticks(x)
    ax.set_xticklabels(names, rotation=35, ha="right", fontsize=8)
    ax.set_ylabel("RMS")
    ax.set_title(f"DAS-like gauge nonzero check: {result['das_gauge_nonzero_status']}")
    ax.legend()
    ax.grid(alpha=0.25)
    _save(fig, output_path)


def plot_elastic2d_das_force_direction_comparison(result: dict[str, Any], output_path: Path) -> None:
    """按 source direction 汇总 DAS-like gauge 响应。"""

    setup_chinese_matplotlib()
    grouped: dict[str, float] = {}
    for item in result["cases"].values():
        grouped[item["source_type"]] = max(
            grouped.get(item["source_type"], 0.0),
            item["velocity_gauge_strain_rms"],
            item["displacement_gauge_strain_rms"],
        )
    fig, ax = plt.subplots(figsize=(6.4, 4.0), dpi=150)
    ax.bar(list(grouped.keys()), list(grouped.values()), color=["#4e79a7", "#f28e2b"])
    ax.set_yscale("symlog", linthresh=1.0e-20)
    ax.set_ylabel("best gauge RMS")
    ax.set_title("DAS-like force direction comparison")
    ax.grid(axis="y", alpha=0.25)
    _save(fig, output_path)


def plot_stage5f_status_badge(summary: dict[str, Any], output_path: Path) -> None:
    """绘制 Stage 5F 状态图。"""

    setup_chinese_matplotlib()
    fig, ax = plt.subplots(figsize=(7.2, 4.0), dpi=150)
    ax.axis("off")
    ax.text(0.5, 0.8, "Stage 5F 当前状态", ha="center", va="center", fontsize=20, fontweight="bold")
    ax.text(
        0.5,
        0.5,
        "主定位 forward：layered_kinematic\n"
        "elastic2d：validation forward\n"
        f"Rayleigh benchmark：{summary.get('rayleigh_like_event_detected')}\n"
        f"DAS gauge：{summary.get('das_gauge_final_status')}\n"
        f"ready_for_2p5d：{summary.get('ready_for_2p5d')}",
        ha="center",
        va="center",
        fontsize=12,
    )
    ax.text(0.5, 0.12, "2D elastic 服务三维 DAS-like 场景，不替代 x-y-depth 定位。", ha="center", color="#e15759")
    _save(fig, output_path)


def plot_elastic2d_rayleigh_benchmark_matrix(result: dict[str, Any], output_path: Path) -> None:
    """绘制 Rayleigh benchmark case 矩阵。"""

    setup_chinese_matplotlib()
    names = list(result["cases"].keys())
    values = [result["cases"][name]["estimated_surface_velocity_mps"] for name in names]
    detected = [result["cases"][name]["rayleigh_like_event_detected"] for name in names]
    fig, ax = plt.subplots(figsize=(10.5, 4.8), dpi=150)
    colors = ["#59a14f" if flag else "#e15759" for flag in detected]
    ax.bar(np.arange(len(names)), values, color=colors)
    expected = result["best_case_metrics"]["expected_rayleigh_like_range_mps"]
    ax.axhspan(expected[0], expected[1], color="#59a14f", alpha=0.15, label="期望 Rayleigh-like 区间")
    ax.set_xticks(np.arange(len(names)))
    ax.set_xticklabels(names, rotation=35, ha="right", fontsize=8)
    ax.set_ylabel("表面事件速度 / (m/s)")
    ax.set_title(f"elastic2d Rayleigh benchmark 矩阵，最佳={result['best_case']}")
    ax.legend()
    ax.grid(axis="y", alpha=0.25)
    _save(fig, output_path)


def plot_elastic2d_rayleigh_velocity_error(result: dict[str, Any], output_path: Path) -> None:
    """绘制各 case Rayleigh-like 速度相对误差。"""

    setup_chinese_matplotlib()
    names = list(result["cases"].keys())
    values = [result["cases"][name]["rayleigh_velocity_relative_error"] for name in names]
    fig, ax = plt.subplots(figsize=(10.5, 4.4), dpi=150)
    ax.bar(np.arange(len(names)), values, color="#4e79a7")
    ax.set_xticks(np.arange(len(names)))
    ax.set_xticklabels(names, rotation=35, ha="right", fontsize=8)
    ax.set_ylabel("相对误差")
    ax.set_title("Rayleigh-like 速度误差对比")
    ax.grid(axis="y", alpha=0.25)
    _save(fig, output_path)


def plot_elastic2d_surface_event_ridge(result: dict[str, Any], output_path: Path) -> None:
    """绘制最佳 case 的拾取 ridge。"""

    setup_chinese_matplotlib()
    best = result["best_case_metrics"]
    offsets = np.asarray(best.get("pick_offset_m", []), dtype=float)
    times = np.asarray(best.get("pick_time_s", []), dtype=float)
    fig, ax = plt.subplots(figsize=(6.6, 4.2), dpi=150)
    if offsets.size and times.size:
        ax.plot(offsets, times * 1000.0, marker="o", linewidth=2.0)
    ax.set_xlabel("震源到接收点水平距离 / m")
    ax.set_ylabel("拾取时间 / ms")
    ax.set_title(f"最佳 case 表面事件 ridge：{result['best_case']}")
    ax.grid(alpha=0.25)
    _save(fig, output_path)


def plot_elastic2d_free_surface_mode_comparison(result: dict[str, Any], output_path: Path) -> None:
    """按 free-surface 模式汇总最小速度误差。"""

    setup_chinese_matplotlib()
    grouped: dict[str, float] = {}
    for item in result["cases"].values():
        key = item["free_surface_mode"]
        grouped[key] = min(grouped.get(key, np.inf), item["rayleigh_velocity_relative_error"])
    fig, ax = plt.subplots(figsize=(6.8, 4.0), dpi=150)
    ax.bar(list(grouped.keys()), list(grouped.values()), color="#76b7b2")
    ax.set_ylabel("最小相对误差")
    ax.set_title("free-surface 模式对 Rayleigh-like 速度的影响")
    ax.grid(axis="y", alpha=0.25)
    _save(fig, output_path)


def plot_elastic2d_boundary_reflection_diagnostics(result: dict[str, Any], output_path: Path) -> None:
    """绘制 boundary reflection 指标。"""

    setup_chinese_matplotlib()
    names = list(result["cases"].keys())
    values = [result["cases"][name]["boundary_reflection_indicator"] for name in names]
    fig, ax = plt.subplots(figsize=(10.5, 4.4), dpi=150)
    ax.bar(np.arange(len(names)), values, color="#f28e2b")
    ax.set_xticks(np.arange(len(names)))
    ax.set_xticklabels(names, rotation=35, ha="right", fontsize=8)
    ax.set_ylabel("尾段能量占比")
    ax.set_title("边界反射 / 尾波诊断")
    ax.grid(axis="y", alpha=0.25)
    _save(fig, output_path)


def plot_elastic2d_das_staggered_vs_collocated(result: dict[str, Any], output_path: Path) -> None:
    """绘制 collocated/staggered 的 DAS-like gauge 对比。"""

    setup_chinese_matplotlib()
    names = list(result["cases"].keys())
    values = [result["cases"][name].get("gauge_metric", 0.0) for name in names]
    colors = ["#4e79a7" if result["cases"][name]["scheme"] == "collocated" else "#f28e2b" for name in names]
    fig, ax = plt.subplots(figsize=(8.5, 4.2), dpi=150)
    ax.bar(np.arange(len(names)), values, color=colors)
    ax.set_xticks(np.arange(len(names)))
    ax.set_xticklabels(names, rotation=35, ha="right", fontsize=8)
    ax.set_yscale("symlog", linthresh=1.0e-20)
    ax.set_ylabel("gauge 指标 RMS")
    ax.set_title("DAS-like gauge：collocated 与 staggered 对比")
    ax.grid(axis="y", alpha=0.25)
    _save(fig, output_path)


def plot_elastic2d_das_best_case(result: dict[str, Any], output_path: Path) -> None:
    """绘制 DAS-like gauge 最佳 case。"""

    setup_chinese_matplotlib()
    best = result["best_case_metrics"]
    fig, ax = plt.subplots(figsize=(6.2, 3.8), dpi=150)
    ax.axis("off")
    ax.text(0.5, 0.72, "DAS-like gauge 最佳 case", ha="center", fontsize=16, fontweight="bold")
    ax.text(
        0.5,
        0.42,
        f"case：{result['best_case']}\n"
        f"scheme：{best['scheme']}\n"
        f"source：{best['source_type']}\n"
        f"仅作 validation，不默认用于定位",
        ha="center",
        va="center",
        fontsize=11,
    )
    _save(fig, output_path)


def plot_elastic2d_das_report_consistency(result: dict[str, Any], output_path: Path) -> None:
    """绘制 DAS-like gauge 报告口径一致性图。"""

    setup_chinese_matplotlib()
    fig, ax = plt.subplots(figsize=(7.0, 3.8), dpi=150)
    ax.axis("off")
    ax.text(0.5, 0.75, "DAS gauge 口径一致性", ha="center", fontsize=16, fontweight="bold")
    ax.text(
        0.5,
        0.42,
        "结论：非零但仍弱 / 未校准\n"
        "默认定位：禁止使用 gauge strain\n"
        "原因：当前不是完整真实 DAS 仪器响应",
        ha="center",
        va="center",
        fontsize=12,
    )
    _save(fig, output_path)


def plot_latest_stable_quality_summary(result: dict[str, Any], output_path: Path) -> None:
    """绘制 latest_stable 图件质量治理摘要。"""

    setup_chinese_matplotlib()
    labels = ["总图件", "空图", "重复", "英文"]
    values = [
        result.get("latest_stable_total_figure_count", 0),
        result.get("empty_figure_count", 0),
        result.get("duplicate_figure_count", 0),
        result.get("english_figure_count", 0),
    ]
    fig, ax = plt.subplots(figsize=(6.6, 4.0), dpi=150)
    ax.bar(labels, values, color=["#4e79a7", "#e15759", "#f28e2b", "#9c755f"])
    ax.set_ylabel("数量")
    ax.set_title("latest_stable 图件质量治理摘要")
    ax.grid(axis="y", alpha=0.25)
    _save(fig, output_path)
