"""运动学伪波场快照与动图。

这里的“伪波场”只用于科研可视化：它基于直达波和等效散射波的运动学走时，
在道路 x-y 平面上画出一个传播示意。它不是弹性波方程数值求解结果，也不是
完整 DAS 仪器模拟结果。
"""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter
import numpy as np

from src.forward.wavelet import ricker
from src.visualization.plot_style import setup_chinese_matplotlib


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
        在道路平面 x-y 上生成规则网格，对选定炮点计算直达波走时和
        source-scatter-grid 的等效散射走时，并叠加 Ricker 子波振幅。

    输入参数：
        params：统一参数对象；
        source_xyz：shape = (n_shot, 3)，单位 m；
        scatter_xyz：shape = (n_scatter, 3)，单位 m；
        scatter_weight：shape = (n_scatter,)，无量纲；
        velocity_mps：等效瑞雷波速度，单位 m/s；
        frame_time_s：当前快照时间，单位 s。

    输出形状：
        grid_x、grid_y、amplitude 均为 shape = (ny, nx)。

    近似条件和限制：
        这是 kinematic pseudo-wavefield snapshot，只表达走时传播示意，不是完整
        弹性波方程数值模拟结果。
    """

    x_grid = np.linspace(0.0, params.road.length_m, params.output.wavefield_grid_nx)
    y_grid = np.linspace(0.0, params.road.width_m, params.output.wavefield_grid_ny)
    grid_x, grid_y = np.meshgrid(x_grid, y_grid)
    grid_z = np.full_like(grid_x, params.road.surface_z_m)

    shot = source_xyz[params.output.wavefield_shot_index]
    direct_distance = np.sqrt((grid_x - shot[0]) ** 2 + (grid_y - shot[1]) ** 2 + (grid_z - shot[2]) ** 2)
    direct_arrival = params.time.t0_s + direct_distance / velocity_mps
    amplitude = ricker(frame_time_s - direct_arrival, params.task.wavelet_frequency_hz) / np.sqrt(direct_distance + 1.0)

    for scatter, weight in zip(scatter_xyz, scatter_weight):
        source_to_scatter = np.linalg.norm(shot - scatter)
        scatter_to_grid = np.sqrt((grid_x - scatter[0]) ** 2 + (grid_y - scatter[1]) ** 2 + (grid_z - scatter[2]) ** 2)
        path = source_to_scatter + scatter_to_grid
        scatter_arrival = params.time.t0_s + path / velocity_mps
        amplitude += weight * ricker(frame_time_s - scatter_arrival, params.task.wavelet_frequency_hz) / np.sqrt(path + 1.0)

    return grid_x, grid_y, amplitude


def plot_pseudo_wavefield_snapshot(
    params: SimpleNamespace,
    source_xyz: np.ndarray,
    scatter_xyz: np.ndarray,
    scatter_weight: np.ndarray,
    velocity_mps: float,
    frame_time_s: float,
    output_path: Path,
) -> None:
    """保存一张运动学伪波场快照图。"""

    setup_chinese_matplotlib()
    grid_x, grid_y, amplitude = compute_kinematic_pseudo_wavefield_frame(
        params, source_xyz, scatter_xyz, scatter_weight, velocity_mps, frame_time_s
    )
    clip = np.percentile(np.abs(amplitude), 99.0)
    if clip == 0:
        clip = 1.0

    fig, ax = plt.subplots(figsize=(9, 4.8), dpi=150)
    image = ax.imshow(
        amplitude,
        extent=[0.0, params.road.length_m, params.road.width_m, 0.0],
        cmap="seismic",
        vmin=-clip,
        vmax=clip,
        aspect="auto",
    )
    ax.plot(params.derived.channel_x, np.full_like(params.derived.channel_x, params.fiber.y_m), color="#1f77b4", label="光纤线")
    shot = source_xyz[params.output.wavefield_shot_index]
    ax.scatter([shot[0]], [shot[1]], marker="^", s=60, color="#d62728", label="当前震源")
    ax.scatter(scatter_xyz[:, 0], scatter_xyz[:, 1], marker="x", s=45, color="#2ca02c", label="等效散射点")
    ax.set_xlabel("沿道路方向 x / m")
    ax.set_ylabel("横穿道路方向 y / m")
    ax.set_title(f"运动学伪波场快照 t={frame_time_s:.3f}s（不是真实弹性波模拟）")
    fig.colorbar(image, ax=ax, label="相对振幅")
    ax.legend(loc="best", fontsize=8)
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
    fig, ax = plt.subplots(figsize=(9, 4.8), dpi=120)

    def draw(frame_index: int):
        ax.clear()
        frame_time_s = float(times[frame_index])
        _, _, amplitude = compute_kinematic_pseudo_wavefield_frame(
            params, source_xyz, scatter_xyz, scatter_weight, velocity_mps, frame_time_s
        )
        clip = np.percentile(np.abs(amplitude), 99.0)
        if clip == 0:
            clip = 1.0
        image = ax.imshow(
            amplitude,
            extent=[0.0, params.road.length_m, params.road.width_m, 0.0],
            cmap="seismic",
            vmin=-clip,
            vmax=clip,
            aspect="auto",
        )
        ax.plot(params.derived.channel_x, np.full_like(params.derived.channel_x, params.fiber.y_m), color="#1f77b4")
        shot = source_xyz[params.output.wavefield_shot_index]
        ax.scatter([shot[0]], [shot[1]], marker="^", s=50, color="#d62728")
        ax.scatter(scatter_xyz[:, 0], scatter_xyz[:, 1], marker="x", s=35, color="#2ca02c")
        ax.set_xlabel("沿道路方向 x / m")
        ax.set_ylabel("横穿道路方向 y / m")
        ax.set_title(f"运动学伪波场示意 t={frame_time_s:.3f}s（不是真实弹性波模拟）")
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
