"""Stage 5J forward-localization link 诊断。

这是本轮唯一新增 validation 脚本。它不扩展算法分支，只检查三维运动学体响应、
炮集绕射到时和 posterior-like 定位结果之间是否互相支持。
"""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from src.model.velocity_model import compute_scatter_travel_time
from src.visualization.plot_style import setup_chinese_matplotlib


def run_forward_localization_link(
    params: SimpleNamespace,
    volume_response: dict[str, Any],
    scan_result: dict[str, Any],
    source_xyz: np.ndarray,
    receiver_xyz: np.ndarray,
    velocity_model,
) -> dict[str, Any]:
    """计算 forward volume 与 posterior peak 的一致性摘要。"""

    volume_meta = volume_response.get("metadata", {})
    peak_volume = volume_meta.get("volume_peak_xyz_m", {})
    posterior_peak = scan_result.get("posterior_summary", {}).get("posterior_peak_location") or scan_result.get("best_location")
    truth = np.array([params.anomaly.x0_m, params.anomaly.y0_m, params.anomaly.depth_m], dtype=float)
    volume_xyz = np.array([peak_volume.get("x_m", np.nan), peak_volume.get("y_m", np.nan), peak_volume.get("depth_m", np.nan)], dtype=float)
    posterior_xyz = np.array(
        [posterior_peak.get("x_m", np.nan), posterior_peak.get("y_m", np.nan), posterior_peak.get("depth_m", np.nan)],
        dtype=float,
    )
    shot_index = int(params.output.wavefield_shot_index)
    posterior_curve = compute_scatter_travel_time(
        np.asarray(source_xyz[shot_index : shot_index + 1], dtype=float),
        posterior_xyz.reshape(1, 3),
        np.asarray(receiver_xyz, dtype=float),
        velocity_model,
    )[0, 0]
    truth_curve = compute_scatter_travel_time(
        np.asarray(source_xyz[shot_index : shot_index + 1], dtype=float),
        truth.reshape(1, 3),
        np.asarray(receiver_xyz, dtype=float),
        velocity_model,
    )[0, 0]
    curve_rms_ms = float(np.sqrt(np.mean((posterior_curve - truth_curve) ** 2)) * 1000.0)
    volume_to_truth_m = float(np.linalg.norm(volume_xyz - truth))
    posterior_to_truth_m = float(np.linalg.norm(posterior_xyz - truth))
    volume_to_posterior_m = float(np.linalg.norm(volume_xyz - posterior_xyz))
    status = "consistent" if volume_to_posterior_m <= 20.0 and curve_rms_ms <= 80.0 else "warning"
    likely_reasons = []
    if volume_to_posterior_m > 20.0:
        likely_reasons.append("geometry ambiguity or attribute weighting")
    if curve_rms_ms > 80.0:
        likely_reasons.append("velocity model mismatch or posterior peak timing offset")
    if params.attenuation.enabled:
        likely_reasons.append("attenuation changes amplitude ranking")
    if not likely_reasons:
        likely_reasons.append("forward volume and posterior peak are broadly aligned")
    return {
        "forward_localization_link_status": status,
        "volume_peak_xyz_m": peak_volume,
        "posterior_peak_location": posterior_peak,
        "volume_peak_to_truth_distance_m": volume_to_truth_m,
        "posterior_peak_to_truth_distance_m": posterior_to_truth_m,
        "volume_peak_to_posterior_peak_distance_m": volume_to_posterior_m,
        "posterior_vs_truth_scatter_curve_rms_ms": curve_rms_ms,
        "likely_reasons": likely_reasons,
    }


def plot_forward_localization_consistency(result: dict[str, Any], output_path: Path) -> None:
    """绘制 forward-localization link 的三维距离摘要。"""

    setup_chinese_matplotlib()
    labels = ["体响应-真值", "posterior-真值", "体响应-posterior"]
    values = [
        result["volume_peak_to_truth_distance_m"],
        result["posterior_peak_to_truth_distance_m"],
        result["volume_peak_to_posterior_peak_distance_m"],
    ]
    fig, axes = plt.subplots(1, 2, figsize=(10.5, 4.2), dpi=150)
    axes[0].bar(labels, values, color=["#4e79a7", "#59a14f", "#e15759"])
    axes[0].set_ylabel("三维距离 / m")
    axes[0].set_title("三维体响应与定位结果的一致性")
    axes[0].tick_params(axis="x", rotation=18)
    axes[0].grid(axis="y", alpha=0.25)
    axes[1].axis("off")
    text = (
        f"状态：{result['forward_localization_link_status']}\n"
        f"posterior/truth 绕射曲线 RMS：{result['posterior_vs_truth_scatter_curve_rms_ms']:.1f} ms\n"
        "可能原因：\n- " + "\n- ".join(result["likely_reasons"])
    )
    axes[1].text(0.02, 0.92, text, va="top", fontsize=10)
    fig.suptitle("forward-localization link：三维运动学 proxy 与定位后验的一致性")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(output_path)
    plt.close(fig)


def write_forward_localization_link_report(result: dict[str, Any], output_path: Path) -> None:
    """写出 forward-localization link 报告。"""

    lines = [
        "# forward-localization link 报告",
        "",
        "本报告连接三维运动学体响应 proxy、炮集理论绕射到时和 posterior-like 定位结果。",
        "当前结果仍是科研候选区，不是工程确诊。",
        "",
        f"- forward_localization_link_status = `{result['forward_localization_link_status']}`",
        f"- volume_peak_to_truth_distance_m = `{result['volume_peak_to_truth_distance_m']}`",
        f"- posterior_peak_to_truth_distance_m = `{result['posterior_peak_to_truth_distance_m']}`",
        f"- volume_peak_to_posterior_peak_distance_m = `{result['volume_peak_to_posterior_peak_distance_m']}`",
        f"- posterior_vs_truth_scatter_curve_rms_ms = `{result['posterior_vs_truth_scatter_curve_rms_ms']}`",
        "",
        "## 可能原因",
        "",
    ]
    lines.extend(f"- {item}" for item in result["likely_reasons"])
    lines.extend(
        [
            "",
            "## 限制",
            "",
            "- 三维体响应是 kinematic proxy，不是真实 3D elastic wavefield。",
            "- 单侧 DAS-like 几何仍可能导致 y-depth ambiguity。",
            "- attenuation 会改变振幅排序，不能被误读为真实粘弹性传播。",
        ]
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines), encoding="utf-8")
