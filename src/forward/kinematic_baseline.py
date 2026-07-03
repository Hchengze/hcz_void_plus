"""F0 kinematic baseline forward。

F0 是项目最早的快速正演基线：直达事件与 source-scatter-receiver 等效散射事件
叠加 Ricker 子波。Stage 5B 后，F0 只作为快速基线和回归测试保留，不能被描述为
真实 DAS 仪器正演或真实 Rayleigh 波全波场模拟。
"""

from __future__ import annotations

from types import SimpleNamespace
from typing import Any

import numpy as np

from src.forward.multishot_forward import synthesize_multishot_forward
from src.model.velocity_model import UniformVelocityModel


FORWARD_ENGINE_NAME = "kinematic_baseline"


def run_kinematic_baseline_forward(
    params: SimpleNamespace,
    source_xyz: np.ndarray,
    receiver_xyz: np.ndarray,
    scatter_xyz: np.ndarray,
    scatter_weight: np.ndarray,
) -> dict[str, Any]:
    """运行 F0 均匀速度运动学基线正演。

    说明：
        该函数显式构造 UniformVelocityModel，只用于 baseline 对比。主流程默认不应
        依赖它作为当前最佳正演能力；Stage 5B 的稳定主线是 layered_kinematic。
    """

    velocity_model = UniformVelocityModel(params.velocity.rayleigh_velocity_mps)
    result = synthesize_multishot_forward(
        params,
        source_xyz,
        receiver_xyz,
        scatter_xyz,
        scatter_weight,
        velocity_model,
    )
    result["forward_engine"] = FORWARD_ENGINE_NAME
    result["velocity_model"] = velocity_model
    result["forward_stage"] = "F0"
    return result
