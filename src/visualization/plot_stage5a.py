"""Stage 5A 速度模型与模型错配诊断图件。"""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from src.model.rayleigh_effective_velocity import sample_velocity_profile
from src.model.velocity_model import build_velocity_model
from src.visualization.plot_style import setup_chinese_matplotlib


def plot_layered_velocity_profile(params: SimpleNamespace, output_path: Path) -> None:
    """绘制当前速度模型的深度剖面。

    该图用于说明 Stage 5A 默认不再只有 uniform velocity。若模型包含局部低速或
    横向梯度，本图仍只是在 x=0,y=0 处采样的示意剖面。
    """

    setup_chinese_matplotlib()
    model = build_velocity_model(params)
    profile = sample_velocity_profile(model, max(params.scan.depth_max_m, max(params.velocity.layer_depths_m)))
    fig, ax = plt.subplots(figsize=(5.8, 4.6), dpi=150)
    ax.plot(profile["velocity_mps"], profile["depth_m"], color="#1f77b4", linewidth=2.0)
    ax.invert_yaxis()
    ax.set_xlabel("等效 Rayleigh 速度 / (m/s)")
    ax.set_ylabel("深度 z / m")
    ax.set_title("分层/非均匀等效 Rayleigh 速度剖面示意")
    ax.grid(True, alpha=0.3)
    ax.text(
        0.02,
        0.98,
        "straight-ray kinematic approximation\n不是弹性波全波场速度反演",
        transform=ax.transAxes,
        va="top",
        fontsize=8,
        bbox={"facecolor": "white", "alpha": 0.75, "edgecolor": "0.8"},
    )
    fig.tight_layout()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path)
    plt.close(fig)


def plot_velocity_model_comparison(ablation: dict[str, Any], output_path: Path) -> None:
    """绘制不同速度模型的定位误差与 y/depth 高分区跨度。"""

    setup_chinese_matplotlib()
    names = list(ablation["cases"].keys())
    errors = [ablation["cases"][name]["truth_error"]["distance_m"] for name in names]
    y_spans = [ablation["cases"][name]["y_span_m"] for name in names]
    depth_spans = [ablation["cases"][name]["depth_span_m"] for name in names]
    x = np.arange(len(names))

    fig, axes = plt.subplots(2, 1, figsize=(9, 6.5), dpi=150, sharex=True)
    axes[0].bar(x, errors, color="#4c78a8")
    axes[0].set_ylabel("真值误差 / m")
    axes[0].set_title("速度模型消融：定位误差")
    axes[0].grid(axis="y", alpha=0.25)

    axes[1].bar(x - 0.18, y_spans, width=0.36, label="y 跨度", color="#59a14f")
    axes[1].bar(x + 0.18, depth_spans, width=0.36, label="depth 跨度", color="#f28e2b")
    axes[1].set_ylabel("高分区跨度 / m")
    axes[1].set_title("速度模型消融：三维不确定性跨度")
    axes[1].legend()
    axes[1].grid(axis="y", alpha=0.25)
    axes[1].set_xticks(x)
    axes[1].set_xticklabels(names, rotation=20, ha="right")
    fig.tight_layout()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path)
    plt.close(fig)


def plot_velocity_model_travel_time_residuals(ablation: dict[str, Any], output_path: Path) -> None:
    """绘制各速度模型相对 uniform 的绕射走时残差。"""

    setup_chinese_matplotlib()
    names = list(ablation["cases"].keys())
    mean_residual = [ablation["cases"][name]["travel_time_residual_to_uniform_mean_s"] * 1000.0 for name in names]
    rms_residual = [ablation["cases"][name]["travel_time_residual_to_uniform_rms_s"] * 1000.0 for name in names]
    x = np.arange(len(names))

    fig, ax = plt.subplots(figsize=(9, 4.6), dpi=150)
    ax.bar(x - 0.18, mean_residual, width=0.36, label="平均残差", color="#e15759")
    ax.bar(x + 0.18, rms_residual, width=0.36, label="RMS 残差", color="#76b7b2")
    ax.axhline(0.0, color="0.2", linewidth=0.8)
    ax.set_ylabel("相对 uniform 绕射走时残差 / ms")
    ax.set_title("速度模型对理论绕射走时曲线的影响")
    ax.set_xticks(x)
    ax.set_xticklabels(names, rotation=20, ha="right")
    ax.legend()
    ax.grid(axis="y", alpha=0.25)
    fig.tight_layout()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path)
    plt.close(fig)


def plot_model_mismatch_error_summary(mismatch: dict[str, Any], output_path: Path) -> None:
    """绘制 forward 模型与 scan 模型错配时的误差摘要。"""

    setup_chinese_matplotlib()
    names = list(mismatch["cases"].keys())
    errors = [mismatch["cases"][name]["truth_error"]["distance_m"] for name in names]
    depth_errors = [mismatch["cases"][name]["truth_error"]["ddepth_m"] for name in names]
    y_spans = [mismatch["cases"][name]["y_span_m"] for name in names]
    depth_spans = [mismatch["cases"][name]["depth_span_m"] for name in names]
    x = np.arange(len(names))

    fig, axes = plt.subplots(2, 1, figsize=(10, 7), dpi=150, sharex=True)
    axes[0].bar(x - 0.18, errors, width=0.36, label="三维误差", color="#4e79a7")
    axes[0].bar(x + 0.18, depth_errors, width=0.36, label="深度误差", color="#f28e2b")
    axes[0].axhline(0.0, color="0.2", linewidth=0.8)
    axes[0].set_ylabel("误差 / m")
    axes[0].set_title("速度模型错配：定位误差")
    axes[0].legend()
    axes[0].grid(axis="y", alpha=0.25)

    axes[1].bar(x - 0.18, y_spans, width=0.36, label="y 高分区跨度", color="#59a14f")
    axes[1].bar(x + 0.18, depth_spans, width=0.36, label="depth 高分区跨度", color="#e15759")
    axes[1].set_ylabel("跨度 / m")
    axes[1].set_title("速度模型错配：不确定性区域")
    axes[1].legend()
    axes[1].grid(axis="y", alpha=0.25)
    axes[1].set_xticks(x)
    axes[1].set_xticklabels(names, rotation=18, ha="right")
    fig.tight_layout()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path)
    plt.close(fig)
