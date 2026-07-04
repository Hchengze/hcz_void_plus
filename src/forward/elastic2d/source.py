"""elastic2d 震源。"""

from __future__ import annotations

import numpy as np


def elastic_ricker_force(time_axis_s: np.ndarray, frequency_hz: float) -> np.ndarray:
    """生成垂向力 Ricker 子波。

    子波峰值延迟取 1.5 / f，避免 t=0 处出现强不连续。输出会归一化，便于小网格
    validation 使用。
    """

    t0 = 1.5 / float(frequency_hz)
    arg = np.pi * float(frequency_hz) * (time_axis_s - t0)
    wavelet = (1.0 - 2.0 * arg**2) * np.exp(-(arg**2))
    peak = np.max(np.abs(wavelet))
    return wavelet / peak if peak > 0.0 else wavelet
