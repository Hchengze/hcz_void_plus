"""最小 staggered-grid velocity-stress elastic2d benchmark。"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from src.forward.elastic2d.model import build_uniform_elastic_model
from src.forward.elastic2d.source import elastic_ricker_force
from src.forward.elastic2d.staggered_boundary import apply_staggered_free_surface, build_staggered_sponge
from src.forward.elastic2d.staggered_diagnostics import check_staggered_elastic_cfl, staggered_energy_diagnostics
from src.forward.elastic2d.staggered_grid import StaggeredGrid2D, build_staggered_grid_from_params


@dataclass(frozen=True)
class StaggeredElastic2DResult:
    """staggered-grid benchmark 输出。"""

    surface_vx_gather: np.ndarray
    surface_vz_gather: np.ndarray
    wavefield_snapshots_vz: np.ndarray
    snapshot_times_s: np.ndarray
    time_axis_s: np.ndarray
    receiver_x_m: np.ndarray
    grid: StaggeredGrid2D
    cfl_info: dict
    diagnostics: dict
    source_x_m: float
    source_z_m: float
    source_type: str
    free_surface_mode: str
    boundary_mode: str
    scheme: str = "staggered"


def _dz_vx_to_sxz(vx: np.ndarray, dz: float) -> np.ndarray:
    out = np.zeros((vx.shape[0] + 1, vx.shape[1]), dtype=float)
    out[1:-1, :] = (vx[1:, :] - vx[:-1, :]) / dz
    return out


def _dx_vz_to_sxz(vz: np.ndarray, dx: float) -> np.ndarray:
    out = np.zeros((vz.shape[0], vz.shape[1] + 1), dtype=float)
    out[:, 1:-1] = (vz[:, 1:] - vz[:, :-1]) / dx
    return out


def _sxz_z_to_vx(sxz: np.ndarray, dz: float) -> np.ndarray:
    return (sxz[1:, :] - sxz[:-1, :]) / dz


def _sxz_x_to_vz(sxz: np.ndarray, dx: float) -> np.ndarray:
    return (sxz[:, 1:] - sxz[:, :-1]) / dx


def run_staggered_elastic2d_prototype(params, *, source_type: str | None = None) -> StaggeredElastic2DResult:
    """运行最小 staggered-grid elastic2d benchmark。

    该实现用于 Stage 5F benchmark。它具备错格变量位置和 CFL/快照输出，但仍是
    小网格科研原型，不是工业级 PML/staggered solver。
    """

    grid = build_staggered_grid_from_params(params)
    model = build_uniform_elastic_model(
        grid,
        params.forward.elastic2d_vp_mps,
        params.forward.elastic2d_vs_mps,
        params.forward.elastic2d_rho_kgm3,
    )
    dt_limit = 0.32 / (
        np.max(model.vp_mps) * np.sqrt(1.0 / grid.dx_m**2 + 1.0 / grid.dz_m**2)
    )
    dt = min(params.time.dt_s, float(dt_limit))
    nt = int(np.floor(params.forward.elastic2d_duration_s / dt)) + 1
    time_axis = np.arange(nt, dtype=float) * dt
    cfl_info = check_staggered_elastic_cfl(model.vp_mps, dt, grid.dx_m, grid.dz_m)
    sponge = build_staggered_sponge(grid, params.forward.elastic2d_sponge_strength_mode)
    wavelet = elastic_ricker_force(time_axis, params.task.wavelet_frequency_hz)

    vx = np.zeros((grid.nz, grid.nx + 1), dtype=float)
    vz = np.zeros((grid.nz + 1, grid.nx), dtype=float)
    sxx = np.zeros((grid.nz, grid.nx), dtype=float)
    szz = np.zeros_like(sxx)
    sxz = np.zeros((grid.nz + 1, grid.nx + 1), dtype=float)

    source_ix = max(2, grid.nx // 4)
    source_iz = int(round(params.forward.elastic2d_source_depth_m / max(grid.dz_m, 1.0e-9)))
    source_iz = min(max(1, source_iz), grid.nz - 3)
    source_kind = source_type or params.forward.elastic2d_source_type
    receiver_iz = 1
    receiver_ix = np.arange(2, grid.nx - 2, dtype=int)
    surface_vx = np.zeros((nt, len(receiver_ix)), dtype=float)
    surface_vz = np.zeros_like(surface_vx)
    snapshot_indices = np.linspace(0, nt - 1, params.forward.elastic2d_snapshot_count, dtype=int)
    snapshots = []

    inv_rho = 1.0 / np.maximum(model.rho_kgm3, 1.0e-9)
    for it in range(nt):
        dsxx_dx = np.zeros_like(vx)
        dsxx_dx[:, 1:-1] = (sxx[:, 1:] - sxx[:, :-1]) / grid.dx_m
        dsxz_dz = _sxz_z_to_vx(sxz, grid.dz_m)
        vx += dt * (dsxx_dx + dsxz_dz) * np.pad(inv_rho, ((0, 0), (0, 1)), mode="edge")

        dszz_dz = np.zeros_like(vz)
        dszz_dz[1:-1, :] = (szz[1:, :] - szz[:-1, :]) / grid.dz_m
        dsxz_dx = _sxz_x_to_vz(sxz, grid.dx_m)
        vz += dt * (dszz_dz + dsxz_dx) * np.pad(inv_rho, ((0, 1), (0, 0)), mode="edge")

        value = dt * wavelet[it] / max(model.rho_kgm3[source_iz, source_ix], 1.0e-9)
        if source_kind == "horizontal_force":
            vx[source_iz, source_ix] += value
        elif source_kind == "explosive":
            sxx[source_iz, source_ix] += wavelet[it]
            szz[source_iz, source_ix] += wavelet[it]
        else:
            vz[source_iz, source_ix] += value

        dvx_dx = (vx[:, 1:] - vx[:, :-1]) / grid.dx_m
        dvz_dz = (vz[1:, :] - vz[:-1, :]) / grid.dz_m
        sxx += dt * ((model.lambda_pa + 2.0 * model.mu_pa) * dvx_dx + model.lambda_pa * dvz_dz)
        szz += dt * (model.lambda_pa * dvx_dx + (model.lambda_pa + 2.0 * model.mu_pa) * dvz_dz)
        sxz += dt * np.pad(model.mu_pa, ((0, 1), (0, 1)), mode="edge") * (
            _dz_vx_to_sxz(vx, grid.dz_m) + _dx_vz_to_sxz(vz, grid.dx_m)
        )

        mode = "traction_free_variant" if params.forward.elastic2d_free_surface_mode == "stress_zero_variant" else "approximate"
        apply_staggered_free_surface(szz, sxz, mode)
        vx *= sponge["vx"]
        vz *= sponge["vz"]
        sxx *= sponge["stress"]
        szz *= sponge["stress"]
        sxz *= sponge["sxz"]

        surface_vx[it, :] = vx[receiver_iz, receiver_ix]
        surface_vz[it, :] = vz[receiver_iz, receiver_ix]
        if it in set(snapshot_indices.tolist()):
            snapshots.append(0.5 * (vz[:-1, :] + vz[1:, :]))

    snapshots_array = np.asarray(snapshots, dtype=float)
    return StaggeredElastic2DResult(
        surface_vx_gather=surface_vx,
        surface_vz_gather=surface_vz,
        wavefield_snapshots_vz=snapshots_array,
        snapshot_times_s=time_axis[snapshot_indices],
        time_axis_s=time_axis,
        receiver_x_m=grid.x_m[receiver_ix],
        grid=grid,
        cfl_info=cfl_info,
        diagnostics=staggered_energy_diagnostics(surface_vz, snapshots_array),
        source_x_m=grid.x_m[source_ix],
        source_z_m=grid.z_m[source_iz],
        source_type=source_kind,
        free_surface_mode=params.forward.elastic2d_free_surface_mode,
        boundary_mode=params.forward.elastic2d_sponge_strength_mode,
    )
