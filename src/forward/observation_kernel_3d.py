"""统一三维观测算子。

Stage 5K 把 forward 和 localization 共用的几何、走时、振幅、衰减和采样逻辑集中到本模块。
核心约定是：所有候选点都按 ``source_xyz -> candidate_xyz -> receiver_xyz`` 的三维路径进入
观测算子；二维 elastic 仍然只是 validation forward，不能替代这里的三维道路 DAS-like 主线。
"""

from __future__ import annotations

from dataclasses import dataclass
from types import SimpleNamespace
from typing import Any

import numpy as np

from src.forward.amplitude_model import compute_direct_amplitude, compute_scatter_amplitude, geometric_spreading
from src.forward.wavelet import shifted_ricker
from src.model.attenuation_model import AttenuationModel, build_attenuation_model
from src.model.velocity_model import KinematicVelocityModel, compute_kinematic_travel_time, compute_scatter_travel_time


EPS = 1.0e-12


@dataclass(frozen=True)
class ObservationPath3D:
    """三维观测路径表。

    数组字段统一使用 ``shot x receiver x candidate`` 顺序。这样 forward 和 localization 可以直接
    对同一张表取 ``scatter_time_s[:, :, candidate_index]``，避免一边正演、一边定位时各自维护走时逻辑。
    """

    shot_index: np.ndarray
    receiver_index: np.ndarray
    candidate_index: np.ndarray
    source_xyz: np.ndarray
    receiver_xyz: np.ndarray
    candidate_xyz: np.ndarray
    direct_time_s: np.ndarray
    scatter_time_s: np.ndarray
    direct_amplitude: np.ndarray
    scatter_amplitude: np.ndarray
    attenuation_factor: np.ndarray
    geometric_factor: np.ndarray
    depth_sensitivity: np.ndarray
    validity_flag: np.ndarray
    metadata: dict[str, Any]


def candidate_grid_to_xyz(x_grid: np.ndarray, y_grid: np.ndarray, depth_grid: np.ndarray) -> np.ndarray:
    """把 x/y/depth 扫描网格按 ``x -> y -> depth`` 顺序展开为 candidate_xyz。"""

    xx, yy, zz = np.meshgrid(x_grid, y_grid, depth_grid, indexing="ij")
    return np.column_stack([xx.ravel(), yy.ravel(), zz.ravel()])


def _candidate_grid_shape_from_params(params: SimpleNamespace, n_candidate: int) -> list[int]:
    """从统一参数中读取 candidate 体 shape；失败时退回一维候选表。"""

    shape = getattr(getattr(params, "derived", SimpleNamespace()), "scan_shape", None)
    if shape is not None and int(np.prod(shape)) == int(n_candidate):
        return [int(v) for v in shape]
    return [int(n_candidate)]


def _path_length(start_xyz: np.ndarray, end_xyz: np.ndarray) -> np.ndarray:
    """计算广播后的三维直线路径长度。"""

    start, end = np.broadcast_arrays(np.asarray(start_xyz, dtype=float), np.asarray(end_xyz, dtype=float))
    return np.linalg.norm(end - start, axis=-1)


def _path_effective_q(
    attenuation_model: AttenuationModel,
    source_xyz: np.ndarray,
    candidate_xyz: np.ndarray,
    receiver_xyz: np.ndarray,
) -> np.ndarray:
    """计算 source-candidate-receiver 两段路径的调和等效 Q。"""

    q_source = attenuation_model.effective_q_for_path(source_xyz[:, None, None, :], candidate_xyz[None, None, :, :])
    q_receiver = attenuation_model.effective_q_for_path(candidate_xyz[None, None, :, :], receiver_xyz[None, :, None, :])
    return 2.0 / (1.0 / np.maximum(q_source, EPS) + 1.0 / np.maximum(q_receiver, EPS))


def compute_direct_times_3d(
    source_xyz: np.ndarray,
    receiver_xyz: np.ndarray,
    candidate_xyz: np.ndarray,
    velocity_model: KinematicVelocityModel,
    params: SimpleNamespace,
) -> np.ndarray:
    """计算 direct arrival 到时表，shape 为 ``shot x receiver x candidate``。

    direct 到时与 candidate 无关，但为了与 scatter 到时保持相同索引结构，这里广播到 candidate 维。
    """

    source = np.asarray(source_xyz, dtype=float)
    receiver = np.asarray(receiver_xyz, dtype=float)
    candidate = np.asarray(candidate_xyz, dtype=float).reshape(-1, 3)
    direct = params.time.t0_s + compute_kinematic_travel_time(
        source[:, None, :],
        receiver[None, :, :],
        velocity_model,
    )
    return np.broadcast_to(direct[:, :, None], (source.shape[0], receiver.shape[0], candidate.shape[0])).copy()


def compute_scatter_times_3d(
    source_xyz: np.ndarray,
    receiver_xyz: np.ndarray,
    candidate_xyz: np.ndarray,
    velocity_model: KinematicVelocityModel,
    params: SimpleNamespace,
) -> np.ndarray:
    """计算 source-candidate-receiver scatter 到时表。"""

    scatter = compute_scatter_travel_time(source_xyz, candidate_xyz, receiver_xyz, velocity_model)
    return params.time.t0_s + np.transpose(scatter, (0, 2, 1))


def compute_path_amplitudes_3d(
    source_xyz: np.ndarray,
    receiver_xyz: np.ndarray,
    candidate_xyz: np.ndarray,
    direct_time_s: np.ndarray,
    scatter_time_s: np.ndarray,
    attenuation_model: AttenuationModel,
    params: SimpleNamespace,
    candidate_weight: np.ndarray | None = None,
) -> dict[str, np.ndarray]:
    """计算 direct/scatter 幅度及其可审计分量。"""

    source = np.asarray(source_xyz, dtype=float)
    receiver = np.asarray(receiver_xyz, dtype=float)
    candidate = np.asarray(candidate_xyz, dtype=float).reshape(-1, 3)
    weight = np.ones(candidate.shape[0], dtype=float) if candidate_weight is None else np.asarray(candidate_weight, dtype=float)
    weight = weight.reshape(-1)
    if weight.size != candidate.shape[0]:
        raise ValueError("candidate_weight 数量必须与 candidate_xyz 一致")

    direct_base = compute_direct_amplitude(
        params,
        source[:, None, :],
        receiver[None, :, :],
        direct_time_s[:, :, 0] - params.time.t0_s,
        attenuation_model,
    )
    direct_amplitude = np.broadcast_to(direct_base[:, :, None], scatter_time_s.shape).copy()
    scatter_travel = scatter_time_s - params.time.t0_s
    scatter_amplitude = compute_scatter_amplitude(
        params,
        source[:, None, None, :],
        candidate[None, None, :, :],
        receiver[None, :, None, :],
        scatter_travel,
        weight[None, None, :],
        attenuation_model,
    )

    source_path = _path_length(source[:, None, None, :], candidate[None, None, :, :])
    receiver_path = _path_length(candidate[None, None, :, :], receiver[None, :, None, :])
    total_path = source_path + receiver_path
    geometric_factor = geometric_spreading(total_path, attenuation_model)
    depth_sensitivity = np.exp(
        -np.maximum(candidate[None, None, :, 2], 0.0) / max(params.derived.rayleigh_penetration_depth_m, EPS)
    )
    q_eff = _path_effective_q(attenuation_model, source, candidate, receiver)
    attenuation_factor = attenuation_model.q_decay(scatter_travel, params.task.wavelet_dominant_frequency_hz, q_eff)
    return {
        "direct_amplitude": direct_amplitude,
        "scatter_amplitude": scatter_amplitude,
        "attenuation_factor": attenuation_factor,
        "geometric_factor": np.broadcast_to(geometric_factor, scatter_time_s.shape).copy(),
        "depth_sensitivity": np.broadcast_to(depth_sensitivity, scatter_time_s.shape).copy(),
    }


def build_observation_paths_3d(
    source_xyz: np.ndarray,
    receiver_xyz: np.ndarray,
    candidate_xyz: np.ndarray,
    velocity_model: KinematicVelocityModel,
    attenuation_model: AttenuationModel | None,
    params: SimpleNamespace,
    *,
    candidate_weight: np.ndarray | None = None,
) -> ObservationPath3D:
    """构建统一三维观测路径表。

    输出表是本轮 forward/localization 共享的核心对象。任何 scan candidate 走时、receiver-consistent
    imaging、kernel-based synthesis 都应优先从该表读取路径信息。
    """

    source = np.asarray(source_xyz, dtype=float)
    receiver = np.asarray(receiver_xyz, dtype=float)
    candidate = np.asarray(candidate_xyz, dtype=float).reshape(-1, 3)
    attenuation = attenuation_model or build_attenuation_model(params)
    direct_time = compute_direct_times_3d(source, receiver, candidate, velocity_model, params)
    scatter_time = compute_scatter_times_3d(source, receiver, candidate, velocity_model, params)
    amplitude = compute_path_amplitudes_3d(
        source,
        receiver,
        candidate,
        direct_time,
        scatter_time,
        attenuation,
        params,
        candidate_weight=candidate_weight,
    )

    n_shot, n_receiver, n_candidate = scatter_time.shape
    shot_index = np.broadcast_to(np.arange(n_shot)[:, None, None], scatter_time.shape).copy()
    receiver_index = np.broadcast_to(np.arange(n_receiver)[None, :, None], scatter_time.shape).copy()
    candidate_index = np.broadcast_to(np.arange(n_candidate)[None, None, :], scatter_time.shape).copy()
    validity = np.isfinite(scatter_time) & (scatter_time >= params.time.t0_s)
    validity &= scatter_time <= params.time.record_length_s + params.time.t0_s
    metadata = {
        "uses_velocity_path_integration": True,
        "uses_attenuation": bool(attenuation.enabled),
        "uses_receiver_consistent_paths": True,
        "candidate_grid_shape": _candidate_grid_shape_from_params(params, n_candidate),
        "n_shot": int(n_shot),
        "n_receiver": int(n_receiver),
        "n_candidate": int(n_candidate),
        "path_shape": [int(n_shot), int(n_receiver), int(n_candidate)],
        "volume_proxy_role": "visualization_only",
    }
    return ObservationPath3D(
        shot_index=shot_index,
        receiver_index=receiver_index,
        candidate_index=candidate_index,
        source_xyz=source,
        receiver_xyz=receiver,
        candidate_xyz=candidate,
        direct_time_s=direct_time,
        scatter_time_s=scatter_time,
        direct_amplitude=amplitude["direct_amplitude"],
        scatter_amplitude=amplitude["scatter_amplitude"],
        attenuation_factor=amplitude["attenuation_factor"],
        geometric_factor=amplitude["geometric_factor"],
        depth_sensitivity=amplitude["depth_sensitivity"],
        validity_flag=validity,
        metadata=metadata,
    )


def sample_gather_along_scatter_paths(
    gather: np.ndarray,
    time_axis: np.ndarray,
    observation_paths: ObservationPath3D,
    *,
    fill_value: float = 0.0,
) -> dict[str, np.ndarray]:
    """沿 observation kernel 的 scatter_time_s 从 gather 中线性取样。"""

    data = np.asarray(gather, dtype=float)
    time = np.asarray(time_axis, dtype=float)
    if data.ndim != 3:
        raise ValueError(f"gather 必须是 shot x time x receiver，当前 shape={data.shape}")
    dt = float(time[1] - time[0]) if time.size > 1 else 1.0
    float_index = (observation_paths.scatter_time_s - time[0]) / dt
    lower = np.floor(float_index).astype(int)
    upper = lower + 1
    frac = float_index - lower
    valid = (lower >= 0) & (upper < data.shape[1]) & observation_paths.validity_flag
    lower_clip = np.clip(lower, 0, data.shape[1] - 1)
    upper_clip = np.clip(upper, 0, data.shape[1] - 1)
    shot = observation_paths.shot_index
    receiver = observation_paths.receiver_index
    lower_value = data[shot, lower_clip, receiver]
    upper_value = data[shot, upper_clip, receiver]
    samples = (1.0 - frac) * lower_value + frac * upper_value
    samples = np.where(valid, samples, fill_value)
    return {
        "samples": samples,
        "valid": valid,
        "scatter_time_s": observation_paths.scatter_time_s,
    }


def stack_receiver_consistent_image(
    gather: np.ndarray,
    time_axis: np.ndarray,
    observation_paths: ObservationPath3D,
    *,
    candidate_grid_shape: tuple[int, int, int] | list[int] | None = None,
) -> dict[str, np.ndarray | dict[str, Any]]:
    """用同一 observation kernel 对 shot/receiver 叠加，形成 receiver-consistent image。"""

    sampled = sample_gather_along_scatter_paths(gather, time_axis, observation_paths)
    values = sampled["samples"] * np.sign(observation_paths.scatter_amplitude)
    weight = np.abs(observation_paths.scatter_amplitude)
    valid = sampled["valid"]
    weighted = np.where(valid, values * weight, 0.0)
    denom = np.maximum(np.sum(np.where(valid, weight, 0.0), axis=(0, 1)), EPS)
    image = np.sum(weighted, axis=(0, 1)) / denom
    shape = tuple(candidate_grid_shape or observation_paths.metadata.get("candidate_grid_shape") or [image.size])
    if len(shape) != 3:
        raise ValueError(f"candidate_grid_shape 必须是三维，当前={shape}")
    return {
        "imaging_vector": image,
        "imaging_volume": image.reshape(shape),
        "sample_count_volume": np.sum(valid, axis=(0, 1)).reshape(shape),
        "metadata": {
            "uses_receiver_consistent_paths": True,
            "uses_velocity_path_integration": True,
            "uses_attenuation": observation_paths.metadata["uses_attenuation"],
            "candidate_grid_shape": list(shape),
        },
    }


def synthesize_gather_from_observation_paths(
    params: SimpleNamespace,
    observation_paths: ObservationPath3D,
) -> dict[str, np.ndarray]:
    """直接由 observation kernel 合成 direct/scatter gather。

    该路径用于 Stage 5K 的 kernel-based synthesis。它与旧 direct/scatter 快速实现使用同一套走时和幅度表；
    因此到时应一致，振幅差异只来自是否显式使用 candidate 权重和统一 kernel 分量。
    """

    time_axis = params.derived.time_axis
    n_shot = observation_paths.metadata["n_shot"]
    n_receiver = observation_paths.metadata["n_receiver"]
    n_time = len(time_axis)
    direct = np.zeros((n_shot, n_time, n_receiver), dtype=float)
    scatter = np.zeros_like(direct)

    for i_shot in range(n_shot):
        for i_receiver in range(n_receiver):
            arrival = observation_paths.direct_time_s[i_shot, i_receiver, 0]
            amplitude = observation_paths.direct_amplitude[i_shot, i_receiver, 0]
            direct[i_shot, :, i_receiver] += amplitude * shifted_ricker(
                time_axis, arrival, params.task.wavelet_frequency_hz
            )
            for i_candidate in range(observation_paths.metadata["n_candidate"]):
                scatter[i_shot, :, i_receiver] += observation_paths.scatter_amplitude[
                    i_shot, i_receiver, i_candidate
                ] * shifted_ricker(
                    time_axis,
                    observation_paths.scatter_time_s[i_shot, i_receiver, i_candidate],
                    params.task.wavelet_frequency_hz,
                )
    return {"direct_data": direct, "scatter_data": scatter, "synthetic_data": direct + scatter}
