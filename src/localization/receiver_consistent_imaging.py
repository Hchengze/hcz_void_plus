"""接收一致性三维成像体。

本模块使用 Stage 5K 的 ``ObservationPath3D``，沿每个 candidate 的
``source -> candidate -> receiver`` 理论散射到时从 gather 中取样并叠加。它服务三维道路
DAS-like 空洞定位主线，不使用 source->voxel 的体响应 proxy 作为定位依据。
"""

from __future__ import annotations

from typing import Any

import numpy as np

from src.forward.observation_kernel_3d import ObservationPath3D, sample_gather_along_scatter_paths
from src.localization.multi_attribute_scan import normalize_attribute_volume


EPS = 1.0e-12


def _location_from_index(index: tuple[int, int, int], x_grid: np.ndarray, y_grid: np.ndarray, depth_grid: np.ndarray) -> dict[str, float]:
    return {
        "x_m": float(x_grid[index[0]]),
        "y_m": float(y_grid[index[1]]),
        "depth_m": float(depth_grid[index[2]]),
    }


def _distance(a: dict[str, float] | None, b: dict[str, float] | None) -> float | None:
    if not a or not b:
        return None
    av = np.array([a["x_m"], a["y_m"], a["depth_m"]], dtype=float)
    bv = np.array([b["x_m"], b["y_m"], b["depth_m"]], dtype=float)
    return float(np.linalg.norm(av - bv))


def build_receiver_consistent_imaging_volume(
    observation_paths: ObservationPath3D,
    gather: np.ndarray,
    time_axis: np.ndarray,
    x_grid: np.ndarray,
    y_grid: np.ndarray,
    depth_grid: np.ndarray,
    *,
    truth_location: dict[str, float] | None = None,
    posterior_peak_location: dict[str, float] | None = None,
) -> dict[str, Any]:
    """构建 receiver-consistent imaging volume。

    输出体 shape 与 candidate grid 一致。energy/envelope/semblance/combined 都只来自
    observation kernel 的 scatter_time_s，不使用三维体响应 proxy。
    """

    shape = (len(x_grid), len(y_grid), len(depth_grid))
    sampled = sample_gather_along_scatter_paths(gather, time_axis, observation_paths)
    samples = sampled["samples"]
    valid = sampled["valid"]
    # 使用散射幅度绝对值作为接收路径权重，保留 gather 取样本身的符号给 semblance 使用。
    amp_weight = np.abs(observation_paths.scatter_amplitude)
    weighted_sample = np.where(valid, samples * amp_weight, 0.0)
    weight_sum = np.maximum(np.sum(np.where(valid, amp_weight, 0.0), axis=(0, 1)), EPS)
    energy = np.sum(weighted_sample * weighted_sample, axis=(0, 1)) / weight_sum
    envelope = np.sum(np.abs(weighted_sample), axis=(0, 1)) / weight_sum

    n_path = np.maximum(np.sum(valid, axis=(0, 1)), 1)
    coherent_sum = np.sum(np.where(valid, samples, 0.0), axis=(0, 1))
    incoherent_sum = np.sum(np.where(valid, samples * samples, 0.0), axis=(0, 1))
    semblance = (coherent_sum * coherent_sum) / np.maximum(n_path * incoherent_sum, EPS)
    semblance = np.clip(semblance, 0.0, 1.0)

    energy_volume = energy.reshape(shape)
    envelope_volume = envelope.reshape(shape)
    semblance_volume = semblance.reshape(shape)
    combined = (
        0.45 * normalize_attribute_volume(energy_volume)
        + 0.35 * normalize_attribute_volume(envelope_volume)
        + 0.20 * normalize_attribute_volume(semblance_volume)
    )
    peak_index = tuple(int(v) for v in np.unravel_index(int(np.argmax(combined)), combined.shape))
    peak_location = _location_from_index(peak_index, np.asarray(x_grid), np.asarray(y_grid), np.asarray(depth_grid))
    truth_distance = _distance(peak_location, truth_location)
    posterior_distance = _distance(peak_location, posterior_peak_location)
    return {
        "imaging_volume_energy": energy_volume,
        "imaging_volume_envelope": envelope_volume,
        "imaging_volume_semblance": semblance_volume,
        "imaging_volume_combined": combined,
        "imaging_peak_index": peak_index,
        "imaging_peak_location": peak_location,
        "imaging_peak_to_truth_distance": truth_distance,
        "imaging_peak_to_posterior_peak_distance": posterior_distance,
        "imaging_metadata": {
            "imaging_uses_receiver_consistent_paths": True,
            "imaging_uses_observation_kernel": True,
            "imaging_uses_velocity_path_integration": True,
            "imaging_uses_attenuation": observation_paths.metadata["uses_attenuation"],
            "volume_proxy_used_for_localization": False,
            "candidate_grid_shape": list(shape),
            "imaging_note": "receiver-consistent rule-based imaging volume, not FWI or 3D elastic imaging",
        },
    }
