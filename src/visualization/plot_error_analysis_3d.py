"""Stage 5H 三维主线误差分析图。

这里的图用于解释三维定位结果和当前 validation 限制之间的关系。它们不把 2D elastic
结果直接迁移成三维结论，只帮助人工复查 ready_for_2p5d、DAS gauge 与模型错配风险。
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from src.visualization.plot_elastic2d import (
    plot_rayleigh_pick_interpretation,
    plot_stage5g_status_badge,
    plot_stage5h_status_badge,
)
from src.visualization.plot_style import setup_chinese_matplotlib


def plot_model_mismatch_error_summary_3d(result: dict[str, Any], output_path: Path) -> None:
    """绘制面向三维定位解释的模型错配误差摘要。

    该函数是轻量接口，供测试和后续三维化复用；full_pipeline 当前仍复用 Stage 5A
    的模型错配实验结果。
    """

    setup_chinese_matplotlib()
    cases = result.get("cases", {})
    names = list(cases.keys()) or ["layered"]
    errors = []
    for name in names:
        item = cases.get(name, {})
        error = item.get("truth_error_distance_m") or item.get("distance_m") or item.get("error_m") or 0.0
        errors.append(float(error))
    fig, ax = plt.subplots(figsize=(7.0, 4.2), dpi=150)
    ax.bar(np.arange(len(names)), errors, color="#4e79a7")
    ax.set_xticks(np.arange(len(names)))
    ax.set_xticklabels(names, rotation=25, ha="right", fontsize=8)
    ax.set_ylabel("定位误差 / m")
    ax.set_title("三维定位模型错配误差摘要")
    ax.text(
        0.02,
        0.95,
        "当前速度为分层 Rayleigh 等效速度；不是完整 Vp/Vs/rho 弹性反演。",
        transform=ax.transAxes,
        va="top",
        fontsize=9,
        bbox={"facecolor": "white", "alpha": 0.78, "edgecolor": "0.8"},
    )
    ax.grid(axis="y", alpha=0.25)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(output_path)
    plt.close(fig)


def _save(fig: plt.Figure, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(output_path)
    plt.close(fig)


def plot_scan_velocity_model_consistency(result: dict[str, Any], output_path: Path) -> None:
    """绘制 scan 走时是否使用路径积分的审计摘要。"""

    setup_chinese_matplotlib()
    labels = ["direct", "scatter", "scan"]
    values = [
        1.0 if result.get("forward_direct_uses_path_integration") else 0.0,
        1.0 if result.get("forward_scatter_uses_path_integration") else 0.0,
        1.0 if result.get("scan_candidate_uses_path_integration") else 0.0,
    ]
    fig, ax = plt.subplots(figsize=(7.2, 4.2), dpi=150)
    ax.bar(labels, values, color=["#4e79a7", "#59a14f", "#f28e2b"])
    ax.set_ylim(0.0, 1.15)
    ax.set_ylabel("路径积分启用状态")
    ax.set_title("正演-扫描速度模型一致性：active scan 不使用代表速度")
    ax.text(
        0.02,
        0.90,
        f"scan_candidate_uses_path_integration={result.get('scan_candidate_uses_path_integration')}\n"
        f"scan_uses_representative_velocity={result.get('scan_uses_representative_velocity')}\n"
        f"layered vs representative RMS={result.get('active_vs_representative_rms_ms', 0.0):.3g} ms",
        transform=ax.transAxes,
        va="top",
        fontsize=9,
        bbox={"facecolor": "white", "alpha": 0.82, "edgecolor": "0.8"},
    )
    ax.grid(axis="y", alpha=0.25)
    _save(fig, output_path)


def plot_3d_geometry_resolution_analysis(scan_result: dict[str, Any], output_path: Path) -> None:
    """绘制三维几何分辨率体的 x-y 最大投影。"""

    setup_chinese_matplotlib()
    volume = np.asarray(scan_result["geometry_resolution_volume"], dtype=float)
    projection = np.max(volume, axis=2)
    summary = scan_result.get("geometry_resolution_summary", {})
    fig, ax = plt.subplots(figsize=(7.2, 4.8), dpi=150)
    im = ax.imshow(projection.T, origin="lower", aspect="auto", cmap="viridis")
    fig.colorbar(im, ax=ax, label="几何分辨率指标")
    ax.set_xlabel("x 网格索引")
    ax.set_ylabel("y 网格索引")
    ax.set_title("三维观测几何分辨率：y-depth 模糊性诊断")
    ax.text(
        0.02,
        0.95,
        f"几何类型：{summary.get('source_receiver_geometry_class')}\n"
        f"平均分辨率={summary.get('geometry_resolution_mean', 0.0):.3g}\n"
        f"y-depth 可分辨={summary.get('y_depth_separable')}",
        transform=ax.transAxes,
        va="top",
        fontsize=9,
        bbox={"facecolor": "white", "alpha": 0.82, "edgecolor": "0.8"},
    )
    _save(fig, output_path)


def plot_multi_peak_ambiguity_analysis(scan_result: dict[str, Any], output_path: Path) -> None:
    """绘制 posterior-like 高概率区域连通体和模糊性指标。"""

    setup_chinese_matplotlib()
    uncertainty = scan_result.get("uncertainty_summary", {})
    components = (uncertainty.get("connected_components_3d") or {}).get("component_boxes", [])
    counts = [item.get("point_count", 0) for item in components] or [0]
    labels = [f"连通体{i + 1}" for i in range(len(counts))]
    fig, ax = plt.subplots(figsize=(7.2, 4.2), dpi=150)
    ax.bar(labels, counts, color="#4e79a7")
    ax.set_ylabel("高概率网格点数")
    ax.set_title("三维 posterior-like 多峰/模糊性分析")
    ax.text(
        0.02,
        0.95,
        f"multi_peak_warning={uncertainty.get('multi_peak_warning')}\n"
        f"ambiguity_warning={uncertainty.get('ambiguity_warning')}\n"
        f"y_depth_coupling_warning={uncertainty.get('y_depth_coupling_warning')}",
        transform=ax.transAxes,
        va="top",
        fontsize=9,
        bbox={"facecolor": "white", "alpha": 0.82, "edgecolor": "0.8"},
    )
    ax.grid(axis="y", alpha=0.25)
    _save(fig, output_path)


def plot_module_coordination_summary(summary: dict[str, Any], output_path: Path) -> None:
    """绘制 Stage 5K 模块协同摘要。

    该图重点检查 forward、localization、posterior 是否围绕同一套三维 observation kernel 协同。
    """

    setup_chinese_matplotlib()
    items = [
        ("正演使用 kernel", summary.get("forward_uses_observation_kernel")),
        ("定位使用 kernel", summary.get("localization_uses_observation_kernel")),
        ("正演定位同核", summary.get("forward_localization_share_kernel")),
        ("接收一致性成像", summary.get("imaging_uses_receiver_consistent_paths")),
        ("proxy 不参与定位", not summary.get("volume_proxy_used_for_localization", True)),
        ("posterior 融合成像", summary.get("posterior_uses_imaging_volume")),
        ("几何诊断参与推荐", summary.get("geometry_resolution_used_in_recommendation")),
    ]
    labels = [item[0] for item in items]
    values = [1.0 if bool(item[1]) else 0.0 for item in items]
    fig, ax = plt.subplots(figsize=(8.4, 4.8), dpi=150)
    colors = ["#59a14f" if value > 0.5 else "#e15759" for value in values]
    ax.barh(np.arange(len(labels)), values, color=colors)
    ax.set_yticks(np.arange(len(labels)))
    ax.set_yticklabels(labels, fontsize=9)
    ax.set_xlim(0.0, 1.15)
    ax.set_xlabel("协同契约是否满足")
    ax.set_title("Stage 5K 模块协同：统一三维 observation kernel")
    ax.text(
        0.02,
        0.05,
        f"coordination_status={summary.get('module_coordination_status')}\n"
        f"volume_proxy_role={summary.get('volume_proxy_role')}\n"
        f"ready_for_2p5d={summary.get('ready_for_2p5d')}",
        transform=ax.transAxes,
        fontsize=9,
        bbox={"facecolor": "white", "alpha": 0.82, "edgecolor": "0.8"},
    )
    ax.grid(axis="x", alpha=0.25)
    _save(fig, output_path)


def _location_vector(location: dict[str, Any] | None) -> np.ndarray | None:
    if not location:
        return None
    return np.array([location["x_m"], location["y_m"], location["depth_m"]], dtype=float)


def plot_receiver_imaging_vs_volume_proxy(
    scan_result: dict[str, Any],
    volume_response: dict[str, Any] | None,
    output_path: Path,
) -> None:
    """对比接收一致性成像峰值与旧体响应 proxy 峰值。

    Stage 5K 后，定位解释优先看 receiver-consistent imaging；volume proxy 只保留作 forward 可读性图。
    """

    setup_chinese_matplotlib()
    imaging_peak = _location_vector(scan_result.get("imaging_peak_location"))
    posterior_peak = _location_vector(scan_result.get("posterior_peak_location"))
    proxy_peak = _location_vector((volume_response or {}).get("metadata", {}).get("volume_peak_xyz_m"))
    labels = ["成像峰值-后验峰值", "proxy峰值-后验峰值"]
    imaging_distance = (
        float(np.linalg.norm(imaging_peak - posterior_peak)) if imaging_peak is not None and posterior_peak is not None else 0.0
    )
    proxy_distance = (
        float(np.linalg.norm(proxy_peak - posterior_peak)) if proxy_peak is not None and posterior_peak is not None else 0.0
    )
    fig, ax = plt.subplots(figsize=(7.6, 4.6), dpi=150)
    ax.bar(labels, [imaging_distance, proxy_distance], color=["#59a14f", "#f28e2b"])
    ax.set_ylabel("与 posterior peak 的距离 / m")
    ax.set_title("接收一致性成像 vs 三维体响应 proxy")
    ax.text(
        0.02,
        0.95,
        "结论口径：volume proxy = visualization_only；定位依据优先使用 receiver-consistent imaging。",
        transform=ax.transAxes,
        va="top",
        fontsize=9,
        bbox={"facecolor": "white", "alpha": 0.82, "edgecolor": "0.8"},
    )
    ax.grid(axis="y", alpha=0.25)
    _save(fig, output_path)


__all__ = [
    "plot_model_mismatch_error_summary_3d",
    "plot_rayleigh_pick_interpretation",
    "plot_stage5g_status_badge",
    "plot_stage5h_status_badge",
    "plot_scan_velocity_model_consistency",
    "plot_3d_geometry_resolution_analysis",
    "plot_multi_peak_ambiguity_analysis",
    "plot_module_coordination_summary",
    "plot_receiver_imaging_vs_volume_proxy",
]
