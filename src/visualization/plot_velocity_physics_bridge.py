"""速度模型物理关系图件。"""

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


def plot_rayleigh_equivalent_vs_elastic_velocity(result: dict[str, Any], output_path: Path) -> None:
    """绘制 Rayleigh equivalent velocity、implied Vs 与 elastic2d Vs。"""

    setup_chinese_matplotlib()
    vr = np.asarray(result["layer_rayleigh_equivalent_velocity_mps"], dtype=float)
    implied_vs = np.asarray(result["implied_vs_from_rayleigh_mps"], dtype=float)
    x = np.arange(len(vr))
    fig, ax = plt.subplots(figsize=(7.0, 4.2), dpi=150)
    ax.plot(x, vr, marker="o", label="分层等效 Rayleigh 速度")
    ax.plot(x, implied_vs, marker="s", label="由 Vr/0.9 推算的 Vs")
    ax.axhline(result["elastic2d_vs_mps"], color="#e15759", linestyle="--", label="elastic2d Vs")
    ax.axhline(
        result["elastic2d_rayleigh_equivalent_mps"],
        color="#f28e2b",
        linestyle=":",
        label="elastic2d 0.9Vs 等效值",
    )
    ax.set_xlabel("层编号")
    ax.set_ylabel("速度 / (m/s)")
    ax.set_title("等效 Rayleigh 速度与 elastic2d Vs 对比")
    ax.legend()
    ax.grid(alpha=0.25)
    _save(fig, output_path)


def plot_elastic_vp_vs_rho_model(result: dict[str, Any], output_path: Path) -> None:
    """绘制 elastic2d Vp/Vs/rho 参数关系。"""

    setup_chinese_matplotlib()
    labels = ["Vp / m/s", "Vs / m/s", "密度 / kg/m3", "0.9Vs / m/s"]
    values = [
        result["elastic2d_vp_mps"],
        result["elastic2d_vs_mps"],
        result["elastic2d_rho_kgm3"],
        result["elastic2d_rayleigh_equivalent_mps"],
    ]
    fig, ax = plt.subplots(figsize=(6.2, 4.2), dpi=150)
    ax.bar(labels, values, color=["#4e79a7", "#59a14f", "#9c755f", "#f28e2b"])
    ax.set_ylabel("数值")
    ax.set_title("elastic2d validation Vp/Vs/rho 参数")
    ax.grid(axis="y", alpha=0.25)
    _save(fig, output_path)


def plot_velocity_model_physics_bridge(result: dict[str, Any], output_path: Path) -> None:
    """绘制速度模型桥接状态图。"""

    setup_chinese_matplotlib()
    fig, ax = plt.subplots(figsize=(7.0, 4.0), dpi=150)
    ax.axis("off")
    status = result["rayleigh_equivalent_vs_elastic_consistency"]
    color = "#59a14f" if status == "consistent" else "#e15759"
    text = (
        "速度模型物理桥接\n"
        f"状态：{status}\n"
        f"Vr 中值 = {result['representative_rayleigh_mps']:.1f} m/s\n"
        f"推算 Vs = {result['representative_implied_vs_mps']:.1f} m/s\n"
        f"elastic2d Vs = {result['elastic2d_vs_mps']:.1f} m/s\n"
        f"Vs 比值 = {result['elastic_vs_to_implied_vs_ratio']:.3f}"
    )
    ax.text(0.5, 0.55, text, ha="center", va="center", fontsize=14, fontweight="bold", color=color)
    ax.text(
        0.5,
        0.12,
        "layered_kinematic：等效 Rayleigh 速度\nelastic2d：Vp/Vs/rho validation 模型",
        ha="center",
        va="center",
        fontsize=10,
    )
    _save(fig, output_path)


def plot_bridge_derived_elastic_parameters(result: dict[str, Any], output_path: Path) -> None:
    """绘制由 Rayleigh equivalent velocity 推导的弹性参数示意。"""

    setup_chinese_matplotlib()
    implied_vs = np.asarray(result["implied_vs_from_rayleigh_mps"], dtype=float)
    implied_vp = 2.0 * implied_vs
    layers = np.arange(len(implied_vs))
    fig, ax = plt.subplots(figsize=(7.0, 4.2), dpi=150)
    ax.plot(layers, implied_vs, marker="o", label="由 Rayleigh 推算 Vs")
    ax.plot(layers, implied_vp, marker="s", label="示意 Vp=2Vs")
    ax.axhline(result["elastic2d_vs_mps"], color="#59a14f", linestyle="--", label="当前 elastic2d Vs")
    ax.axhline(result["elastic2d_vp_mps"], color="#4e79a7", linestyle=":", label="当前 elastic2d Vp")
    ax.set_xlabel("层编号")
    ax.set_ylabel("速度 / (m/s)")
    ax.set_title("由等效 Rayleigh 速度推导 elastic 参数的差异")
    ax.legend()
    ax.grid(alpha=0.25)
    _save(fig, output_path)
