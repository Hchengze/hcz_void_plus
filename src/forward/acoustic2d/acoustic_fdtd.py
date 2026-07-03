"""最小 2D scalar acoustic FDTD prototype。"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from src.forward.acoustic2d.boundary import build_sponge_damping
from src.forward.acoustic2d.diagnostics import acoustic_energy_diagnostics, check_cfl_stability
from src.forward.acoustic2d.grid import Acoustic2DGrid, build_layered_acoustic_velocity
from src.forward.acoustic2d.source import acoustic_ricker_source


@dataclass(frozen=True)
class Acoustic2DResult:
    """acoustic2d prototype 输出。"""

    shot_gather: np.ndarray
    wavefield_snapshots: np.ndarray
    snapshot_times_s: np.ndarray
    velocity_mps: np.ndarray
    cfl_info: dict[str, float | bool]
    diagnostics: dict[str, float]


def run_acoustic2d_prototype(params) -> Acoustic2DResult:
    """运行最小二维标量声学 FDTD。

    该函数只用于验证波动方程数值框架：网格、震源、接收、sponge 边界、CFL 与快照。
    它不能真实模拟 Rayleigh 波，因为 acoustic 方程没有剪切波、自由表面 Rayleigh 模式
    和弹性空洞散射机制。
    """

    grid = Acoustic2DGrid(
        nx=params.forward.acoustic2d_nx,
        nz=params.forward.acoustic2d_nz,
        dx_m=params.forward.acoustic2d_dx_m,
        dz_m=params.forward.acoustic2d_dz_m,
    )
    velocity = build_layered_acoustic_velocity(
        grid,
        params.velocity.layer_depths_m,
        params.velocity.layer_rayleigh_velocities_mps,
    )
    dt = min(params.time.dt_s, 0.5 / (np.max(velocity) * np.sqrt(1.0 / grid.dx_m**2 + 1.0 / grid.dz_m**2)))
    nt = int(np.floor(params.forward.acoustic2d_duration_s / dt)) + 1
    time_axis = np.arange(nt, dtype=float) * dt
    source = acoustic_ricker_source(time_axis, params.task.wavelet_frequency_hz)
    damping = build_sponge_damping(grid.nz, grid.nx)
    cfl_info = check_cfl_stability(velocity, dt, grid.dx_m, grid.dz_m)

    p_prev = np.zeros((grid.nz, grid.nx), dtype=float)
    p_curr = np.zeros_like(p_prev)
    p_next = np.zeros_like(p_prev)
    source_ix = grid.nx // 4
    source_iz = 2
    receiver_z = 2
    receiver_ix = np.linspace(4, grid.nx - 5, min(48, grid.nx - 8), dtype=int)
    shot_gather = np.zeros((nt, len(receiver_ix)), dtype=float)
    snapshot_indices = np.linspace(0, nt - 1, params.forward.acoustic2d_snapshot_count, dtype=int)
    snapshots = []

    coeff_x = (velocity * dt / grid.dx_m) ** 2
    coeff_z = (velocity * dt / grid.dz_m) ** 2
    for it in range(nt):
        lap_x = np.zeros_like(p_curr)
        lap_z = np.zeros_like(p_curr)
        lap_x[:, 1:-1] = p_curr[:, 2:] - 2.0 * p_curr[:, 1:-1] + p_curr[:, :-2]
        lap_z[1:-1, :] = p_curr[2:, :] - 2.0 * p_curr[1:-1, :] + p_curr[:-2, :]
        p_next = 2.0 * p_curr - p_prev + coeff_x * lap_x + coeff_z * lap_z
        p_next[source_iz, source_ix] += source[it]
        p_next *= damping
        shot_gather[it, :] = p_next[receiver_z, receiver_ix]
        if it in set(snapshot_indices.tolist()):
            snapshots.append(p_next.copy())
        p_prev, p_curr, p_next = p_curr, p_next, p_prev

    wavefield_snapshots = np.asarray(snapshots, dtype=float)
    return Acoustic2DResult(
        shot_gather=shot_gather,
        wavefield_snapshots=wavefield_snapshots,
        snapshot_times_s=time_axis[snapshot_indices],
        velocity_mps=velocity,
        cfl_info=cfl_info,
        diagnostics=acoustic_energy_diagnostics(wavefield_snapshots, shot_gather),
    )
