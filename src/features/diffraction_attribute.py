"""绕射/散射局部能量属性。"""

from __future__ import annotations

import numpy as np

from src.features.local_energy import extract_window_energy


def compute_diffraction_energy_attribute(
    data: np.ndarray,
    time_axis: np.ndarray,
    predicted_diffraction_times: np.ndarray,
    half_width_s: float,
) -> np.ndarray:
    """计算候选绕射走时附近的局部能量属性。

    输入 data 的 shape 必须为 shot × time × channel。predicted_diffraction_times
    的 shape 为 shot × channel。当前属性就是局部能量，不引入复杂机器学习或
    高级滤波，便于解释和调试。
    """

    return extract_window_energy(data, time_axis, predicted_diffraction_times, half_width_s)
