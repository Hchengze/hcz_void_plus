"""震源子波工具。"""

from __future__ import annotations

import numpy as np


def ricker(time_shift_s: np.ndarray, frequency_hz: float) -> np.ndarray:
    """生成 Ricker 子波。

    物理意义：
        Ricker 子波是浅层主动源正演中常用的零相位近似震源波形。这里用它
        表示锤击、落锤或小型主动源的等效时间函数。

    输入参数：
        time_shift_s：相对到时的时间轴，单位 s；0 表示子波峰值附近；
        frequency_hz：主频，单位 Hz。

    输出形状：
        与 time_shift_s 相同的一维或多维数组。

    近似条件和限制：
        这不是震源-路面耦合的真实力学模拟，只是运动学正演中的简化子波。
    """

    pi_ft = np.pi * frequency_hz * time_shift_s
    pi_ft_sq = pi_ft * pi_ft
    return (1.0 - 2.0 * pi_ft_sq) * np.exp(-pi_ft_sq)


def shifted_ricker(time_axis_s: np.ndarray, arrival_time_s: float, frequency_hz: float) -> np.ndarray:
    """在指定走时位置生成一条 Ricker 子波。

    输入参数：
        time_axis_s：记录时间轴，shape = (n_time,)，单位 s；
        arrival_time_s：目标走时，单位 s；
        frequency_hz：主频，单位 Hz。

    输出形状：
        wavelet，shape = (n_time,)。
    """

    return ricker(time_axis_s - arrival_time_s, frequency_hz)
