"""正演引擎注册表。

Stage 5B 将 forward modeling 单独确立为主线。所有正演入口通过本注册表管理，
避免 pipeline 随意调用旧函数、混淆 kinematic baseline、layered kinematic 和
wave-equation prototype。
"""

from __future__ import annotations

from dataclasses import dataclass
from types import SimpleNamespace
from typing import Any, Callable

import numpy as np

from src.forward.kinematic_baseline import run_kinematic_baseline_forward
from src.forward.layered_kinematic import run_layered_kinematic_forward


ForwardRunner = Callable[[SimpleNamespace, np.ndarray, np.ndarray, np.ndarray, np.ndarray], dict[str, Any]]


@dataclass(frozen=True)
class ForwardEngineSpec:
    """正演引擎说明。"""

    name: str
    stage: str
    runner: ForwardRunner | None
    is_default_localization_forward: bool
    description: str
    limitation: str


FORWARD_ENGINES: dict[str, ForwardEngineSpec] = {
    "kinematic_baseline": ForwardEngineSpec(
        name="kinematic_baseline",
        stage="F0",
        runner=run_kinematic_baseline_forward,
        is_default_localization_forward=False,
        description="source-scatter-receiver 运动学基线正演。",
        limitation="快速基线，不是真实波场，不考虑分层/非均匀速度主线。",
    ),
    "layered_kinematic": ForwardEngineSpec(
        name="layered_kinematic",
        stage="F1",
        runner=run_layered_kinematic_forward,
        is_default_localization_forward=True,
        description="分层/非均匀 straight-ray kinematic forward，当前主流程默认引擎。",
        limitation="路径仍为直线采样积分，不是弹性波全波场。",
    ),
    "acoustic2d_prototype": ForwardEngineSpec(
        name="acoustic2d_prototype",
        stage="F2",
        runner=None,
        is_default_localization_forward=False,
        description="二维标量 acoustic FDTD prototype，用于波动方程框架验证。",
        limitation="不能真实模拟 Rayleigh/free-surface/void scattering，不作为默认定位数据。",
    ),
}


def list_forward_engines() -> list[str]:
    """列出可识别的正演引擎名称。"""

    return list(FORWARD_ENGINES)


def get_forward_engine_spec(name: str) -> ForwardEngineSpec:
    """读取正演引擎说明；未知名称抛出中文错误。"""

    if name not in FORWARD_ENGINES:
        raise ValueError(f"未知 forward_engine：{name}，可选项为 {list_forward_engines()}")
    return FORWARD_ENGINES[name]


def run_registered_forward(
    params: SimpleNamespace,
    source_xyz: np.ndarray,
    receiver_xyz: np.ndarray,
    scatter_xyz: np.ndarray,
    scatter_weight: np.ndarray,
) -> dict[str, Any]:
    """按 params.forward.engine 调度当前主正演。

    acoustic2d_prototype 是验证型 wave-equation prototype，不直接替代 DAS-like 主流程；
    因此 full_pipeline 默认仍使用 layered_kinematic。
    """

    spec = get_forward_engine_spec(params.forward.engine)
    if spec.runner is None:
        raise ValueError(f"{spec.name} 是 validation prototype，不能作为 full_pipeline 默认主正演。")
    return spec.runner(params, source_xyz, receiver_xyz, scatter_xyz, scatter_weight)
