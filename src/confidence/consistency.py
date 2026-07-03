"""多炮贡献一致性诊断。"""

from __future__ import annotations

from types import SimpleNamespace
from typing import Any

import numpy as np

from src.features.local_energy import extract_window_energy
from src.localization.travel_time import compute_candidate_diffraction_times
from src.model.velocity_model import UniformVelocityModel


EPS = 1.0e-12


def compute_multishot_consistency(
    data: np.ndarray,
    time_axis: np.ndarray,
    source_xyz: np.ndarray,
    receiver_xyz: np.ndarray,
    velocity_model: UniformVelocityModel,
    best_location: dict[str, float],
    params: SimpleNamespace,
) -> dict[str, Any]:
    """计算最佳候选点处各炮贡献是否均衡。

    物理意义：
        多炮联合定位应尽量由多炮共同贡献。如果 best point 的能量几乎只来自一两炮，
        说明它可能是局部噪声、直达波残余或几何偶然聚焦造成的候选点。这里按最佳
        候选点理论绕射走时，在每炮所有通道上提取局部能量并求平均。

    输入 data：
        shape = (n_shot, n_time, n_channel)，即 shot × time × channel。

    输出：
        per_shot_scores：每炮平均局部能量；
        coefficient_of_variation：std / mean；
        warning：若 CV 超过 main.py 中的阈值，则提示多炮一致性较差。
    """

    candidate_xyz = np.array(
        [best_location["x_m"], best_location["y_m"], best_location["depth_m"]],
        dtype=float,
    )
    candidate_times = compute_candidate_diffraction_times(
        candidate_xyz,
        source_xyz,
        receiver_xyz,
        velocity_model,
        t0_s=params.time.t0_s,
    )
    energy = extract_window_energy(data, time_axis, candidate_times, params.scan.time_window_half_width_s)
    per_shot_scores = np.mean(energy, axis=1)
    mean_score = float(np.mean(per_shot_scores))
    std_score = float(np.std(per_shot_scores))
    cv = float(std_score / max(mean_score, EPS))
    warning = cv > params.confidence.consistency_warning_cv_threshold
    return {
        "per_shot_scores": per_shot_scores.tolist(),
        "mean": mean_score,
        "std": std_score,
        "coefficient_of_variation": cv,
        "warning": bool(warning),
        "warning_threshold": params.confidence.consistency_warning_cv_threshold,
    }

