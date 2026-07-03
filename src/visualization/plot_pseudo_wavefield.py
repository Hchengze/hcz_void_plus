"""运动学地表响应示意图与动图。

本模块只绘制道路表面 x-y 平面上的传播示意：
    x：沿道路方向，也是光纤延伸方向；
    y：横穿道路方向；
    z/depth：深度方向，向下为正。

注意：异常体深度 h 进入三维路径距离和 Rayleigh 波简化深度敏感性衰减，不会
被画到 y 轴上。这里的快照更准确地说是 kinematic surface response snapshot，
不是真实弹性波方程数值模拟结果。
"""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter
from matplotlib.patches import Rectangle
import numpy as np

from src.forward.wavelet import ricker
from src.physics.rayleigh import estimate_penetration_depth, rayleigh_depth_weight
from src.visualization.plot_style import setup_chinese_matplotlib


def build_pseudo_wavefield_surface_grid(params: SimpleNamespace) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """生成道路表面 x-y 平面伪波场网格。

    输出形状：
        grid_x、grid_y、grid_z 均为 shape = (ny, nx)。

    几何含义：
        grid_x 是沿道路方向坐标；
        grid_y 是横穿道路方向坐标；
        grid_z 固定为 0，表示道路表面平面。异常体深度不允许替代 grid_y。
    """

    margin_y = max(params.road.width_m * 0.08, 1.0)
    y_min = min(0.0, params.fiber.y_m, params.source.y_m) - margin_y
    y_max = max(params.road.width_m, params.fiber.y_m, params.source.y_m) + margin_y
    x_grid = np.linspace(0.0, params.road.length_m, params.output.wavefield_grid_nx)
    y_grid = np.linspace(y_min, y_max, params.output.wavefield_grid_ny)
    grid_x, grid_y = np.meshgrid(x_grid, y_grid)
    grid_z = np.zeros_like(grid_x)
    return grid_x, grid_y, grid_z


def compute_kinematic_pseudo_wavefield_frame(
    params: SimpleNamespace,
    source_xyz: np.ndarray,
    scatter_xyz: np.ndarray,
    scatter_weight: np.ndarray,
    velocity_mps: float,
    frame_time_s: float,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """计算单帧运动学伪波场。

    物理意义：
        在道路表面 x-y 平面上生成规则网格，选定一个炮点作为当前震源，计算
        source-grid 直达波走时，以及 source-scatter-grid 等效散射走时，并叠加
        Ricker 子波振幅。

    输入参数：
        source_xyz：shape = (n_shot, 3)，单位 m，z 通常为 0；
        scatter_xyz：shape = (n_scatter, 3)，单位 m，其中第 3 列是异常体深度；
        scatter_weight：shape = (n_scatter,)，无量纲；
        frame_time_s：当前快照时间，单位 s。

    输出形状：
        grid_x、grid_y、amplitude 均为 shape = (ny, nx)。

    近似条件和限制：
        这是 Rayleigh 波走时控制的运动学地表响应示意。grid_z 固定为 0；
        异常体深度只参与三维路径距离和简化深度敏感性衰减，不作为 y 坐标显示；
        结果不是真实弹性波模拟。
    """

    grid_x, grid_y, grid_z = build_pseudo_wavefield_surface_grid(params)

    shot = source_xyz[params.output.wavefield_shot_index]
    direct_distance = np.sqrt((grid_x - shot[0]) ** 2 + (grid_y - shot[1]) ** 2 + (grid_z - shot[2]) ** 2)
    direct_arrival = params.time.t0_s + direct_distance / velocity_mps
    amplitude = ricker(frame_time_s - direct_arrival, params.task.wavelet_frequency_hz) / np.sqrt(direct_distance + 1.0)

    penetration_depth_m = estimate_penetration_depth(params)
    for scatter, weight in zip(scatter_xyz, scatter_weight):
        # scatter[2] 是异常体深度 h：它影响三维路径距离，也通过 Rayleigh 波
        # 简化深度敏感性 exp(-h / penetration_depth) 衰减散射响应。
        depth_decay = rayleigh_depth_weight(scatter[2], penetration_depth_m)
        source_to_scatter = np.linalg.norm(shot - scatter)
        scatter_to_grid = np.sqrt((grid_x - scatter[0]) ** 2 + (grid_y - scatter[1]) ** 2 + (grid_z - scatter[2]) ** 2)
        path = source_to_scatter + scatter_to_grid
        scatter_arrival = params.time.t0_s + path / velocity_mps
        amplitude += (
            weight
            * depth_decay
            * ricker(frame_time_s - scatter_arrival, params.task.wavelet_frequency_hz)
            / np.sqrt(path + 1.0)
        )

    return grid_x, grid_y, amplitude


def _add_geometry_overlays(ax, params: SimpleNamespace, source_xyz: np.ndarray, scatter_xyz: np.ndarray) -> None:
    """在 x-y 平面图上叠加道路、光纤、震源测线和异常体投影。"""

    road = Rectangle(
        (0.0, 0.0),
        params.road.length_m,
        params.road.width_m,
        facecolor="#f2f2f2",
        edgecolor="0.20",
        linewidth=1.2,
        alpha=0.32,
        label="道路区域 0≤y≤W",
    )
    ax.add_patch(road)
    ax.axhline(params.fiber.y_m, color="#1f77b4", linewidth=2.0, label=f"DAS 光纤测线 y={params.fiber.y_m:.1f} m")
    ax.axhline(params.source.y_m, color="#d62728", linewidth=1.8, linestyle="--", label=f"震源测线 y=W={params.source.y_m:.1f} m")
    ax.scatter(source_xyz[:, 0], source_xyz[:, 1], marker="^", s=24, color="#d62728", alpha=0.65, label="全部炮点")
    shot = source_xyz[params.output.wavefield_shot_index]
    ax.scatter([shot[0]], [shot[1]], marker="*", s=110, color="#ff7f0e", edgecolors="black", linewidths=0.4, label="当前选中炮点")
    ax.scatter(
        [params.anomaly.x0_m],
        [params.anomaly.y0_m],
        marker="x",
        s=80,
        color="#2ca02c",
        linewidths=2.0,
        label="异常体平面投影，仅用于显示位置",
    )
    ax.text(
        params.anomaly.x0_m,
        params.anomaly.y0_m,
        f"  h={params.anomaly.depth_m:.1f} m",
        color="#2ca02c",
        fontsize=8,
        va="bottom",
    )
    ax.scatter(scatter_xyz[:, 0], scatter_xyz[:, 1], marker="+", s=36, color="#006d2c", alpha=0.7, label="等效散射点投影")


def _wavefield_extent(grid_x: np.ndarray, grid_y: np.ndarray) -> list[float]:
    """返回 imshow 使用的正向 x-y extent。"""

    return [float(grid_x.min()), float(grid_x.max()), float(grid_y.min()), float(grid_y.max())]


def plot_pseudo_wavefield_snapshot(
    params: SimpleNamespace,
    source_xyz: np.ndarray,
    scatter_xyz: np.ndarray,
    scatter_weight: np.ndarray,
    velocity_mps: float,
    frame_time_s: float,
    output_path: Path,
) -> None:
    """保存一张道路 x-y 平面运动学伪波场快照图。"""

    setup_chinese_matplotlib()
    grid_x, grid_y, amplitude = compute_kinematic_pseudo_wavefield_frame(
        params, source_xyz, scatter_xyz, scatter_weight, velocity_mps, frame_time_s
    )
    clip = np.percentile(np.abs(amplitude), 99.0)
    if clip == 0:
        clip = 1.0

    fig, ax = plt.subplots(figsize=(10, 4.8), dpi=150)
    image = ax.imshow(
        amplitude,
        extent=_wavefield_extent(grid_x, grid_y),
        origin="lower",
        cmap="seismic",
        vmin=-clip,
        vmax=clip,
        aspect="auto",
        alpha=0.92,
    )
    _add_geometry_overlays(ax, params, source_xyz, scatter_xyz)
    ax.set_xlabel("沿道路方向 x / m")
    ax.set_ylabel("横穿道路方向 y / m")
    ax.set_title(f"运动学地表响应示意 t={frame_time_s:.3f}s（不是真实弹性波场模拟）")
    fig.colorbar(image, ax=ax, label="相对振幅")
    ax.legend(loc="upper right", fontsize=7, ncol=2)
    fig.tight_layout()
    fig.savefig(output_path)
    plt.close(fig)


def _snapshot_times(params: SimpleNamespace) -> np.ndarray:
    """生成有限数量的快照时间，避免无节制输出所有时间帧。"""

    start = params.time.t0_s
    stop = params.time.record_length_s
    return np.linspace(start, stop, params.output.wavefield_snapshot_count)


def save_pseudo_wavefield_snapshots(
    params: SimpleNamespace,
    source_xyz: np.ndarray,
    scatter_xyz: np.ndarray,
    scatter_weight: np.ndarray,
    velocity_mps: float,
    output_dir: Path,
) -> list[Path]:
    """保存一组运动学伪波场快照。"""

    if not params.output.save_wavefield_snapshots:
        return []

    output_paths: list[Path] = []
    for index, frame_time_s in enumerate(_snapshot_times(params)):
        path = output_dir / f"snap_pseudo_wavefield_t{index:03d}.png"
        plot_pseudo_wavefield_snapshot(params, source_xyz, scatter_xyz, scatter_weight, velocity_mps, frame_time_s, path)
        output_paths.append(path)
    return output_paths


def save_pseudo_wavefield_animation(
    params: SimpleNamespace,
    source_xyz: np.ndarray,
    scatter_xyz: np.ndarray,
    scatter_weight: np.ndarray,
    velocity_mps: float,
    output_path: Path,
) -> dict[str, object]:
    """尝试保存运动学伪波场 GIF。

    如果 GIF 写出失败，本函数返回失败原因，不抛出异常，保证主流程继续完成。
    """

    if not params.output.save_wavefield_animation:
        return {"success": False, "path": None, "reason": "用户关闭 save_wavefield_animation。"}

    setup_chinese_matplotlib()
    times = _snapshot_times(params)
    fig, ax = plt.subplots(figsize=(10, 4.8), dpi=120)

    def draw(frame_index: int):
        ax.clear()
        frame_time_s = float(times[frame_index])
        grid_x, grid_y, amplitude = compute_kinematic_pseudo_wavefield_frame(
            params, source_xyz, scatter_xyz, scatter_weight, velocity_mps, frame_time_s
        )
        clip = np.percentile(np.abs(amplitude), 99.0)
        if clip == 0:
            clip = 1.0
        image = ax.imshow(
            amplitude,
            extent=_wavefield_extent(grid_x, grid_y),
            origin="lower",
            cmap="seismic",
            vmin=-clip,
            vmax=clip,
            aspect="auto",
            alpha=0.92,
        )
        _add_geometry_overlays(ax, params, source_xyz, scatter_xyz)
        ax.set_xlabel("沿道路方向 x / m")
        ax.set_ylabel("横穿道路方向 y / m")
        ax.set_title(f"运动学地表响应示意 t={frame_time_s:.3f}s（不是真实弹性波场模拟）")
        ax.legend(loc="upper right", fontsize=7, ncol=2)
        return [image]

    try:
        animation = FuncAnimation(fig, draw, frames=len(times), blit=False)
        writer = PillowWriter(fps=params.output.wavefield_animation_fps)
        animation.save(output_path, writer=writer)
        plt.close(fig)
        return {"success": True, "path": str(output_path), "reason": None}
    except Exception as exc:  # noqa: BLE001 - 这里需要保护科研主流程不中断
        plt.close(fig)
        return {"success": False, "path": None, "reason": str(exc)}
