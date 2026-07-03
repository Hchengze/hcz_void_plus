"""简化 f-k / f-v 速度扇区滤波。"""

from __future__ import annotations

import numpy as np


def fk_velocity_filter(data: np.ndarray, dt_s: float, dx_m: float, velocity_min_mps: float, velocity_max_mps: float) -> np.ndarray:
    """对每炮记录做简化 f-k 速度扇区滤波。

    输入 data shape = shot × time × channel。本函数沿 time-channel 做二维 FFT，
    保留表观速度 v=|f/k| 位于给定范围内的能量。k=0 分量保留，避免整体低波数背景
    被完全抹掉。该实现只是接口和最小可用版本，不是成熟面波 FK 分离算法。
    """

    n_shot, n_time, n_channel = data.shape
    freq = np.fft.fftfreq(n_time, d=dt_s)
    wavenumber = np.fft.fftfreq(n_channel, d=dx_m)
    filtered = np.zeros_like(data)
    for i_shot in range(n_shot):
        spectrum = np.fft.fft2(data[i_shot])
        f_grid, k_grid = np.meshgrid(freq, wavenumber, indexing="ij")
        apparent_velocity = np.full_like(f_grid, np.inf, dtype=float)
        nonzero = np.abs(k_grid) > 1.0e-12
        apparent_velocity[nonzero] = np.abs(f_grid[nonzero] / k_grid[nonzero])
        mask = (apparent_velocity >= velocity_min_mps) & (apparent_velocity <= velocity_max_mps)
        mask |= ~nonzero
        filtered[i_shot] = np.real(np.fft.ifft2(spectrum * mask))
    return filtered

