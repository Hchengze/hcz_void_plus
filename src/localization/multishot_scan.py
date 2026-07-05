"""x-y-h 多炮基础扫描定位。"""

from __future__ import annotations

from types import SimpleNamespace
from typing import Any

import numpy as np

from src.forward.observation_kernel_3d import build_observation_paths_3d, candidate_grid_to_xyz
from src.localization.attribute_scoring import score_candidate_attributes
from src.localization.geometry_sensitivity import compute_geometry_resolution_volume
from src.localization.multi_attribute_scan import build_multi_attribute_score_volumes, score_weights_from_params
from src.localization.posterior_volume import build_posterior_from_score
from src.localization.receiver_consistent_imaging import build_receiver_consistent_imaging_volume
from src.localization.recommendation_3d import build_posterior_recommendation
from src.localization.scan_velocity_model_audit import run_scan_velocity_model_audit
from src.localization.uncertainty_volume import high_probability_region, summarize_uncertainty_volume
from src.model.attenuation_model import build_attenuation_model
from src.model.velocity_model import KinematicVelocityModel
from src.physics.rayleigh import estimate_penetration_depth, rayleigh_depth_weight


def _build_energy_cumulative(data: np.ndarray) -> np.ndarray:
    """预计算 data^2 沿时间轴的累计和，用于快速窗口能量查询。"""

    energy_data = data * data
    return np.concatenate(
        [np.zeros((data.shape[0], 1, data.shape[2]), dtype=float), np.cumsum(energy_data, axis=1)],
        axis=1,
    )


def _score_candidate_fast(
    cumulative_energy: np.ndarray,
    time_axis: np.ndarray,
    candidate_times: np.ndarray,
    half_width_s: float,
) -> float:
    """用预计算累计能量快速计算候选点得分。

    candidate_times 的 shape 为 shot × channel。通过累计和查询窗口能量，避免对
    每个候选点重复扫描完整 time 轴。
    """

    n_shot = cumulative_energy.shape[0]
    n_time = cumulative_energy.shape[1] - 1
    n_channel = cumulative_energy.shape[2]
    dt = float(time_axis[1] - time_axis[0]) if len(time_axis) > 1 else 1.0
    half_samples = int(np.ceil(half_width_s / dt))
    center_index = np.rint((candidate_times - time_axis[0]) / dt).astype(int)
    start = np.clip(center_index - half_samples, 0, n_time)
    stop = np.clip(center_index + half_samples + 1, 0, n_time)
    valid = stop > start
    shot_index = np.arange(n_shot)[:, None]
    channel_index = np.arange(n_channel)[None, :]
    energy = cumulative_energy[shot_index, stop, channel_index] - cumulative_energy[shot_index, start, channel_index]
    energy[~valid] = 0.0
    return float(np.mean(energy))


def _score_candidate_normalized_fast(
    cumulative_energy: np.ndarray,
    trace_energy: np.ndarray,
    time_axis: np.ndarray,
    candidate_times: np.ndarray,
    half_width_s: float,
) -> float:
    """计算归一化局部能量堆叠得分。

    与 diffraction_energy_stack 直接平均窗口能量不同，本函数先把每个 shot-channel
    的窗口能量除以该道全记录能量，再对所有炮和通道平均。这样可以降低强能量炮、
    强能量通道或残余直达波对扫描结果的支配，使得得分更接近“沿候选绕射曲线能量
    是否相对增强”的属性。

    限制：
        这仍然是运动学局部能量属性，不是匹配滤波成像，也不是 FWI。
    """

    n_shot = cumulative_energy.shape[0]
    n_time = cumulative_energy.shape[1] - 1
    n_channel = cumulative_energy.shape[2]
    dt = float(time_axis[1] - time_axis[0]) if len(time_axis) > 1 else 1.0
    half_samples = int(np.ceil(half_width_s / dt))
    center_index = np.rint((candidate_times - time_axis[0]) / dt).astype(int)
    start = np.clip(center_index - half_samples, 0, n_time)
    stop = np.clip(center_index + half_samples + 1, 0, n_time)
    valid = stop > start
    shot_index = np.arange(n_shot)[:, None]
    channel_index = np.arange(n_channel)[None, :]
    energy = cumulative_energy[shot_index, stop, channel_index] - cumulative_energy[shot_index, start, channel_index]
    normalized_energy = energy / np.maximum(trace_energy, 1.0e-12)
    normalized_energy[~valid] = 0.0
    return float(np.mean(normalized_energy))


def _best_from_volume(
    score_volume: np.ndarray,
    x_grid: np.ndarray,
    y_grid: np.ndarray,
    depth_grid: np.ndarray,
    truth: np.ndarray,
) -> dict[str, Any]:
    """从任意 score volume 提取最高分位置及真值误差。

    该工具用于同时分析 raw score 和 depth-weighted score，避免把深度权重后的结果
    误当成唯一定位结果。返回的 location 仍然只是科研级候选位置。
    """

    best_index = np.unravel_index(int(np.argmax(score_volume)), score_volume.shape)
    best_location = {
        "x_m": float(x_grid[best_index[0]]),
        "y_m": float(y_grid[best_index[1]]),
        "depth_m": float(depth_grid[best_index[2]]),
    }
    best = np.array([best_location["x_m"], best_location["y_m"], best_location["depth_m"]], dtype=float)
    truth_error = {
        "dx_m": float(best[0] - truth[0]),
        "dy_m": float(best[1] - truth[1]),
        "ddepth_m": float(best[2] - truth[2]),
        "distance_m": float(np.linalg.norm(best - truth)),
    }
    return {
        "best_index": tuple(int(v) for v in best_index),
        "best_location": best_location,
        "best_score": float(score_volume[best_index]),
        "truth_error": truth_error,
    }


def _normalize_volume(score_volume: np.ndarray) -> np.ndarray:
    """将得分体归一化到 0-1，用于绘图，不改变实际扫描分数。"""

    max_score = float(np.max(score_volume))
    min_score = float(np.min(score_volume))
    if max_score > min_score:
        return (score_volume - min_score) / (max_score - min_score)
    return np.zeros_like(score_volume)


def run_multishot_scan(
    data: np.ndarray,
    time_axis: np.ndarray,
    source_xyz: np.ndarray,
    receiver_xyz: np.ndarray,
    velocity_model: KinematicVelocityModel,
    scan_grid: dict[str, Any],
    params: SimpleNamespace,
) -> dict[str, Any]:
    """运行基础 x-y-h 多炮扫描定位。

    扫描逻辑：
        1. 遍历候选异常体位置 x-y-h 网格；
        2. 计算 source -> candidate -> receiver 理论散射走时；
        3. 在 DAS-like 数据中沿该走时时间窗提取局部能量；
        4. 对所有 shot 和 channel 求平均，得到候选点 score；
        5. 形成 score_volume，shape = n_x, n_y, n_depth；
        6. 最高得分位置作为 best_location，并计算与单异常体真值的距离误差。

    限制：
        当前是基于运动学等效散射和局部能量聚焦的基础扫描，不是 FWI，不是完整
        成像，也不能作为工程确诊。单侧 DAS 几何下 y-depth 可能存在耦合。
    """

    x_grid = scan_grid["x_grid"]
    y_grid = scan_grid["y_grid"]
    depth_grid = scan_grid["depth_grid"]
    candidate_xyz_table = candidate_grid_to_xyz(x_grid, y_grid, depth_grid)
    attenuation_model = build_attenuation_model(params)
    observation_paths = build_observation_paths_3d(
        source_xyz,
        receiver_xyz,
        candidate_xyz_table,
        velocity_model,
        attenuation_model,
        params,
    )
    score_volume_unweighted = np.zeros((len(x_grid), len(y_grid), len(depth_grid)), dtype=float)
    attribute_volumes = {
        "energy_score": np.zeros_like(score_volume_unweighted),
        "normalized_energy_score": np.zeros_like(score_volume_unweighted),
        "matched_wavelet_score": np.zeros_like(score_volume_unweighted),
        "semblance_score": np.zeros_like(score_volume_unweighted),
        "frequency_shift_score": np.zeros_like(score_volume_unweighted),
    }
    cumulative_energy = _build_energy_cumulative(data)
    trace_energy = cumulative_energy[:, -1, :]
    penetration_depth_m = estimate_penetration_depth(params)
    attribute_weights = score_weights_from_params(params)
    multi_attribute_enabled = bool(
        getattr(params.scan, "use_multi_attribute", params.scan.score_mode == "multi_attribute")
        or params.scan.score_mode == "multi_attribute"
    )

    for ix, x_m in enumerate(x_grid):
        for iy, y_m in enumerate(y_grid):
            for iz, depth_m in enumerate(depth_grid):
                candidate_index = np.ravel_multi_index((ix, iy, iz), score_volume_unweighted.shape)
                candidate_times = observation_paths.scatter_time_s[:, :, candidate_index]
                if multi_attribute_enabled:
                    attrs = score_candidate_attributes(
                        data,
                        cumulative_energy,
                        trace_energy,
                        time_axis,
                        candidate_times,
                        params.scan.time_window_half_width_s,
                        params.task.wavelet_frequency_hz,
                        params.scan.weight_frequency_shift > 0,
                    )
                    for name, value in attrs.items():
                        attribute_volumes[name][ix, iy, iz] = value
                elif params.scan.score_method == "normalized_energy_stack":
                    score_volume_unweighted[ix, iy, iz] = _score_candidate_normalized_fast(
                        cumulative_energy,
                        trace_energy,
                        time_axis,
                        candidate_times,
                        params.scan.time_window_half_width_s,
                    )
                else:
                    score_volume_unweighted[ix, iy, iz] = _score_candidate_fast(
                        cumulative_energy, time_axis, candidate_times, params.scan.time_window_half_width_s
                    )

    multi_attribute_volumes: dict[str, Any] = {}
    if multi_attribute_enabled:
        multi_attribute_volumes = build_multi_attribute_score_volumes(
            attribute_volumes,
            attribute_weights,
            normalization=getattr(params.scan, "attribute_normalization", "robust_minmax"),
        )
        score_volume_unweighted = multi_attribute_volumes["score_volume_combined"]

    truth_location = {"x_m": float(params.anomaly.x0_m), "y_m": float(params.anomaly.y0_m), "depth_m": float(params.anomaly.depth_m)}
    receiver_imaging = build_receiver_consistent_imaging_volume(
        observation_paths,
        data,
        time_axis,
        x_grid,
        y_grid,
        depth_grid,
        truth_location=truth_location,
    )
    posterior_input_volume = (
        0.65 * _normalize_volume(score_volume_unweighted)
        + 0.35 * _normalize_volume(receiver_imaging["imaging_volume_combined"])
    )
    depth_weights = rayleigh_depth_weight(depth_grid, penetration_depth_m)
    score_volume_depth_weighted = score_volume_unweighted * depth_weights[None, None, :]
    if params.scan.active_score_kind == "depth_weighted":
        score_volume_active = score_volume_depth_weighted
        score_volume_kind = "depth_weighted"
    else:
        score_volume_active = score_volume_unweighted
        score_volume_kind = "multi_attribute_unweighted" if params.scan.score_mode == "multi_attribute" else "unweighted"

    truth = np.array([params.anomaly.x0_m, params.anomaly.y0_m, params.anomaly.depth_m], dtype=float)
    unweighted_best = _best_from_volume(score_volume_unweighted, x_grid, y_grid, depth_grid, truth)
    weighted_best = _best_from_volume(score_volume_depth_weighted, x_grid, y_grid, depth_grid, truth)
    active_best = weighted_best if params.scan.active_score_kind == "depth_weighted" else unweighted_best
    posterior_result = build_posterior_from_score(
        posterior_input_volume,
        x_grid,
        y_grid,
        depth_grid,
        temperature=getattr(params.scan, "posterior_temperature", 0.2),
    )
    posterior_peak = posterior_result["posterior_peak_location"]
    receiver_imaging["imaging_peak_to_posterior_peak_distance"] = float(
        np.linalg.norm(
            np.array(
                [
                    receiver_imaging["imaging_peak_location"]["x_m"] - posterior_peak["x_m"],
                    receiver_imaging["imaging_peak_location"]["y_m"] - posterior_peak["y_m"],
                    receiver_imaging["imaging_peak_location"]["depth_m"] - posterior_peak["depth_m"],
                ],
                dtype=float,
            )
        )
    )
    high_probability = high_probability_region(
        posterior_result["posterior_probability_volume"],
        x_grid,
        y_grid,
        depth_grid,
        mass_threshold=0.9,
    )
    uncertainty_summary = summarize_uncertainty_volume(posterior_result["posterior_summary"], high_probability)
    posterior_recommendation = build_posterior_recommendation(posterior_result["posterior_summary"], uncertainty_summary)
    geometry_resolution = compute_geometry_resolution_volume(source_xyz, receiver_xyz, x_grid, y_grid, depth_grid)
    active_best_candidate = np.array(
        [
            active_best["best_location"]["x_m"],
            active_best["best_location"]["y_m"],
            active_best["best_location"]["depth_m"],
        ],
        dtype=float,
    )
    scan_velocity_model_audit = run_scan_velocity_model_audit(
        active_best_candidate,
        source_xyz,
        receiver_xyz,
        velocity_model,
        t0_s=params.time.t0_s,
    )
    raw_location = unweighted_best["best_location"]
    weighted_location = weighted_best["best_location"]
    raw_weighted_vector = np.array(
        [
            weighted_location["x_m"] - raw_location["x_m"],
            weighted_location["y_m"] - raw_location["y_m"],
            weighted_location["depth_m"] - raw_location["depth_m"],
        ],
        dtype=float,
    )
    raw_weighted_difference = {
        "dx_m": float(raw_weighted_vector[0]),
        "dy_m": float(raw_weighted_vector[1]),
        "ddepth_m": float(raw_weighted_vector[2]),
        "distance_m": float(np.linalg.norm(raw_weighted_vector)),
    }
    depth_prior_bias_warning = (
        abs(raw_weighted_difference["ddepth_m"]) > params.confidence.raw_weighted_depth_diff_warning_m
    )

    return {
        "score_volume": score_volume_active,
        "score_volume_active": score_volume_active,
        "score_volume_kind": score_volume_kind,
        "score_volume_active_kind": score_volume_kind,
        "score_volume_unweighted": score_volume_unweighted,
        "score_volume_raw": score_volume_unweighted,
        "score_volume_depth_weighted": score_volume_depth_weighted,
        "attribute_score_volumes": attribute_volumes,
        "multi_attribute_inversion_enabled": bool(multi_attribute_enabled),
        "multi_attribute_volumes": multi_attribute_volumes,
        "score_volume_energy": multi_attribute_volumes.get("score_volume_energy", attribute_volumes["energy_score"]),
        "score_volume_normalized_energy": multi_attribute_volumes.get(
            "score_volume_normalized_energy", attribute_volumes["normalized_energy_score"]
        ),
        "score_volume_matched_wavelet": multi_attribute_volumes.get(
            "score_volume_matched_wavelet", attribute_volumes["matched_wavelet_score"]
        ),
        "score_volume_semblance": multi_attribute_volumes.get("score_volume_semblance", attribute_volumes["semblance_score"]),
        "score_volume_frequency_shift": multi_attribute_volumes.get(
            "score_volume_frequency_shift", attribute_volumes["frequency_shift_score"]
        ),
        "score_volume_combined": score_volume_unweighted,
        "posterior_input_volume": posterior_input_volume,
        "posterior_uses_imaging_volume": True,
        "attribute_normalization": getattr(params.scan, "attribute_normalization", "robust_minmax"),
        "attribute_weights": attribute_weights,
        "observation_paths_3d": observation_paths,
        "observation_kernel_metadata": observation_paths.metadata,
        "localization_uses_observation_kernel": True,
        "forward_localization_share_kernel": True,
        "receiver_consistent_imaging": receiver_imaging,
        "imaging_volume_energy": receiver_imaging["imaging_volume_energy"],
        "imaging_volume_envelope": receiver_imaging["imaging_volume_envelope"],
        "imaging_volume_semblance": receiver_imaging["imaging_volume_semblance"],
        "imaging_volume_combined": receiver_imaging["imaging_volume_combined"],
        "receiver_consistent_imaging_available": True,
        "imaging_peak_location": receiver_imaging["imaging_peak_location"],
        "imaging_peak_to_truth_distance": receiver_imaging["imaging_peak_to_truth_distance"],
        "imaging_peak_to_posterior_peak_distance": receiver_imaging["imaging_peak_to_posterior_peak_distance"],
        "posterior_probability_volume": posterior_result["posterior_probability_volume"],
        "posterior_volume_status": "generated",
        "posterior_summary": posterior_result["posterior_summary"],
        "posterior_peak_location": posterior_result["posterior_peak_location"],
        "posterior_mean_location": posterior_result["posterior_mean_location"],
        "posterior_covariance_3x3": posterior_result["posterior_covariance_3x3"],
        "uncertainty_ellipsoid_axes": posterior_result["uncertainty_ellipsoid_axes"],
        "high_probability_region": {key: value for key, value in high_probability.items() if key != "mask"},
        "high_probability_mask": high_probability["mask"],
        "uncertainty_summary": uncertainty_summary,
        "posterior_recommendation": posterior_recommendation,
        "connected_components_3d": uncertainty_summary["connected_components_3d"],
        "ambiguity_warning": uncertainty_summary["ambiguity_warning"],
        "multi_peak_warning": uncertainty_summary["multi_peak_warning"],
        "geometry_resolution_volume": geometry_resolution["geometry_resolution_volume"],
        "geometry_resolution": geometry_resolution,
        "geometry_resolution_summary": geometry_resolution["geometry_resolution_summary"],
        "scan_velocity_model_audit": scan_velocity_model_audit,
        "depth_weights": depth_weights,
        "depth_weight_enabled": params.scan.use_depth_weight,
        "penetration_depth_m": penetration_depth_m,
        "normalized_score_volume": _normalize_volume(score_volume_active),
        "normalized_score_volume_active": _normalize_volume(score_volume_active),
        "normalized_score_volume_unweighted": _normalize_volume(score_volume_unweighted),
        "normalized_score_volume_raw": _normalize_volume(score_volume_unweighted),
        "normalized_score_volume_depth_weighted": _normalize_volume(score_volume_depth_weighted),
        "unweighted_best_index": unweighted_best["best_index"],
        "unweighted_best_location": unweighted_best["best_location"],
        "unweighted_best_score": unweighted_best["best_score"],
        "unweighted_truth_error": unweighted_best["truth_error"],
        "raw_best_index": unweighted_best["best_index"],
        "raw_best_location": unweighted_best["best_location"],
        "raw_best_score": unweighted_best["best_score"],
        "raw_truth_error": unweighted_best["truth_error"],
        "weighted_best_index": weighted_best["best_index"],
        "weighted_best_location": weighted_best["best_location"],
        "weighted_best_score": weighted_best["best_score"],
        "weighted_truth_error": weighted_best["truth_error"],
        "raw_weighted_difference": raw_weighted_difference,
        "unweighted_weighted_difference": raw_weighted_difference,
        "depth_prior_bias_warning": bool(depth_prior_bias_warning),
        "active_best_index": active_best["best_index"],
        "active_best_location": active_best["best_location"],
        "active_best_score": active_best["best_score"],
        "active_truth_error": active_best["truth_error"],
        "best_index": active_best["best_index"],
        "best_location": active_best["best_location"],
        "best_score": active_best["best_score"],
        "truth_error": active_best["truth_error"],
        "y_depth_coupling_warning": "单侧 DAS-like 几何下，横向 y 与埋深 h 可能存在耦合，best_location 不能作为工程确诊。",
    }
