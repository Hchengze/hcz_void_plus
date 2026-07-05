"""直达瑞雷波运动学模拟。"""

from __future__ import annotations

from types import SimpleNamespace

import numpy as np

from src.forward.amplitude_model import compute_direct_amplitude
from src.forward.wavelet import shifted_ricker
from src.model.velocity_model import KinematicVelocityModel, compute_kinematic_travel_time


def simulate_direct_wave(
    params: SimpleNamespace,
    source_xyz: np.ndarray,
    receiver_xyz: np.ndarray,
    velocity_model: KinematicVelocityModel,
) -> np.ndarray:
    """生成多炮直达瑞雷波记录。

    物理意义：
        对每一个炮点和每一个 DAS-like 通道，通过 velocity_model 的
        straight-ray 路径采样积分接口计算直达波到时，并在对应时间位置叠加
        Ricker 子波。uniform 模型会退化为 distance / v；layered 或 heterogeneous
        模型会沿路径采样局部速度。

    输入参数：
        params：统一参数对象；
        source_xyz：shape = (n_shot, 3)，单位 m；
        receiver_xyz：shape = (n_channel, 3)，单位 m；
        velocity_model：统一运动学速度模型对象，支持 uniform/layered/heterogeneous。

    输出形状：
        data，shape = (n_shot, n_time, n_channel)，即 shot × time × channel。

    近似条件和限制：
        当前采用运动学走时、几何扩散和经验 Q attenuation。
        这不是完整三维弹性波全波场模拟。
    """

    time_axis = params.derived.time_axis
    n_shot = source_xyz.shape[0]
    n_time = params.derived.nt
    n_channel = receiver_xyz.shape[0]
    travel_times = compute_kinematic_travel_time(
        source_xyz[:, None, :],
        receiver_xyz[None, :, :],
        velocity_model,
    )
    amplitudes = compute_direct_amplitude(
        params,
        source_xyz[:, None, :],
        receiver_xyz[None, :, :],
        travel_times,
    )
    data = np.zeros((n_shot, n_time, n_channel), dtype=float)

    for i_shot in range(n_shot):
        for i_channel in range(n_channel):
            # Stage 5A 后，直达波到时不再强制 distance / 单一速度，而是通过
            # velocity_model 的 straight-ray 采样积分获得。均匀模型会退化回
            # distance / v；分层和非均匀模型会体现局部速度差异。
            arrival = params.time.t0_s + travel_times[i_shot, i_channel]
            # Stage 5J 后，振幅不再只看几何扩散，而是经过 amplitude_model 统一计算。
            amplitude = amplitudes[i_shot, i_channel]
            data[i_shot, :, i_channel] += amplitude * shifted_ricker(
                time_axis, arrival, params.task.wavelet_frequency_hz
            )
    return data
