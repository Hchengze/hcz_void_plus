"""三维不确定性与 score_method 对比图件。"""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from src.visualization.plot_style import setup_chinese_matplotlib


def _nearest_index(grid: np.ndarray, value: float) -> int:
    return int(np.argmin(np.abs(grid - value)))


def plot_score_method_depth_comparison(
    params: SimpleNamespace,
    comparison_result: dict[str, Any],
    output_path: Path,
) -> None:
    """绘制不同 score_method 的 best depth 对比图。

    图中同时显示 unweighted_best 和 weighted_best 的深度。若 weighted_best 总是贴近
    scan_depth_min，而 unweighted_best 更接近真值，应在报告中提示 depth weighting
    对深度结果的影响。
    """

    setup_chinese_matplotlib()
    methods = list(comparison_result["methods"].keys())
    unweighted_depth = [comparison_result["methods"][m]["unweighted_best_location"]["depth_m"] for m in methods]
    weighted_depth = [comparison_result["methods"][m]["weighted_best_location"]["depth_m"] for m in methods]
    x = np.arange(len(methods))
    fig, ax = plt.subplots(figsize=(8.5, 4.8), dpi=150)
    ax.bar(x - 0.18, unweighted_depth, width=0.35, label="unweighted_best depth")
    ax.bar(x + 0.18, weighted_depth, width=0.35, label="weighted_best depth")
    ax.axhline(params.anomaly.depth_m, color="red", linestyle="--", linewidth=1.2, label="真实深度")
    ax.axhline(params.scan.depth_min_m, color="0.4", linestyle=":", linewidth=1.0, label="扫描深度边界")
    ax.set_xticks(x)
    ax.set_xticklabels(methods, rotation=12, ha="right")
    ax.set_ylabel("埋深 h / m")
    ax.set_title("score_method 深度对比（运动学扫描，不是工程确诊）")
    ax.legend(loc="best", fontsize=8)
    ax.grid(True, axis="y", alpha=0.25)
    fig.tight_layout()
    fig.savefig(output_path)
    plt.close(fig)


def plot_3d_high_score_uncertainty_summary(
    params: SimpleNamespace,
    high_score_region: dict[str, Any],
    output_path: Path,
) -> None:
    """绘制三维高分区跨度摘要图。"""

    setup_chinese_matplotlib()
    spans = [
        high_score_region["x_span_m"],
        high_score_region["y_span_m"],
        high_score_region["depth_span_m"],
    ]
    labels = ["x 跨度", "y 跨度", "depth 跨度"]
    fig, ax = plt.subplots(figsize=(7.5, 4.8), dpi=150)
    ax.bar(labels, spans, color=["#4C78A8", "#F58518", "#54A24B"])
    ax.set_ylabel("跨度 / m")
    ax.set_title("三维高分候选区不确定性摘要")
    for i, value in enumerate(spans):
        ax.text(i, value, f"{value:.2f}", ha="center", va="bottom", fontsize=9)
    text = (
        f"高分点数: {high_score_region['high_score_region_point_count']}\n"
        f"等效体积: {high_score_region['high_score_region_volume_estimate_m3']:.3g} m^3\n"
        f"阈值: {high_score_region['threshold_ratio']} × best_score\n"
        "说明: 高分体是运动学扫描候选区，不是工程确诊边界。"
    )
    ax.text(0.98, 0.95, text, transform=ax.transAxes, ha="right", va="top", fontsize=9)
    ax.grid(True, axis="y", alpha=0.25)
    fig.tight_layout()
    fig.savefig(output_path)
    plt.close(fig)


def plot_x_y_depth_uncertainty_slices(
    params: SimpleNamespace,
    score_volume: np.ndarray,
    high_score_region: dict[str, Any],
    recommended_location: dict[str, Any],
    output_path: Path,
) -> None:
    """绘制 x-y-depth 不确定性切片。

    三个面分别为：
        1. 固定 recommended depth 的 x-y 切片；
        2. 固定 recommended y 的 x-depth 切片；
        3. 固定 recommended x 的 y-depth 切片。

    这些切片用于提醒用户：当前应看三维高分体，而不是只看单个 x-depth 剖面。
    """

    setup_chinese_matplotlib()
    x_grid = params.derived.scan_x_grid
    y_grid = params.derived.scan_y_grid
    depth_grid = params.derived.scan_depth_grid
    normalized = score_volume
    max_score = float(np.max(normalized))
    min_score = float(np.min(normalized))
    if max_score > min_score:
        normalized = (normalized - min_score) / (max_score - min_score)
    else:
        normalized = np.zeros_like(normalized)

    rec_x = recommended_location.get("x_m", params.anomaly.x0_m)
    rec_y = recommended_location.get("y_m", params.anomaly.y0_m)
    rec_depth = recommended_location.get("depth_m", params.anomaly.depth_m)
    ix = _nearest_index(x_grid, rec_x)
    iy = _nearest_index(y_grid, rec_y)
    iz = _nearest_index(depth_grid, rec_depth)

    fig, axes = plt.subplots(1, 3, figsize=(13.2, 4.4), dpi=150)
    images = [
        (
            axes[0],
            normalized[:, :, iz].T,
            [x_grid[0], x_grid[-1], y_grid[0], y_grid[-1]],
            "x-y 切片",
            "x / m",
            "y / m",
        ),
        (
            axes[1],
            normalized[:, iy, :].T,
            [x_grid[0], x_grid[-1], depth_grid[-1], depth_grid[0]],
            "x-depth 切片",
            "x / m",
            "h / m",
        ),
        (
            axes[2],
            normalized[ix, :, :].T,
            [y_grid[0], y_grid[-1], depth_grid[-1], depth_grid[0]],
            "y-depth 切片",
            "y / m",
            "h / m",
        ),
    ]
    for ax, data, extent, title, xlabel, ylabel in images:
        image = ax.imshow(data, extent=extent, aspect="auto", origin="upper", cmap="viridis", vmin=0.0, vmax=1.0)
        ax.set_title(title)
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        fig.colorbar(image, ax=ax, fraction=0.046, pad=0.04)
    axes[0].scatter([params.anomaly.x0_m], [params.anomaly.y0_m], marker="x", color="white", label="真实异常体")
    axes[0].scatter([rec_x], [rec_y], marker="o", facecolors="none", edgecolors="red", label="推荐参考点")
    axes[0].legend(loc="best", fontsize=7)
    axes[1].scatter([params.anomaly.x0_m], [params.anomaly.depth_m], marker="x", color="white")
    axes[1].scatter([rec_x], [rec_depth], marker="o", facecolors="none", edgecolors="red")
    axes[2].scatter([params.anomaly.y0_m], [params.anomaly.depth_m], marker="x", color="white")
    axes[2].scatter([rec_y], [rec_depth], marker="o", facecolors="none", edgecolors="red")
    fig.suptitle("三维高分区不确定性切片：候选体而非确定点", fontsize=12)
    fig.tight_layout()
    fig.savefig(output_path)
    plt.close(fig)


def plot_multi_attribute_score_comparison(
    params: SimpleNamespace,
    scan_result: dict[str, Any],
    output_path: Path,
) -> None:
    """绘制多属性 score 的 best 位置与得分摘要。

    该图用于检查 energy、normalized energy、matched wavelet 和 semblance 是否对
    x/y/depth 给出一致候选。若属性之间分歧明显，报告应倾向不确定性区间而非单点。
    """

    setup_chinese_matplotlib()
    volumes = scan_result.get("attribute_score_volumes", {})
    names = ["energy_score", "normalized_energy_score", "matched_wavelet_score", "semblance_score"]
    best_depths = []
    best_x = []
    best_y = []
    for name in names:
        volume = volumes.get(name)
        if volume is None or not np.any(np.isfinite(volume)):
            best_depths.append(0.0)
            best_x.append(0.0)
            best_y.append(0.0)
            continue
        idx = np.unravel_index(int(np.argmax(volume)), volume.shape)
        best_x.append(float(params.derived.scan_x_grid[idx[0]]))
        best_y.append(float(params.derived.scan_y_grid[idx[1]]))
        best_depths.append(float(params.derived.scan_depth_grid[idx[2]]))

    x = np.arange(len(names))
    fig, axes = plt.subplots(1, 2, figsize=(10.5, 4.8), dpi=150)
    axes[0].bar(x, best_depths, color="#4C78A8")
    axes[0].axhline(params.anomaly.depth_m, color="red", linestyle="--", linewidth=1.1, label="真实深度")
    axes[0].set_xticks(x)
    axes[0].set_xticklabels(names, rotation=15, ha="right")
    axes[0].set_ylabel("best depth / m")
    axes[0].set_title("各属性 best depth")
    axes[0].legend(loc="best", fontsize=8)
    axes[1].scatter(best_x, best_y, s=65, c=best_depths, cmap="viridis", label="属性 best")
    axes[1].scatter([params.anomaly.x0_m], [params.anomaly.y0_m], marker="x", s=70, color="red", label="真实异常体")
    for i, name in enumerate(names):
        axes[1].text(best_x[i], best_y[i], f" {name}", fontsize=7)
    axes[1].set_xlabel("x / m")
    axes[1].set_ylabel("y / m")
    axes[1].set_title("各属性 best x-y 投影")
    axes[1].legend(loc="best", fontsize=8)
    fig.suptitle("多属性扫描得分对比（科研候选，不是工程确诊）", fontsize=12)
    fig.tight_layout()
    fig.savefig(output_path)
    plt.close(fig)


def plot_depth_prior_sensitivity(
    params: SimpleNamespace,
    sensitivity_result: dict[str, Any],
    output_path: Path,
) -> None:
    """绘制 depth prior 因子对 best depth 的影响。"""

    setup_chinese_matplotlib()
    factors = list(sensitivity_result["factors"].keys())
    depths = [sensitivity_result["factors"][factor]["best_location"]["depth_m"] for factor in factors]
    x = np.arange(len(factors))
    fig, ax = plt.subplots(figsize=(8.5, 4.8), dpi=150)
    ax.plot(x, depths, marker="o", linewidth=1.8, label="best depth")
    ax.axhline(params.anomaly.depth_m, color="red", linestyle="--", linewidth=1.1, label="真实深度")
    ax.axhline(params.scan.depth_min_m, color="0.4", linestyle=":", linewidth=1.0, label="深度边界")
    ax.set_xticks(x)
    ax.set_xticklabels(factors)
    ax.set_xlabel("depth prior factor")
    ax.set_ylabel("best depth / m")
    ax.set_title("depth prior 强度敏感性诊断")
    ax.legend(loc="best", fontsize=8)
    ax.grid(True, alpha=0.25)
    fig.tight_layout()
    fig.savefig(output_path)
    plt.close(fig)
