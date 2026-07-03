"""F1 layered / heterogeneous straight-ray kinematic forward。

这是 Stage 5B 的当前稳定正演主线。它仍然是 kinematic approximation，但所有直达
和散射走时都通过 velocity_model 的路径采样积分接口计算，因此支持 layered、
lateral_gradient、localized_low_velocity_zone 等近地表等效速度模型。
"""

from __future__ import annotations

from types import SimpleNamespace
from typing import Any

import numpy as np

from src.forward.multishot_forward import synthesize_multishot_forward
from src.model.velocity_model import build_velocity_model


FORWARD_ENGINE_NAME = "layered_kinematic"


def run_layered_kinematic_forward(
    params: SimpleNamespace,
    source_xyz: np.ndarray,
    receiver_xyz: np.ndarray,
    scatter_xyz: np.ndarray,
    scatter_weight: np.ndarray,
) -> dict[str, Any]:
    """运行 F1 分层/非均匀 straight-ray 运动学正演。

    输入仍是三维 source_xyz / receiver_xyz / scatter_xyz。函数本身不读取任何局部
    默认参数，速度模型完全来自 main.py 解析后的 params。
    """

    velocity_model = build_velocity_model(params)
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
    result["forward_stage"] = "F1"
    return result
