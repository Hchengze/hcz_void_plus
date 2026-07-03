"""采集几何生成模块。

所有函数只接收 main.py 已解析、派生和校验后的 params 对象，不在本模块中
定义任何局部默认参数。
"""

from __future__ import annotations

from types import SimpleNamespace

import numpy as np


def check_coordinate_array(name: str, array: np.ndarray) -> None:
    """检查三维坐标数组的形状。

    物理意义：
        本项目所有点坐标都采用 x-y-z 三列表示，其中 x 沿道路和光纤方向，
        y 横穿道路方向，z 为向下为正的深度方向。

    输入参数：
        name：数组名称，用于错误信息；
        array：待检查的坐标数组，单位 m。

    输出形状：
        无返回值；若 array 不是 (n_point, 3)，抛出 ValueError。

    近似条件和限制：
        这里只检查坐标维度，不判断该点是否真实可施工或是否满足复杂城市约束。
    """

    if not isinstance(array, np.ndarray):
        raise ValueError(f"{name} 必须是 numpy.ndarray，当前类型为 {type(array)}。")
    if array.ndim != 2 or array.shape[1] != 3:
        raise ValueError(f"{name} 坐标维度错误：当前 shape={array.shape}，合理条件是 (n_point, 3)。")


def generate_receiver_xyz(params: SimpleNamespace) -> np.ndarray:
    """根据 params.derived.channel_x 生成 DAS-like 接收通道坐标。

    物理意义：
        光纤沿道路 x 方向布设，Stage 1 将每个离散通道视为点式接收器。

    输入参数：
        params：main.py 解析后的参数对象，其中 channel_x 单位 m。

    输出形状：
        receiver_xyz，shape = (n_channel, 3)，单位 m。

    近似条件和限制：
        当前是 point_receiver approximation，不是完整 DAS 仪器响应；尚未考虑
        gauge length、光纤耦合、解调和方向敏感性。
    """

    receiver_xyz = np.column_stack(
        [
            params.derived.channel_x,
            np.full(params.fiber.channel_count, params.fiber.y_m),
            np.full(params.fiber.channel_count, params.fiber.z_m),
        ]
    )
    check_coordinate_array("receiver_xyz", receiver_xyz)
    return receiver_xyz


def generate_source_xyz(params: SimpleNamespace) -> np.ndarray:
    """根据 params.derived.shot_x 生成震源坐标。

    物理意义：
        震源线近似与光纤平行，位于道路另一侧或道路边缘；若用户未给出
        source_y_m，main.py 已将其解析为 road_width_m。

    输入参数：
        params：main.py 解析后的参数对象，其中 shot_x 单位 m。

    输出形状：
        source_xyz，shape = (n_shot, 3)，单位 m。

    近似条件和限制：
        Stage 1 不模拟震源真实力学过程，只把震源作为运动学走时起点。
    """

    source_xyz = np.column_stack(
        [
            params.derived.shot_x,
            np.full(params.source.shot_count, params.source.y_m),
            np.full(params.source.shot_count, params.source.z_m),
        ]
    )
    check_coordinate_array("source_xyz", source_xyz)
    return source_xyz
