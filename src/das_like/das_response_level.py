"""DAS-like 响应层级调度。"""

from __future__ import annotations

from types import SimpleNamespace

import numpy as np

from src.das_like.point_receiver import apply_point_receiver_approximation


def apply_das_like_response(data: np.ndarray, params: SimpleNamespace) -> np.ndarray:
    """根据 params.das_like.response_level 应用 DAS-like 响应近似。"""

    if params.das_like.response_level == "point_receiver":
        return apply_point_receiver_approximation(data, params)
    raise ValueError(f"未知 das_response_level={params.das_like.response_level}。")
