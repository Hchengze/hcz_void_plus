"""最小 2D velocity-stress elastic FDTD prototype。"""

from __future__ import annotations

from dataclasses import dataclass
from types import SimpleNamespace

import numpy as np

from src.forward.elastic2d.boundary import build_elastic_sponge
from src.forward.elastic2d.diagnostics import check_elastic_cfl, elastic_energy_diagnostics
from src.forward.elastic2d.grid import Elastic2DGrid
from src.forward.elastic2d.model import Elastic2DModel, apply_void_like_anomaly, build_uniform_elastic_model
from src.forward.elastic2d.source import elastic_ricker_force


@dataclass(frozen=True)
class Elastic2DResult:
    """elastic2d prototype 输出。"""

    surface_vx_gather: np.ndarray
    surface_vz_gather: np.ndarray
    wavefield_snapshots_vz: np.ndarray
    snapshot_times_s: np.ndarray
    time_axis_s: np.ndarray
    receiver_x_m: np.ndarray
    grid: Elastic2DGrid
    model: Elastic2DModel
    cfl_info: dict[str, float | bool]
    diagnostics: dict[str, float]
    source_x_m: float
    source_z_m: float
    source_type: str


def build_elastic2d_grid_from_params(params: SimpleNamespace) -> Elastic2DGrid:
    """从 main.py 参数构建 elastic2d 网格。"""

    return Elastic2DGrid(
        nx=params.forward.elastic2d_nx,
        nz=params.forward.elastic2d_nz,
        dx_m=params.forward.elastic2d_dx_m,
        dz_m=params.forward.elastic2d_dz_m,
    )


def build_elastic2d_model_from_params(params: SimpleNamespace, grid: Elastic2DGrid, with_void: bool) -> Elastic2DModel:
    """从 main.py 参数构建 elastic2d 模型。

    void-like anomaly 会被限制在局部 validation 网格内；真实三维异常体仍由主流程的
    source_xyz / receiver_xyz / candidate_xyz 表达。
    """

    model = build_uniform_elastic_model(
        grid,
        params.forward.elastic2d_vp_mps,
        params.forward.elastic2d_vs_mps,
        params.forward.elastic2d_rho_kgm3,
    )
    if not with_void or not params.forward.elastic2d_void_enabled:
        return model
    center_x = params.forward.elastic2d_void_x_m
    if center_x is None or center_x < 0.0 or center_x > grid.width_m:
        center_x = 0.62 * grid.width_m
    center_z = params.forward.elastic2d_void_z_m
    if center_z is None or center_z <= 0.0 or center_z > grid.depth_m:
        center_z = min(max(0.45 * grid.depth_m, 2.0 * grid.dz_m), grid.depth_m - 2.0 * grid.dz_m)
    return apply_void_like_anomaly(
        model,
        grid,
        center_x_m=float(center_x),
        center_z_m=float(center_z),
        radius_m=params.forward.elastic2d_void_radius_m,
        vp_factor=params.forward.elastic2d_void_vp_factor,
        vs_factor=params.forward.elastic2d_void_vs_factor,
        rho_factor=params.forward.elastic2d_void_rho_factor,
    )


def _ddx(field: np.ndarray, dx_m: float) -> np.ndarray:
    """二阶中心差分 x 导数，边界使用一阶近似。"""

    out = np.zeros_like(field)
    out[:, 1:-1] = (field[:, 2:] - field[:, :-2]) / (2.0 * dx_m)
    out[:, 0] = (field[:, 1] - field[:, 0]) / dx_m
    out[:, -1] = (field[:, -1] - field[:, -2]) / dx_m
    return out


def _ddz(field: np.ndarray, dz_m: float) -> np.ndarray:
    """二阶中心差分 z 导数，边界使用一阶近似。"""

    out = np.zeros_like(field)
    out[1:-1, :] = (field[2:, :] - field[:-2, :]) / (2.0 * dz_m)
    out[0, :] = (field[1, :] - field[0, :]) / dz_m
    out[-1, :] = (field[-1, :] - field[-2, :]) / dz_m
    return out


def run_elastic2d_prototype(params: SimpleNamespace, with_void: bool = False) -> Elastic2DResult:
    """运行最小 collocated-grid 2D elastic prototype。

    方程采用 velocity-stress 形式，变量包括 vx、vz、sxx、szz、sxz。顶部通过
    szz=sxz=0 做近似 free surface；左右和底部使用 sponge。该实现追求可审计的
    科研验证闭环，不是工业级 staggered-grid/PML elastic solver。
    """

    grid = build_elastic2d_grid_from_params(params)
    model = build_elastic2d_model_from_params(params, grid, with_void=with_void)
    dt_limit = 0.35 / (
        np.max(model.vp_mps) * np.sqrt(1.0 / grid.dx_m**2 + 1.0 / grid.dz_m**2)
    )
    dt = min(params.time.dt_s, float(dt_limit))
    nt = int(np.floor(params.forward.elastic2d_duration_s / dt)) + 1
    time_axis = np.arange(nt, dtype=float) * dt
    source = elastic_ricker_force(time_axis, params.task.wavelet_frequency_hz)
    damping = build_elastic_sponge(grid.nz, grid.nx)
    cfl_info = check_elastic_cfl(model.vp_mps, dt, grid.dx_m, grid.dz_m)

    vx = np.zeros((grid.nz, grid.nx), dtype=float)
    vz = np.zeros_like(vx)
    sxx = np.zeros_like(vx)
    szz = np.zeros_like(vx)
    sxz = np.zeros_like(vx)

    source_ix = max(2, grid.nx // 4)
    # 震源深度由 main.py 参数控制；这里限制在内部网格，避免放到 sponge 或越界点。
    source_iz = int(round(params.forward.elastic2d_source_depth_m / max(grid.dz_m, 1.0e-9)))
    source_iz = min(max(1, source_iz), grid.nz - 3)
    receiver_iz = 1
    receiver_ix = np.arange(2, grid.nx - 2, dtype=int)
    surface_vx = np.zeros((nt, len(receiver_ix)), dtype=float)
    surface_vz = np.zeros_like(surface_vx)
    snapshot_indices = np.linspace(0, nt - 1, params.forward.elastic2d_snapshot_count, dtype=int)
    snapshots = []

    inv_rho = 1.0 / np.maximum(model.rho_kgm3, 1.0e-9)
    for it in range(nt):
        # 动量方程：应力散度更新速度。collocated-grid 简化便于审计，但不是高精度工业格式。
        vx += dt * (_ddx(sxx, grid.dx_m) + _ddz(sxz, grid.dz_m)) * inv_rho
        vz += dt * (_ddx(sxz, grid.dx_m) + _ddz(szz, grid.dz_m)) * inv_rho
        # 三种最小震源机制都只服务 validation，不进入 layered_kinematic 主定位 forward。
        # vertical_force 更接近锤击竖向力；horizontal_force 用来增强沿光纤切向 vx；
        # explosive 是简化体积源，用于检查 pressure-like 响应，不代表真实 Rayleigh 激发。
        source_value = dt * source[it] / max(model.rho_kgm3[source_iz, source_ix], 1.0e-9)
        if params.forward.elastic2d_source_type == "horizontal_force":
            vx[source_iz, source_ix] += source_value
        elif params.forward.elastic2d_source_type == "explosive":
            sxx[source_iz, source_ix] += source[it]
            szz[source_iz, source_ix] += source[it]
        else:
            vz[source_iz, source_ix] += source_value

        dvx_dx = _ddx(vx, grid.dx_m)
        dvz_dz = _ddz(vz, grid.dz_m)
        dvx_dz = _ddz(vx, grid.dz_m)
        dvz_dx = _ddx(vz, grid.dx_m)
        # 本构方程：速度梯度更新应力。
        sxx += dt * ((model.lambda_pa + 2.0 * model.mu_pa) * dvx_dx + model.lambda_pa * dvz_dz)
        szz += dt * (model.lambda_pa * dvx_dx + (model.lambda_pa + 2.0 * model.mu_pa) * dvz_dz)
        sxz += dt * model.mu_pa * (dvx_dz + dvz_dx)

        # 顶部近似自由表面：法向和切向牵引置零。该处理足以做 Rayleigh-like sanity check，
        # 但不是严格高阶自由表面边界。
        szz[0, :] = 0.0
        sxz[0, :] = 0.0

        vx *= damping
        vz *= damping
        sxx *= damping
        szz *= damping
        sxz *= damping

        surface_vx[it, :] = vx[receiver_iz, receiver_ix]
        surface_vz[it, :] = vz[receiver_iz, receiver_ix]
        if it in set(snapshot_indices.tolist()):
            snapshots.append(vz.copy())

    snapshots_array = np.asarray(snapshots, dtype=float)
    diagnostics = elastic_energy_diagnostics(surface_vz, snapshots_array)
    return Elastic2DResult(
        surface_vx_gather=surface_vx,
        surface_vz_gather=surface_vz,
        wavefield_snapshots_vz=snapshots_array,
        snapshot_times_s=time_axis[snapshot_indices],
        time_axis_s=time_axis,
        receiver_x_m=grid.x_m[receiver_ix],
        grid=grid,
        model=model,
        cfl_info=cfl_info,
        diagnostics=diagnostics,
        source_x_m=grid.x_m[source_ix],
        source_z_m=grid.z_m[source_iz],
        source_type=params.forward.elastic2d_source_type,
    )
