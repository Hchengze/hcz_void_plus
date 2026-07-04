"""elastic2d 介质模型。"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from src.forward.elastic2d.grid import Elastic2DGrid


@dataclass(frozen=True)
class Elastic2DModel:
    """二维各向同性弹性模型。

    参数包括 Vp、Vs、rho 以及 Lamé 参数 lambda、mu。当前只服务小域验证，
    不代表真实道路三维速度结构。
    """

    vp_mps: np.ndarray
    vs_mps: np.ndarray
    rho_kgm3: np.ndarray
    lambda_pa: np.ndarray
    mu_pa: np.ndarray


def _lame_from_vp_vs_rho(vp: np.ndarray, vs: np.ndarray, rho: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """由 Vp/Vs/rho 计算 Lamé 参数。"""

    mu = rho * vs**2
    lam = rho * vp**2 - 2.0 * mu
    return lam, mu


def build_uniform_elastic_model(grid: Elastic2DGrid, vp_mps: float, vs_mps: float, rho_kgm3: float) -> Elastic2DModel:
    """构建均匀半空间 elastic2d 模型。"""

    vp = np.full((grid.nz, grid.nx), float(vp_mps), dtype=float)
    vs = np.full_like(vp, float(vs_mps))
    rho = np.full_like(vp, float(rho_kgm3))
    lam, mu = _lame_from_vp_vs_rho(vp, vs, rho)
    return Elastic2DModel(vp, vs, rho, lam, mu)


def apply_void_like_anomaly(
    model: Elastic2DModel,
    grid: Elastic2DGrid,
    center_x_m: float,
    center_z_m: float,
    radius_m: float,
    vp_factor: float,
    vs_factor: float,
    rho_factor: float,
) -> Elastic2DModel:
    """施加低 Vp/低 Vs/低密度的 void-like 扰动。

    这不是几何空腔边界散射，只是把局部介质参数降低，用来观察 surface gather
    中是否出现可见散射残差。真实空洞边界条件需后续更严格 elastic solver。
    """

    x = grid.x_m[None, :]
    z = grid.z_m[:, None]
    mask = (x - center_x_m) ** 2 + (z - center_z_m) ** 2 <= radius_m**2
    vp = model.vp_mps.copy()
    vs = model.vs_mps.copy()
    rho = model.rho_kgm3.copy()
    vp[mask] *= float(vp_factor)
    vs[mask] *= float(vs_factor)
    rho[mask] *= float(rho_factor)
    lam, mu = _lame_from_vp_vs_rho(vp, vs, rho)
    return Elastic2DModel(vp, vs, rho, lam, mu)
