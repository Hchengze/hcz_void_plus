"""DAS-like 点式接收近似。"""

from __future__ import annotations

from types import SimpleNamespace

import numpy as np


def apply_point_receiver_approximation(data: np.ndarray, params: SimpleNamespace) -> np.ndarray:
    """返回点式接收近似下的 DAS-like 数据。

    物理意义：
        当前把光纤每个通道近似为一个点式接收器，记录该点处的标量波形响应。

    输入参数：
        data：shape = (n_shot, n_time, n_channel)，即 shot × time × channel；
        params：统一参数对象，包含 gauge_length_m 等 DAS-like 参数。

    输出形状：
        与输入 data 相同。

    近似条件和限制：
        当前 DAS-like response 是 point_receiver approximation；
        不是完整 DAS 仪器模拟；
        尚未完整考虑 gauge length、光纤耦合条件、解调过程和仪器响应；
        gauge length 参数当前进入 params 和 metadata，但在 point_receiver 模式下
        不参与波形计算。
    """

    expected = (params.source.shot_count, params.derived.nt, params.fiber.channel_count)
    if data.shape != expected:
        raise ValueError(f"DAS-like 数据维度错误：当前 shape={data.shape}，合理条件是 {expected}。")
    return data.copy()
