"""三维运动学体响应 proxy。

本模块把 Stage 5J 的正演展示从 x-y 地表面推进到 x-y-depth 体网格。
它仍是 layered_kinematic 的三维运动学响应 proxy：走时使用 velocity_model path integration，
振幅使用 amplitude_model 的经验 Q attenuation；它不是 3D elastic wavefield。
"""

from __future__ import annotations

from dataclasses import dataclass
from types import SimpleNamespace
from typing import Any

import numpy as np

from src.forward.amplitude_model import compute_direct_amplitude, compute_scatter_amplitude
from src.forward.wavelet import ricker
from src.model.velocity_model import KinematicVelocityModel, compute_kinematic_travel_time


@dataclass(frozen=True)
class VolumeGrid:
    """三维体响应网格，数组顺序为 depth/y/x。"""

    x_axis_m: np.ndarray
    y_axis_m: np.ndarray
    depth_axis_m: np.ndarray
    xyz: np.ndarray


def build_volume_grid(params: SimpleNamespace) -> VolumeGrid:
    """构建 x-y-depth 体网格，depth/h 向下为正。"""

    nx = int(params.output.volume_wavefield_nx)
    ny = int(params.output.volume_wavefield_ny)
    nh = int(params.output.volume_wavefield_nh)
    x_axis = np.linspace(0.0, params.road.length_m, nx)
    y_axis = np.linspace(0.0, params.road.width_m, ny)
    depth_max = max(params.scan.depth_max_m, params.anomaly.depth_m * 1.5, 1.0)
    depth_axis = np.linspace(0.0, depth_max, nh)
    depth_grid, y_grid, x_grid = np.meshgrid(depth_axis, y_axis, x_axis, indexing="ij")
    xyz = np.stack([x_grid, y_grid, depth_grid], axis=-1)
    return VolumeGrid(x_axis, y_axis, depth_axis, xyz)


def _select_scatter_points(
    scatter_xyz: np.ndarray,
    scatter_weight: np.ndarray,
    max_count: int,
) -> tuple[np.ndarray, np.ndarray]:
    """按散射权重挑选少量代表点，避免体响应 proxy 拖慢 full_pipeline。"""

    scatter = np.asarray(scatter_xyz, dtype=float)
    weight = np.asarray(scatter_weight, dtype=float)
    if scatter.shape[0] <= max_count:
        return scatter, weight
    order = np.argsort(np.abs(weight))[::-1][:max_count]
    return scatter[order], weight[order]


def compute_kinematic_volume_response(
    params: SimpleNamespace,
    source_xyz: np.ndarray,
    scatter_xyz: np.ndarray,
    scatter_weight: np.ndarray,
    velocity_model: KinematicVelocityModel,
    *,
    shot_index: int | None = None,
) -> dict[str, Any]:
    """生成三维运动学体响应帧。

    输出 ``volume_frames`` 的 shape 为 ``(nt_frame, nh, ny, nx)``。
    这里的体响应只用于三维 forward 可读性和 forward-localization link，不替代 elastic2d。
    """

    grid = build_volume_grid(params)
    shot_id = int(params.output.wavefield_shot_index if shot_index is None else shot_index)
    shot_id = max(0, min(shot_id, len(source_xyz) - 1))
    shot = np.asarray(source_xyz[shot_id], dtype=float)
    scatter, weight = _select_scatter_points(
        scatter_xyz,
        scatter_weight,
        int(params.output.volume_wavefield_max_scatter_points),
    )

    times = np.linspace(params.time.t0_s, params.time.record_length_s, int(params.output.volume_wavefield_frame_count))
    direct_arrival = params.time.t0_s + compute_kinematic_travel_time(shot, grid.xyz, velocity_model)
    direct_amp = compute_direct_amplitude(params, shot, grid.xyz, direct_arrival - params.time.t0_s)

    scattered_arrivals: list[np.ndarray] = []
    scattered_amplitudes: list[np.ndarray] = []
    for scat, scat_weight in zip(scatter, weight):
        t_source_scatter = compute_kinematic_travel_time(shot, scat, velocity_model)
        t_scatter_grid = compute_kinematic_travel_time(scat, grid.xyz, velocity_model)
        arrival = params.time.t0_s + t_source_scatter + t_scatter_grid
        amp = compute_scatter_amplitude(
            params,
            shot,
            scat,
            grid.xyz,
            t_source_scatter + t_scatter_grid,
            scat_weight,
        )
        scattered_arrivals.append(arrival)
        scattered_amplitudes.append(amp)

    frames = np.zeros((len(times), len(grid.depth_axis_m), len(grid.y_axis_m), len(grid.x_axis_m)), dtype=float)
    for iframe, frame_time in enumerate(times):
        frame = direct_amp * ricker(frame_time - direct_arrival, params.task.wavelet_frequency_hz)
        for arrival, amp in zip(scattered_arrivals, scattered_amplitudes):
            frame = frame + amp * ricker(frame_time - arrival, params.task.wavelet_frequency_hz)
        frames[iframe] = frame

    energy = np.max(np.abs(frames), axis=0)
    metadata = {
        "volume_grid_shape": list(frames.shape),
        "volume_frame_count": int(frames.shape[0]),
        "volume_nh_ny_nx": [int(frames.shape[1]), int(frames.shape[2]), int(frames.shape[3])],
        "depth_axis_positive_down": True,
        "volume_uses_velocity_path_integration": True,
        "volume_uses_attenuation": bool(params.attenuation.enabled),
        "volume_is_kinematic_proxy": True,
        "selected_shot_index": shot_id,
        "selected_scatter_count": int(scatter.shape[0]),
        "volume_peak_energy": float(np.max(energy)),
        "volume_peak_xyz_m": _peak_xyz_from_energy(energy, grid),
        "note": "3D kinematic volume response proxy, not 3D elastic wavefield",
    }
    return {
        "volume_frames": frames,
        "time_axis_s": times,
        "x_axis_m": grid.x_axis_m,
        "y_axis_m": grid.y_axis_m,
        "depth_axis_m": grid.depth_axis_m,
        "energy_volume": energy,
        "metadata": metadata,
    }


def _peak_xyz_from_energy(energy: np.ndarray, grid: VolumeGrid) -> dict[str, float]:
    """返回三维能量 proxy 最大点位置。"""

    ih, iy, ix = np.unravel_index(int(np.argmax(energy)), energy.shape)
    return {
        "x_m": float(grid.x_axis_m[ix]),
        "y_m": float(grid.y_axis_m[iy]),
        "depth_m": float(grid.depth_axis_m[ih]),
    }
