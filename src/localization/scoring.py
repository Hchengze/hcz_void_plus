"""候选点得分函数。"""

from __future__ import annotations

import numpy as np

from src.features.diffraction_attribute import compute_diffraction_energy_attribute


def score_candidate_by_diffraction_energy(
    data: np.ndarray,
    time_axis: np.ndarray,
    candidate_times: np.ndarray,
    half_width_s: float,
) -> float:
    """用理论绕射走时附近的局部能量给候选点打分。

    输入 data 的 shape 为 shot × time × channel；candidate_times 的 shape 为
    shot × channel。得分是所有炮和通道局部能量的平均值。
    """

    energy = compute_diffraction_energy_attribute(data, time_axis, candidate_times, half_width_s)
    return float(np.mean(energy))
