"""Stage 4B 验证图件。"""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from src.validation.common import normalize_volume
from src.validation.fk_filter_validation import compute_fk_amplitude_spectrum
from src.visualization.plot_style import setup_chinese_matplotlib


def _case_labels(result: dict[str, Any]) -> list[str]:
    return list((result.get("cases") or result.get("groups") or {}).keys())


def plot_preprocessing_ablation_summary(result: dict[str, Any], output_path: Path) -> None:
    """绘制预处理消融的误差和 y/depth 跨度。"""

    setup_chinese_matplotlib()
    labels = _case_labels(result)
    errors = [result["cases"][name]["truth_error"]["distance_m"] for name in labels]
    y_spans = [result["cases"][name]["y_span_m"] for name in labels]
    d_spans = [result["cases"][name]["depth_span_m"] for name in labels]
    x = np.arange(len(labels))
    fig, axes = plt.subplots(2, 1, figsize=(10.5, 7.2), dpi=150, sharex=True)
    axes[0].bar(x, errors, color="#4C78A8")
    axes[0].set_ylabel("真值误差 / m")
    axes[0].set_title("预处理消融：定位误差")
    axes[1].plot(x, y_spans, marker="o", label="y 跨度")
    axes[1].plot(x, d_spans, marker="s", label="depth 跨度")
    axes[1].set_ylabel("高分区跨度 / m")
    axes[1].set_xticks(x)
    axes[1].set_xticklabels(labels, rotation=18, ha="right")
    axes[1].legend(loc="best")
    axes[1].grid(True, alpha=0.25)
    fig.suptitle("预处理组合消融验证（三维诊断网格，非工程确诊）")
    fig.tight_layout()
    fig.savefig(output_path)
    plt.close(fig)


def plot_fk_spectrum_before_after(
    params: SimpleNamespace,
    before_data: np.ndarray,
    after_data: np.ndarray,
    output_path: Path,
) -> None:
    """绘制 FK 前后单炮 f-k 谱。"""

    setup_chinese_matplotlib()
    shot_index = min(params.output.wavefield_shot_index, before_data.shape[0] - 1)
    freq, wavnum, before_amp = compute_fk_amplitude_spectrum(
        before_data[shot_index],
        params.time.dt_s,
        params.fiber.channel_spacing_m,
    )
    _, _, after_amp = compute_fk_amplitude_spectrum(
        after_data[shot_index],
        params.time.dt_s,
        params.fiber.channel_spacing_m,
    )
    fig, axes = plt.subplots(1, 2, figsize=(11.0, 4.8), dpi=150, sharey=True)
    for ax, amp, title in zip(axes, [before_amp, after_amp], ["FK 前", "FK 后"]):
        image = ax.imshow(
            amp,
            extent=[wavnum[0], wavnum[-1], freq[0], freq[-1]],
            origin="lower",
            aspect="auto",
            cmap="magma",
        )
        ax.set_title(title)
        ax.set_xlabel("波数 k / cycles m^-1")
        ax.set_ylim(0, min(120.0, float(np.max(freq))))
        fig.colorbar(image, ax=ax, fraction=0.046, pad=0.04)
    axes[0].set_ylabel("频率 f / Hz")
    fig.suptitle("简化 f-k 速度扇区滤波前后频谱（QC 图，不是成熟 FK 分离）")
    fig.tight_layout()
    fig.savefig(output_path)
    plt.close(fig)


def plot_fk_filter_effect_on_gather(
    params: SimpleNamespace,
    before_data: np.ndarray,
    after_data: np.ndarray,
    output_path: Path,
) -> None:
    """绘制 FK 前后 shot gather 对比。"""

    setup_chinese_matplotlib()
    shot_index = min(params.output.wavefield_shot_index, before_data.shape[0] - 1)
    channel_x = params.derived.channel_x
    time_axis = params.derived.time_axis
    vmax = float(np.percentile(np.abs(before_data[shot_index]), 99.0)) + 1.0e-12
    fig, axes = plt.subplots(1, 2, figsize=(11.2, 4.8), dpi=150, sharey=True)
    for ax, data, title in zip(axes, [before_data, after_data], ["滤波前", "滤波后"]):
        ax.imshow(
            data[shot_index],
            extent=[channel_x[0], channel_x[-1], time_axis[-1], time_axis[0]],
            aspect="auto",
            cmap="seismic",
            vmin=-vmax,
            vmax=vmax,
        )
        ax.set_title(title)
        ax.set_xlabel("通道 x / m")
    axes[0].set_ylabel("时间 / s")
    fig.suptitle("FK 滤波对炮集的影响：检查直达波削弱与绕射保留")
    fig.tight_layout()
    fig.savefig(output_path)
    plt.close(fig)


def _plot_attribute_slice(params: SimpleNamespace, volume: np.ndarray, title: str, output_path: Path) -> None:
    """绘制固定 best-y 的 x-depth 属性切片。"""

    setup_chinese_matplotlib()
    idx = np.unravel_index(int(np.argmax(volume)), volume.shape)
    iy = idx[1]
    image_data = normalize_volume(volume)[:, iy, :].T
    fig, ax = plt.subplots(figsize=(7.5, 5.0), dpi=150)
    image = ax.imshow(
        image_data,
        extent=[
            params.derived.scan_x_grid[0],
            params.derived.scan_x_grid[-1],
            params.derived.scan_depth_grid[-1],
            params.derived.scan_depth_grid[0],
        ],
        aspect="auto",
        origin="upper",
        cmap="viridis",
        vmin=0.0,
        vmax=1.0,
    )
    best_x = params.derived.scan_x_grid[idx[0]]
    best_depth = params.derived.scan_depth_grid[idx[2]]
    ax.scatter([best_x], [best_depth], marker="o", facecolors="none", edgecolors="white", label="属性 best")
    ax.scatter([params.anomaly.x0_m], [params.anomaly.depth_m], marker="x", color="red", label="真值")
    ax.set_xlabel("沿道路方向 x / m")
    ax.set_ylabel("埋深 h / m")
    ax.set_title(title)
    ax.legend(loc="best", fontsize=8)
    fig.colorbar(image, ax=ax, label="归一化属性得分")
    fig.tight_layout()
    fig.savefig(output_path)
    plt.close(fig)


def plot_matched_wavelet_score_comparison(params: SimpleNamespace, volume: np.ndarray, output_path: Path) -> None:
    _plot_attribute_slice(params, volume, "matched wavelet score x-depth 切片", output_path)


def plot_semblance_score_volume_slice(params: SimpleNamespace, volume: np.ndarray, output_path: Path) -> None:
    _plot_attribute_slice(params, volume, "semblance score x-depth 切片", output_path)


def plot_frequency_shift_attribute(params: SimpleNamespace, volume: np.ndarray, output_path: Path) -> None:
    _plot_attribute_slice(params, volume, "frequency shift attribute x-depth 切片", output_path)


def plot_multi_attribute_ablation(result: dict[str, Any], output_path: Path) -> None:
    """绘制多属性消融误差与高分区跨度。"""

    setup_chinese_matplotlib()
    labels = _case_labels(result)
    errors = [result["groups"][name]["truth_error"]["distance_m"] for name in labels]
    y_spans = [result["groups"][name]["y_span_m"] for name in labels]
    d_spans = [result["groups"][name]["depth_span_m"] for name in labels]
    x = np.arange(len(labels))
    fig, axes = plt.subplots(2, 1, figsize=(10.5, 7.2), dpi=150, sharex=True)
    axes[0].bar(x, errors, color="#72B7B2")
    axes[0].set_ylabel("真值误差 / m")
    axes[0].set_title("多属性消融：best 误差")
    axes[1].plot(x, y_spans, marker="o", label="y 跨度")
    axes[1].plot(x, d_spans, marker="s", label="depth 跨度")
    axes[1].set_ylabel("高分区跨度 / m")
    axes[1].set_xticks(x)
    axes[1].set_xticklabels(labels, rotation=18, ha="right")
    axes[1].legend(loc="best")
    axes[1].grid(True, alpha=0.25)
    fig.suptitle("multi_attribute 消融验证：若未优于 energy only，报告必须诚实说明")
    fig.tight_layout()
    fig.savefig(output_path)
    plt.close(fig)


def plot_geometry_ablation_best_locations(params: SimpleNamespace, result: dict[str, Any], output_path: Path) -> None:
    """绘制几何消融 best 平面位置。"""

    setup_chinese_matplotlib()
    fig, ax = plt.subplots(figsize=(8.8, 5.0), dpi=150)
    ax.axhspan(0.0, params.road.width_m, color="#eef3f7", alpha=0.9, label="道路区域")
    for name, item in result["cases"].items():
        loc = item["best_location"]
        ax.scatter([loc["x_m"]], [loc["y_m"]], s=55, label=name)
    ax.scatter([params.anomaly.x0_m], [params.anomaly.y0_m], marker="x", s=80, color="red", label="真值投影")
    ax.set_xlabel("沿道路方向 x / m")
    ax.set_ylabel("横穿道路方向 y / m")
    ax.set_title("三维几何消融：best 平面位置")
    ax.legend(loc="best", fontsize=7)
    fig.tight_layout()
    fig.savefig(output_path)
    plt.close(fig)


def plot_geometry_ablation_uncertainty_spans(result: dict[str, Any], output_path: Path) -> None:
    """绘制几何消融 y/depth 不确定性跨度。"""

    setup_chinese_matplotlib()
    labels = _case_labels(result)
    y_spans = [result["cases"][name]["y_span_m"] for name in labels]
    d_spans = [result["cases"][name]["depth_span_m"] for name in labels]
    x = np.arange(len(labels))
    fig, ax = plt.subplots(figsize=(10.5, 5.0), dpi=150)
    ax.bar(x - 0.18, y_spans, width=0.35, label="y 跨度")
    ax.bar(x + 0.18, d_spans, width=0.35, label="depth 跨度")
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=18, ha="right")
    ax.set_ylabel("高分区跨度 / m")
    ax.set_title("三维几何消融：y/depth 可分辨性对比")
    ax.legend(loc="best")
    ax.grid(True, axis="y", alpha=0.25)
    fig.tight_layout()
    fig.savefig(output_path)
    plt.close(fig)


def plot_3d_high_score_components(high_region: dict[str, Any], output_path: Path) -> None:
    """绘制高分连通域数量与各分量跨度。"""

    setup_chinese_matplotlib()
    boxes = high_region.get("component_boxes", [])
    labels = [f"C{i + 1}" for i in range(len(boxes))]
    y_spans = [box["y_span_m"] for box in boxes]
    d_spans = [box["depth_span_m"] for box in boxes]
    counts = [box["point_count"] for box in boxes]
    x = np.arange(len(labels))
    fig, axes = plt.subplots(2, 1, figsize=(8.5, 6.2), dpi=150, sharex=True)
    axes[0].bar(x, counts, color="#4C78A8")
    axes[0].set_ylabel("点数")
    axes[0].set_title("三维高分区 6-neighbor 连通域")
    axes[1].bar(x - 0.18, y_spans, width=0.35, label="y 跨度")
    axes[1].bar(x + 0.18, d_spans, width=0.35, label="depth 跨度")
    axes[1].set_xticks(x)
    axes[1].set_xticklabels(labels)
    axes[1].set_ylabel("跨度 / m")
    axes[1].legend(loc="best")
    axes[1].grid(True, axis="y", alpha=0.25)
    fig.tight_layout()
    fig.savefig(output_path)
    plt.close(fig)


def plot_recommendation_decision_flow(confidence_metrics: dict[str, Any], output_path: Path) -> None:
    """用文本图展示推荐位置决策依据。"""

    setup_chinese_matplotlib()
    stage3b = confidence_metrics["stage3b_warnings"]
    high_region = confidence_metrics["high_score_region"]
    recommendation = confidence_metrics["recommendation"]
    lines = [
        f"recommended_type: {recommendation['recommended_location_type']}",
        f"low_confidence_flag: {confidence_metrics['low_confidence_flag']}",
        f"boundary warning: {stage3b['best_depth_at_boundary_warning']}",
        f"wide-y warning: {stage3b['wide_y_high_score_zone_warning']}",
        f"raw/weighted divergence: {stage3b['raw_weighted_divergence_warning']}",
        f"shallow bias: {stage3b['shallow_bias_warning']}",
        f"multi-region warning: {high_region.get('multi_region_warning')}",
        f"component count: {high_region.get('high_score_component_count')}",
        "结论：科研候选区表达，不能作为工程确诊。",
    ]
    fig, ax = plt.subplots(figsize=(9.0, 5.2), dpi=150)
    ax.axis("off")
    ax.text(
        0.02,
        0.95,
        "\n".join(lines),
        transform=ax.transAxes,
        va="top",
        ha="left",
        fontsize=11,
    )
    ax.set_title("推荐位置决策流程摘要")
    fig.tight_layout()
    fig.savefig(output_path)
    plt.close(fig)
