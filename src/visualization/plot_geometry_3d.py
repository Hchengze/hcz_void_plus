"""三维道路 DAS-like 几何与速度采样路径图。

这些图服务 Stage 5G 的主线核验：项目最终对象是三维道路场景，二维 elastic 只是局部
validation。图中所有候选、震源和接收点都用 xyz/h 表达，但不声称已经完成 3D elastic
波场模拟。
"""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from src.model.velocity_model import build_velocity_model
from src.visualization.plot_style import setup_chinese_matplotlib


def _save(fig: plt.Figure, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(output_path)
    plt.close(fig)


def _candidate_xyz(params: SimpleNamespace, scan_result: dict[str, Any] | None = None) -> np.ndarray:
    """选择用于路径展示的候选点，优先使用当前推荐/最佳定位点。"""

    location = None
    if scan_result:
        location = scan_result.get("best_location") or scan_result.get("active_best_location")
    if not location:
        location = {"x_m": params.anomaly.x0_m, "y_m": params.anomaly.y0_m, "depth_m": params.anomaly.depth_m}
    return np.array([location["x_m"], location["y_m"], location["depth_m"]], dtype=float)


def plot_geometry_3d_overview(
    params: SimpleNamespace,
    source_xyz: np.ndarray,
    receiver_xyz: np.ndarray,
    scatter_xyz: np.ndarray,
    output_path: Path,
    scan_result: dict[str, Any] | None = None,
) -> None:
    """绘制三维 source / receiver / anomaly / candidate 总览图。"""

    setup_chinese_matplotlib()
    candidate = _candidate_xyz(params, scan_result)
    fig = plt.figure(figsize=(9.2, 6.2), dpi=150)
    ax = fig.add_subplot(111, projection="3d")

    road_x = [0.0, params.road.length_m, params.road.length_m, 0.0, 0.0]
    road_y = [0.0, 0.0, params.road.width_m, params.road.width_m, 0.0]
    road_z = [0.0] * 5
    ax.plot(road_x, road_y, road_z, color="0.35", linewidth=1.5, label="道路边界")
    ax.plot(receiver_xyz[:, 0], receiver_xyz[:, 1], receiver_xyz[:, 2], color="#1f77b4", linewidth=2.0, label="DAS-like 光纤线")
    ax.scatter(receiver_xyz[:, 0], receiver_xyz[:, 1], receiver_xyz[:, 2], s=8, color="#1f77b4", alpha=0.65)
    ax.plot(source_xyz[:, 0], source_xyz[:, 1], source_xyz[:, 2], color="#d62728", linestyle="--", linewidth=1.5, label="震源线")
    ax.scatter(source_xyz[:, 0], source_xyz[:, 1], source_xyz[:, 2], s=28, marker="^", color="#d62728", label="震源点")
    ax.scatter(scatter_xyz[:, 0], scatter_xyz[:, 1], scatter_xyz[:, 2], s=38, marker="+", color="#2ca02c", label="异常体等效散射点")
    ax.scatter([candidate[0]], [candidate[1]], [candidate[2]], s=86, marker="o", facecolors="none", edgecolors="#ff7f0e", linewidths=2.0, label="当前候选/推荐点")
    ax.scatter([params.anomaly.x0_m], [params.anomaly.y0_m], [params.anomaly.depth_m], s=82, marker="x", color="black", linewidths=2.0, label="真值位置")

    ax.set_xlabel("沿道路 x / m")
    ax.set_ylabel("横向 y / m")
    ax.set_zlabel("埋深 h / m")
    ax.set_title("三维道路 DAS-like 几何总览：不是 3D elastic 波场")
    ax.invert_zaxis()
    ax.view_init(elev=22, azim=-58)
    ax.legend(loc="upper left", fontsize=8)
    _save(fig, output_path)


def plot_velocity_sampling_paths_3d(
    params: SimpleNamespace,
    source_xyz: np.ndarray,
    receiver_xyz: np.ndarray,
    candidate_xyz: np.ndarray,
    output_path: Path,
) -> dict[str, Any]:
    """绘制三维 source -> candidate -> receiver 速度采样路径。"""

    setup_chinese_matplotlib()
    model = build_velocity_model(params)
    source = np.asarray(source_xyz[len(source_xyz) // 2], dtype=float)
    receiver = np.asarray(receiver_xyz[len(receiver_xyz) // 2], dtype=float)
    candidate = np.asarray(candidate_xyz, dtype=float)

    t1 = np.linspace(0.0, 1.0, 48, endpoint=False)[:, None]
    t2 = np.linspace(0.0, 1.0, 48)[:, None]
    samples = np.vstack([source + t1 * (candidate - source), candidate + t2 * (receiver - candidate)])
    velocities = model.velocity_at(samples)
    distance = np.concatenate([[0.0], np.cumsum(np.linalg.norm(np.diff(samples, axis=0), axis=1))])

    fig = plt.figure(figsize=(10.2, 4.8), dpi=150)
    ax3d = fig.add_subplot(121, projection="3d")
    line = ax3d.scatter(samples[:, 0], samples[:, 1], samples[:, 2], c=velocities, cmap="viridis", s=22)
    ax3d.scatter([source[0]], [source[1]], [source[2]], marker="^", s=70, color="#d62728", label="选中震源")
    ax3d.scatter([candidate[0]], [candidate[1]], [candidate[2]], marker="o", s=70, facecolors="none", edgecolors="#ff7f0e", label="候选点")
    ax3d.scatter([receiver[0]], [receiver[1]], [receiver[2]], marker="s", s=50, color="#1f77b4", label="选中接收点")
    ax3d.set_xlabel("x / m")
    ax3d.set_ylabel("y / m")
    ax3d.set_zlabel("h / m")
    ax3d.invert_zaxis()
    ax3d.set_title("三维采样路径")
    ax3d.legend(loc="upper left", fontsize=7)

    ax = fig.add_subplot(122)
    ax.plot(distance, velocities, color="#e15759", linewidth=2.0)
    ax.set_xlabel("路径距离 / m")
    ax.set_ylabel("采样 Rayleigh 等效速度 / (m/s)")
    ax.set_title("source → candidate → receiver 分层速度采样")
    ax.grid(alpha=0.25)
    fig.colorbar(line, ax=ax3d, fraction=0.046, pad=0.04, label="m/s")
    _save(fig, output_path)

    return {
        "sample_count": int(samples.shape[0]),
        "velocity_min_mps": float(np.min(velocities)),
        "velocity_max_mps": float(np.max(velocities)),
        "velocity_mean_mps": float(np.mean(velocities)),
    }
