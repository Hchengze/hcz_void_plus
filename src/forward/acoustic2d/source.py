"""acoustic2d 震源函数。"""

from __future__ import annotations

import numpy as np

from src.forward.wavelet import ricker


def acoustic_ricker_source(time_axis: np.ndarray, dominant_frequency_hz: float, delay_s: float | None = None) -> np.ndarray:
    """生成 acoustic2d 使用的 Ricker 震源时间函数。"""

    delay = delay_s if delay_s is not None else 1.5 / dominant_frequency_hz
    return ricker(time_axis - delay, dominant_frequency_hz)
