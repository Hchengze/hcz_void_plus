"""自动增益控制 AGC。"""

from __future__ import annotations

import numpy as np


def apply_agc(data: np.ndarray, dt_s: float, window_s: float) -> np.ndarray:
    """滑动 RMS AGC。

    物理意义：
        AGC 用局部 RMS 对振幅归一化，使弱绕射事件更容易在图件和属性中显现。
        它会改变真实振幅关系，因此报告必须说明仅作为属性增强，不用于工程定量解释。
    """

    half = max(int(round(window_s / dt_s / 2.0)), 1)
    padded = np.pad(data * data, ((0, 0), (half, half), (0, 0)), mode="edge")
    cumsum = np.cumsum(padded, axis=1)
    window_power = cumsum[:, 2 * half :, :] - cumsum[:, : -2 * half, :]
    rms = np.sqrt(window_power / max(2 * half, 1) + 1.0e-12)
    rms = rms[:, : data.shape[1], :]
    return data / rms

