"""按道振幅归一化。"""

from __future__ import annotations

import numpy as np


def trace_normalization(data: np.ndarray, mode: str) -> np.ndarray:
    """按 shot-channel 道归一化，不改变数据 shape。"""

    if mode == "none":
        return data.copy()
    if mode == "rms":
        scale = np.sqrt(np.mean(data * data, axis=1, keepdims=True) + 1.0e-12)
    elif mode == "max":
        scale = np.max(np.abs(data), axis=1, keepdims=True) + 1.0e-12
    else:
        raise ValueError(f"未知 trace_normalization mode={mode}")
    return data / scale

