"""几何距离与运动学路径长度计算。"""

from __future__ import annotations

import numpy as np

from src.geometry.acquisition_geometry import check_coordinate_array


def source_receiver_distance(source_xyz: np.ndarray, receiver_xyz: np.ndarray) -> np.ndarray:
    """计算震源到 DAS-like 接收通道的直线路径距离。

    物理意义：
        Stage 1 使用等效瑞雷波速度和直线路径近似直达波走时：
        t_direct = t0 + distance(source, receiver) / v_rayleigh。

    输入参数：
        source_xyz：shape = (n_shot, 3)，单位 m；
        receiver_xyz：shape = (n_channel, 3)，单位 m。

    输出形状：
        distance，shape = (n_shot, n_channel)，单位 m。

    近似条件和限制：
        这里没有模拟真实瑞雷波沿自由表面传播的复杂路径，也没有考虑道路分层
        和频散；这是运动学近似中的几何距离。
    """

    check_coordinate_array("source_xyz", source_xyz)
    check_coordinate_array("receiver_xyz", receiver_xyz)
    diff = source_xyz[:, None, :] - receiver_xyz[None, :, :]
    distance = np.linalg.norm(diff, axis=2)
    return distance


def source_scatter_receiver_path_distance(
    source_xyz: np.ndarray, scatter_xyz: np.ndarray, receiver_xyz: np.ndarray
) -> np.ndarray:
    """计算 source-scatter-receiver 的折线路径距离。

    物理意义：
        异常体被表示为一个或多个等效散射点，散射/绕射走时采用：
        t_scatter = t0 + distance(source, scatter)/v_eff
                    + distance(scatter, receiver)/v_eff。

    输入参数：
        source_xyz：shape = (n_shot, 3)，单位 m；
        scatter_xyz：shape = (n_scatter, 3)，单位 m；
        receiver_xyz：shape = (n_channel, 3)，单位 m。

    输出形状：
        path_distance，shape = (n_shot, n_scatter, n_channel)，单位 m。

    近似条件和限制：
        多个散射点是异常体形状的运动学等效散射近似，不是真实边界散射模拟；
        当前未考虑反射系数角度依赖、模式转换或三维弹性全波场。
    """

    check_coordinate_array("source_xyz", source_xyz)
    check_coordinate_array("scatter_xyz", scatter_xyz)
    check_coordinate_array("receiver_xyz", receiver_xyz)
    source_to_scatter = np.linalg.norm(source_xyz[:, None, :] - scatter_xyz[None, :, :], axis=2)
    scatter_to_receiver = np.linalg.norm(scatter_xyz[:, None, :] - receiver_xyz[None, :, :], axis=2)
    return source_to_scatter[:, :, None] + scatter_to_receiver[None, :, :]
