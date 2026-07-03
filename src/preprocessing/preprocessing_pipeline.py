"""统一预处理流水线。"""

from __future__ import annotations

from types import SimpleNamespace
from typing import Any

import numpy as np

from src.preprocessing.agc import apply_agc
from src.preprocessing.bandpass import bandpass_filter
from src.preprocessing.envelope import envelope_attribute
from src.preprocessing.fk_filter import fk_velocity_filter
from src.preprocessing.trace_normalization import trace_normalization


def run_preprocessing_pipeline(data: np.ndarray, params: SimpleNamespace) -> tuple[np.ndarray, dict[str, Any]]:
    """按 params 执行预处理，并返回 processed_data 与步骤记录。

    该函数是扫描前的独立模块，不把预处理写死进 localization。所有开关和参数都来自
    main.py 的 argparse。输出 shape 始终与输入 data 相同。
    """

    processed = data.copy()
    steps: list[str] = []
    if not params.preprocessing.enabled:
        return processed, {"enabled": False, "steps": steps}
    if params.preprocessing.bandpass_enabled:
        processed = bandpass_filter(
            processed,
            params.time.dt_s,
            params.preprocessing.bandpass_low_hz,
            params.preprocessing.bandpass_high_hz,
        )
        steps.append("bandpass")
    if params.preprocessing.fk_filter_enabled:
        processed = fk_velocity_filter(
            processed,
            params.time.dt_s,
            params.fiber.channel_spacing_m,
            params.preprocessing.fk_velocity_min_mps,
            params.preprocessing.fk_velocity_max_mps,
        )
        steps.append("fk_filter")
    if params.preprocessing.agc_enabled:
        processed = apply_agc(processed, params.time.dt_s, params.preprocessing.agc_window_s)
        steps.append("agc")
    if params.preprocessing.envelope_enabled:
        processed = envelope_attribute(processed)
        steps.append("envelope")
    if params.preprocessing.trace_normalization != "none":
        processed = trace_normalization(processed, params.preprocessing.trace_normalization)
        steps.append(f"trace_normalization_{params.preprocessing.trace_normalization}")
    return processed, {"enabled": True, "steps": steps}

