"""扫描得分峰值与整体对比度分析。"""

from __future__ import annotations

from typing import Any

import numpy as np


EPS = 1.0e-12


def analyze_peak_sharpness(score_volume: np.ndarray, best_index: tuple[int, int, int], neighborhood_radius: int) -> dict[str, Any]:
    """计算 best point 相对局部背景的尖锐程度。

    物理意义：
        如果一个候选异常体位置是真正由多炮绕射能量聚焦形成，得分峰往往应比周围
        候选点更集中、更突出。peak sharpness 用 best_score 与局部邻域均值的比值
        做最基础的可解释诊断。

    输入参数：
        score_volume：shape = (n_x, n_y, n_depth)，扫描得分体；
        best_index：最高得分点索引，顺序为 (ix, iy, iz)；
        neighborhood_radius：局部邻域半径，单位为网格索引。

    输出：
        dict，包含 best_score、local_background_mean、peak_sharpness。

    限制：
        该指标只描述得分体几何形态，不是统计显著性检验，也不是完整置信度。
    """

    if score_volume.ndim != 3:
        raise ValueError(f"score_volume 维度错误：当前 shape={score_volume.shape}，合理条件是 n_x × n_y × n_depth。")
    radius = int(max(neighborhood_radius, 0))
    ix, iy, iz = best_index
    best_score = float(score_volume[best_index])
    x0, x1 = max(ix - radius, 0), min(ix + radius + 1, score_volume.shape[0])
    y0, y1 = max(iy - radius, 0), min(iy + radius + 1, score_volume.shape[1])
    z0, z1 = max(iz - radius, 0), min(iz + radius + 1, score_volume.shape[2])
    local_values = score_volume[x0:x1, y0:y1, z0:z1].astype(float).ravel()
    if local_values.size <= 1:
        local_background_mean = float(np.mean(score_volume))
    else:
        # 排除最高点本身，避免只有峰值参与背景均值导致尖锐度被低估。
        local_values = np.delete(local_values, int(np.argmax(local_values)))
        local_background_mean = float(np.mean(local_values)) if local_values.size else float(np.mean(score_volume))
    peak_sharpness = best_score / max(local_background_mean, EPS)
    return {
        "best_score": best_score,
        "local_background_mean": local_background_mean,
        "peak_sharpness": float(peak_sharpness),
        "neighborhood_radius": radius,
    }


def compute_score_contrast(score_volume: np.ndarray, best_score: float | None = None) -> dict[str, float]:
    """计算最高得分相对全局背景的对比度和百分位。

    score_contrast = best_score / mean_score。score_percentile 表示 best_score 在
    全体候选点中的百分位，最高点通常接近 100%。如果得分体整体都很平坦，即使
    percentile 高，contrast 仍可能不高，这会提示结果不够稳定。
    """

    values = np.asarray(score_volume, dtype=float).ravel()
    if values.size == 0:
        raise ValueError("score_volume 为空，无法计算 score contrast。")
    actual_best = float(np.max(values) if best_score is None else best_score)
    mean_score = float(np.mean(values))
    score_contrast = actual_best / max(mean_score, EPS)
    score_percentile = float(np.mean(values <= actual_best) * 100.0)
    return {
        "mean_score": mean_score,
        "score_contrast": float(score_contrast),
        "score_percentile": score_percentile,
    }

