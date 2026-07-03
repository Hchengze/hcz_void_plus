"""异常体等效散射/绕射波运动学模拟。"""

from __future__ import annotations

from types import SimpleNamespace

import numpy as np

from src.forward.wavelet import shifted_ricker
from src.geometry.distance import source_scatter_receiver_path_distance
from src.model.velocity_model import KinematicVelocityModel, compute_scatter_travel_time


def simulate_scatter_wave(
    params: SimpleNamespace,
    source_xyz: np.ndarray,
    receiver_xyz: np.ndarray,
    scatter_xyz: np.ndarray,
    scatter_weight: np.ndarray,
    velocity_model: KinematicVelocityModel,
) -> np.ndarray:
    """生成异常体等效散射/绕射波记录。

    物理意义：
        异常体被离散为一个或多个等效散射点。每条 source-scatter-receiver
        路径通过 velocity_model 的 straight-ray 路径采样积分接口计算到时，
        并叠加 Ricker 子波。uniform 模型会退化为两段 distance / v；分层和
        非均匀模型会沿两段三维路径积分局部速度。

    输入参数：
        params：统一参数对象；
        source_xyz：shape = (n_shot, 3)，单位 m；
        receiver_xyz：shape = (n_channel, 3)，单位 m；
        scatter_xyz：shape = (n_scatter, 3)，单位 m；
        scatter_weight：shape = (n_scatter,)，无量纲相对散射强度；
        velocity_model：统一运动学速度模型对象，支持 uniform/layered/heterogeneous。

    输出形状：
        data，shape = (n_shot, n_time, n_channel)，即 shot × time × channel。

    近似条件和限制：
        多散射点只是运动学等效散射近似，不是真实边界散射、模式转换或完整
        三维弹性全波场。几何扩散采用 1/sqrt(path+1) 的简化振幅衰减。
    """

    time_axis = params.derived.time_axis
    n_shot = source_xyz.shape[0]
    n_time = params.derived.nt
    n_channel = receiver_xyz.shape[0]
    path_distance = source_scatter_receiver_path_distance(source_xyz, scatter_xyz, receiver_xyz)
    travel_times = compute_scatter_travel_time(source_xyz, scatter_xyz, receiver_xyz, velocity_model)
    data = np.zeros((n_shot, n_time, n_channel), dtype=float)

    for i_shot in range(n_shot):
        for i_scatter in range(scatter_xyz.shape[0]):
            for i_channel in range(n_channel):
                path = path_distance[i_shot, i_scatter, i_channel]
                # 散射波走时通过 source->scatter 与 scatter->receiver 两段路径分别积分。
                # 对 layered / heterogeneous 模型，异常体深度和局部低速会改变该走时；
                # 但路径仍是直线段，因此仍属于运动学近似。
                arrival = params.time.t0_s + travel_times[i_shot, i_scatter, i_channel]
                amplitude = scatter_weight[i_scatter] / np.sqrt(path + 1.0)
                data[i_shot, :, i_channel] += amplitude * shifted_ricker(
                    time_axis, arrival, params.task.wavelet_frequency_hz
                )
    return data
