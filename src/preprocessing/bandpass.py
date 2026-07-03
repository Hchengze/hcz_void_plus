"""基础带通滤波。"""

from __future__ import annotations

import numpy as np


def bandpass_filter(data: np.ndarray, dt_s: float, low_hz: float, high_hz: float) -> np.ndarray:
    """基于 FFT 的零相位带通滤波。

    输入 data shape = shot × time × channel。这里沿时间轴做实数 FFT，并把
    low_hz 到 high_hz 之外的频率置零。该实现不依赖 scipy，适合作为本地科研原型
    的稳定基础版本。
    """

    if data.ndim != 3:
        raise ValueError(f"data shape 错误：{data.shape}，应为 shot × time × channel。")
    freq = np.fft.rfftfreq(data.shape[1], d=dt_s)
    spectrum = np.fft.rfft(data, axis=1)
    mask = (freq >= low_hz) & (freq <= high_hz)
    spectrum *= mask[None, :, None]
    return np.fft.irfft(spectrum, n=data.shape[1], axis=1)

