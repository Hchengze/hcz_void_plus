"""Hilbert 包络属性。"""

from __future__ import annotations

import numpy as np


def envelope_attribute(data: np.ndarray) -> np.ndarray:
    """计算时间轴 Hilbert 包络；无 scipy 时使用 FFT 解析信号实现。"""

    n_time = data.shape[1]
    spectrum = np.fft.fft(data, axis=1)
    h = np.zeros(n_time, dtype=float)
    if n_time % 2 == 0:
        h[0] = h[n_time // 2] = 1.0
        h[1 : n_time // 2] = 2.0
    else:
        h[0] = 1.0
        h[1 : (n_time + 1) // 2] = 2.0
    analytic = np.fft.ifft(spectrum * h[None, :, None], axis=1)
    return np.abs(analytic)

