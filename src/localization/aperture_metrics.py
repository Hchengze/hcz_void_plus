"""三维观测几何孔径指标。

这些指标用于判断 source_xyz、receiver_xyz 和 candidate_xyz 的三维照明条件。
它们可以作为 uncertainty 诊断或辅助权重，但 Stage 5I 默认不让它们替代主 score。
"""

from __future__ import annotations

import numpy as np


def aperture_angle_for_candidate(source_xyz: np.ndarray, receiver_xyz: np.ndarray, candidate_xyz: np.ndarray) -> np.ndarray:
    """计算每个 source-receiver 对在候选点处张开的孔径角，单位为度。"""

    source = np.asarray(source_xyz, dtype=float)
    receiver = np.asarray(receiver_xyz, dtype=float)
    candidate = np.asarray(candidate_xyz, dtype=float).reshape(1, 1, 3)
    vec_s = source[:, None, :] - candidate
    vec_r = receiver[None, :, :] - candidate
    norm_s = np.linalg.norm(vec_s, axis=-1)
    norm_r = np.linalg.norm(vec_r, axis=-1)
    dot = np.sum(vec_s * vec_r, axis=-1)
    cos_angle = dot / np.maximum(norm_s * norm_r, 1.0e-12)
    return np.degrees(np.arccos(np.clip(cos_angle, -1.0, 1.0)))


def summarize_aperture(source_xyz: np.ndarray, receiver_xyz: np.ndarray, candidate_xyz: np.ndarray) -> dict[str, float]:
    """给单个候选点计算孔径角、照明数量和横向/深度模糊指标。"""

    angles = aperture_angle_for_candidate(source_xyz, receiver_xyz, candidate_xyz)
    candidate = np.asarray(candidate_xyz, dtype=float)
    receiver = np.asarray(receiver_xyz, dtype=float)
    source = np.asarray(source_xyz, dtype=float)
    useful = angles > 5.0
    y_offsets = np.abs(np.concatenate([receiver[:, 1] - candidate[1], source[:, 1] - candidate[1]]))
    depth = max(float(candidate[2]), 1.0e-6)
    lateral_ambiguity = float(1.0 / (1.0 + np.std(y_offsets) / depth))
    depth_ambiguity = float(1.0 / (1.0 + np.std(angles) / 30.0))
    return {
        "aperture_angle_mean_deg": float(np.mean(angles)),
        "aperture_angle_max_deg": float(np.max(angles)),
        "aperture_angle_std_deg": float(np.std(angles)),
        "candidate_illumination_count": int(np.count_nonzero(useful)),
        "lateral_ambiguity_index": lateral_ambiguity,
        "depth_ambiguity_index": depth_ambiguity,
        "y_depth_resolution_indicator": float((1.0 - lateral_ambiguity) * (1.0 - depth_ambiguity)),
    }
