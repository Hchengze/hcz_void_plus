"""候选异常体散射走时。"""

from __future__ import annotations

import numpy as np

from src.model.velocity_model import KinematicVelocityModel, compute_scatter_travel_time


def compute_candidate_diffraction_times(
    candidate_xyz: np.ndarray,
    source_xyz: np.ndarray,
    receiver_xyz: np.ndarray,
    velocity_model: KinematicVelocityModel,
    t0_s: float = 0.0,
) -> np.ndarray:
    """计算候选点的 source-candidate-receiver 理论散射走时。

    输入参数：
        candidate_xyz：shape = (3,) 或 (1, 3)，单位 m；
        source_xyz：shape = (n_shot, 3)，单位 m；
        receiver_xyz：shape = (n_channel, 3)，单位 m。

    输出形状：
        candidate_times，shape = (n_shot, n_channel)，单位 s。

    限制：
        当前是运动学等效散射走时，不是 FWI，也不是完整成像。
    """

    candidate = np.asarray(candidate_xyz, dtype=float).reshape(1, 3)
    # Stage 5A 起，候选绕射走时统一走 velocity_model 接口。均匀模型会退化为
    # source-candidate-receiver 路径距离 / v；分层和横向非均匀模型则按路径采样积分。
    travel_time = compute_scatter_travel_time(source_xyz, candidate, receiver_xyz, velocity_model)[:, 0, :]
    return t0_s + travel_time
