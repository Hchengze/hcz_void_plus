"""直达瑞雷波运动学模拟。"""

from __future__ import annotations

from types import SimpleNamespace

import numpy as np

from src.forward.wavelet import shifted_ricker
from src.geometry.distance import source_receiver_distance
from src.model.velocity_model import UniformVelocityModel


def simulate_direct_wave(
    params: SimpleNamespace,
    source_xyz: np.ndarray,
    receiver_xyz: np.ndarray,
    velocity_model: UniformVelocityModel,
) -> np.ndarray:
    """生成多炮直达瑞雷波记录。

    物理意义：
        对每一个炮点和每一个 DAS-like 通道，按
        t_direct = t0 + distance(source, receiver) / v_rayleigh
        计算直达瑞雷波到时，并在对应时间位置叠加 Ricker 子波。

    输入参数：
        params：统一参数对象；
        source_xyz：shape = (n_shot, 3)，单位 m；
        receiver_xyz：shape = (n_channel, 3)，单位 m；
        velocity_model：均匀等效瑞雷波速度模型，速度单位 m/s。

    输出形状：
        data，shape = (n_shot, n_time, n_channel)，即 shot × time × channel。

    近似条件和限制：
        当前采用运动学走时和简单几何扩散，振幅约按 1/sqrt(distance+1) 衰减。
        这不是完整三维弹性波全波场模拟。
    """

    time_axis = params.derived.time_axis
    n_shot = source_xyz.shape[0]
    n_time = params.derived.nt
    n_channel = receiver_xyz.shape[0]
    velocity = velocity_model.get_velocity()
    distances = source_receiver_distance(source_xyz, receiver_xyz)
    data = np.zeros((n_shot, n_time, n_channel), dtype=float)

    for i_shot in range(n_shot):
        for i_channel in range(n_channel):
            arrival = params.time.t0_s + distances[i_shot, i_channel] / velocity
            amplitude = 1.0 / np.sqrt(distances[i_shot, i_channel] + 1.0)
            data[i_shot, :, i_channel] += amplitude * shifted_ricker(
                time_axis, arrival, params.task.wavelet_frequency_hz
            )
    return data
