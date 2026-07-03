"""候选异常体散射走时。"""

from __future__ import annotations

import numpy as np

from src.geometry.distance import source_scatter_receiver_path_distance
from src.model.velocity_model import UniformVelocityModel


def compute_candidate_diffraction_times(
    candidate_xyz: np.ndarray,
    source_xyz: np.ndarray,
    receiver_xyz: np.ndarray,
    velocity_model: UniformVelocityModel,
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
    path_distance = source_scatter_receiver_path_distance(source_xyz, candidate, receiver_xyz)[:, 0, :]
    return t0_s + path_distance / velocity_model.get_velocity()
