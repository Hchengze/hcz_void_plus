"""三维 posterior-like 体诊断。

本模块把三维 combined score volume 转换成一个可审计的 ``posterior_probability_volume``。
这里的 posterior 只是 softmax 形式的规则型诊断，用来表达“候选点相对可信度”和不确定性，
不是严格贝叶斯反演，也不能作为工程确诊概率。
"""

from __future__ import annotations

from typing import Any

import numpy as np


EPS = 1.0e-12


def score_to_posterior_probability(score_volume: np.ndarray, temperature: float = 0.2) -> np.ndarray:
    """把任意三维 score volume 转成归一化 posterior-like 概率体。

    算法说明：
    1. 先做稳健 0-1 归一化，避免原始属性量纲影响 softmax；
    2. 再使用 ``exp(score / temperature)`` 得到相对权重；
    3. 最后归一化到总和为 1。

    ``temperature`` 越小，posterior-like 体越尖锐；越大则越平滑。它是诊断参数，
    不是噪声方差或真实概率模型参数。
    """

    volume = np.asarray(score_volume, dtype=float)
    if volume.ndim != 3:
        raise ValueError(f"score_volume 必须是三维，当前 shape={volume.shape}")
    finite = volume[np.isfinite(volume)]
    if finite.size == 0:
        return np.full_like(volume, 1.0 / max(volume.size, 1), dtype=float)

    vmin = float(np.percentile(finite, 1.0))
    vmax = float(np.percentile(finite, 99.0))
    if vmax <= vmin:
        normalized = np.zeros_like(volume, dtype=float)
    else:
        normalized = np.clip((volume - vmin) / (vmax - vmin), 0.0, 1.0)

    temp = max(float(temperature), EPS)
    logits = normalized / temp
    logits = logits - float(np.nanmax(logits))
    weights = np.exp(np.where(np.isfinite(logits), logits, -60.0))
    total = float(np.sum(weights))
    if total <= EPS:
        return np.full_like(volume, 1.0 / max(volume.size, 1), dtype=float)
    return weights / total


def grid_coordinates(x_grid: np.ndarray, y_grid: np.ndarray, depth_grid: np.ndarray) -> np.ndarray:
    """生成与 score volume 展平顺序一致的三维候选坐标数组。"""

    xx, yy, zz = np.meshgrid(x_grid, y_grid, depth_grid, indexing="ij")
    return np.column_stack([xx.ravel(), yy.ravel(), zz.ravel()])


def summarize_posterior_volume(
    posterior_volume: np.ndarray,
    x_grid: np.ndarray,
    y_grid: np.ndarray,
    depth_grid: np.ndarray,
) -> dict[str, Any]:
    """提取 posterior-like 体的 peak、mean、covariance 和熵等诊断量。"""

    posterior = np.asarray(posterior_volume, dtype=float)
    if posterior.ndim != 3:
        raise ValueError(f"posterior_volume 必须是三维，当前 shape={posterior.shape}")
    total = float(np.sum(posterior))
    if total <= EPS:
        posterior = np.full_like(posterior, 1.0 / max(posterior.size, 1), dtype=float)
    else:
        posterior = posterior / total

    coords = grid_coordinates(np.asarray(x_grid), np.asarray(y_grid), np.asarray(depth_grid))
    weights = posterior.ravel()
    mean = np.sum(coords * weights[:, None], axis=0)
    centered = coords - mean[None, :]
    covariance = centered.T @ (centered * weights[:, None])
    covariance = 0.5 * (covariance + covariance.T)
    eigvals, eigvecs = np.linalg.eigh(covariance)
    order = np.argsort(eigvals)[::-1]
    eigvals = np.maximum(eigvals[order], 0.0)
    eigvecs = eigvecs[:, order]
    axes = np.sqrt(eigvals)
    peak_index = np.unravel_index(int(np.argmax(posterior)), posterior.shape)
    peak_location = {
        "x_m": float(x_grid[peak_index[0]]),
        "y_m": float(y_grid[peak_index[1]]),
        "depth_m": float(depth_grid[peak_index[2]]),
    }
    entropy = -float(np.sum(weights * np.log(np.maximum(weights, EPS))))
    effective_points = float(np.exp(entropy))
    return {
        "posterior_peak_index": tuple(int(v) for v in peak_index),
        "posterior_peak_location": peak_location,
        "posterior_mean_location": {
            "x_m": float(mean[0]),
            "y_m": float(mean[1]),
            "depth_m": float(mean[2]),
        },
        "posterior_covariance_3x3": covariance,
        "uncertainty_ellipsoid_axes": axes,
        "uncertainty_ellipsoid_vectors": eigvecs,
        "posterior_entropy": entropy,
        "posterior_effective_point_count": effective_points,
        "posterior_probability_sum": float(np.sum(posterior)),
        "posterior_like_note": "softmax rule-based posterior-like diagnostic, not strict Bayesian inversion",
    }


def build_posterior_from_score(
    score_volume: np.ndarray,
    x_grid: np.ndarray,
    y_grid: np.ndarray,
    depth_grid: np.ndarray,
    temperature: float = 0.2,
) -> dict[str, Any]:
    """从 combined score 一步生成 posterior-like 体及其摘要。"""

    posterior = score_to_posterior_probability(score_volume, temperature=temperature)
    summary = summarize_posterior_volume(posterior, x_grid, y_grid, depth_grid)
    return {
        "posterior_probability_volume": posterior,
        "posterior_summary": summary,
        **summary,
    }
