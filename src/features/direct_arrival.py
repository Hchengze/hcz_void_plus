"""直达波到时预测。"""

from __future__ import annotations

from types import SimpleNamespace

import numpy as np

from src.model.velocity_model import KinematicVelocityModel, compute_kinematic_travel_time


def predict_direct_arrival_times(
    params: SimpleNamespace,
    source_xyz: np.ndarray,
    receiver_xyz: np.ndarray,
    velocity_model: KinematicVelocityModel,
) -> np.ndarray:
    """预测直达瑞雷波到时。

    物理意义：
        在均匀等效瑞雷波速度假设下，直达波到时为
        t_direct = t0 + distance(source, receiver) / v_rayleigh。

    输入参数：
        source_xyz：shape = (n_shot, 3)，单位 m；
        receiver_xyz：shape = (n_channel, 3)，单位 m；
        velocity_model：速度单位 m/s。

    输出形状：
        direct_times，shape = (n_shot, n_channel)，单位 s。

    近似条件和限制：
        这是运动学预测，不包含真实道路分层、频散或复杂面波传播。
    """

    travel_time = compute_kinematic_travel_time(
        source_xyz[:, None, :],
        receiver_xyz[None, :, :],
        velocity_model,
    )
    return params.time.t0_s + travel_time
