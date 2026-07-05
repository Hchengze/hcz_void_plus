"""多炮 DAS-like 运动学正演合成。"""

from __future__ import annotations

from copy import deepcopy
from types import SimpleNamespace

import numpy as np

from src.das_like.das_response_level import apply_das_like_response
from src.forward.amplitude_model import attenuation_comparison_summary
from src.forward.direct_wave import simulate_direct_wave
from src.forward.observation_kernel_3d import build_observation_paths_3d, synthesize_gather_from_observation_paths
from src.forward.scatter_kinematic import simulate_scatter_wave
from src.model.attenuation_model import attenuation_metadata, build_attenuation_model
from src.model.velocity_model import KinematicVelocityModel


def add_gaussian_noise(data: np.ndarray, snr_db: float, rng: np.random.Generator) -> np.ndarray:
    """按目标信噪比加入高斯白噪声。

    物理意义：
        用简化随机噪声表示交通、环境振动和仪器噪声的一部分影响。

    输入参数：
        data：shape = (n_shot, n_time, n_channel)；
        snr_db：目标信噪比，单位 dB；
        rng：由统一 random_seed 构造的随机数生成器。

    输出形状：
        noisy_data，与 data 相同。

    近似条件和限制：
        这里不是城市交通噪声的真实统计模型，只是用于算法闭环和可复现实验的
        高斯噪声近似。
    """

    signal_rms = float(np.sqrt(np.mean(data * data)))
    if signal_rms == 0.0:
        return data.copy()
    noise_rms = signal_rms / (10.0 ** (snr_db / 20.0))
    noise = rng.normal(loc=0.0, scale=noise_rms, size=data.shape)
    return data + noise


def synthesize_multishot_forward(
    params: SimpleNamespace,
    source_xyz: np.ndarray,
    receiver_xyz: np.ndarray,
    scatter_xyz: np.ndarray,
    scatter_weight: np.ndarray,
    velocity_model: KinematicVelocityModel,
) -> dict[str, np.ndarray]:
    """合成多炮 DAS-like 运动学正演数据。

    物理意义：
        将直达瑞雷波和异常体等效散射/绕射波相加，再根据 DAS-like 接收层级
        得到最终合成记录。

    输入参数：
        params：统一参数对象；
        source_xyz：shape = (n_shot, 3)，单位 m；
        receiver_xyz：shape = (n_channel, 3)，单位 m；
        scatter_xyz：shape = (n_scatter, 3)，单位 m；
        scatter_weight：shape = (n_scatter,)，无量纲；
        velocity_model：统一速度模型对象，可为 uniform、layered 或 heterogeneous。

    输出：
        dict，包含 direct_data、scatter_data、synthetic_data，所有数组 shape 都为
        (n_shot, n_time, n_channel)，即 shot × time × channel。

    近似条件和限制：
        当前是 kinematic approximation 和 DAS-like response approximation；
        不宣称完整 DAS 仪器模拟，也不宣称完整三维弹性波全波场模拟。
    """

    attenuation_model = build_attenuation_model(params)
    observation_paths = build_observation_paths_3d(
        source_xyz,
        receiver_xyz,
        scatter_xyz,
        velocity_model,
        attenuation_model,
        params,
        candidate_weight=scatter_weight,
    )
    if bool(getattr(params.forward, "synthesize_from_observation_kernel", True)):
        # Stage 5K 后，主正演优先从统一 observation kernel 合成，避免 direct/scatter 与定位各自维护路径表。
        kernel_synthetic = synthesize_gather_from_observation_paths(params, observation_paths)
        direct_data = kernel_synthetic["direct_data"]
        scatter_data = kernel_synthetic["scatter_data"]
        forward_uses_kernel = True
    else:
        direct_data = simulate_direct_wave(params, source_xyz, receiver_xyz, velocity_model)
        scatter_data = simulate_scatter_wave(
            params, source_xyz, receiver_xyz, scatter_xyz, scatter_weight, velocity_model
        )
        forward_uses_kernel = False
    combined = direct_data + scatter_data
    das_like_data = apply_das_like_response(combined, params)

    no_attenuation_data = None
    attenuation_summary = attenuation_metadata(attenuation_model)
    if attenuation_model.enabled:
        # 为了让用户能直接看到 Q attenuation 的实际影响，本轮在生产正演中生成一份
        # “关闭 attenuation、其余参数不变”的轻量参考炮集。它只用于 RMS 对照和图件，
        # 不作为 active synthetic_data。
        reference_params = deepcopy(params)
        reference_params.attenuation.enabled = False
        reference_attenuation = build_attenuation_model(reference_params)
        reference_paths = build_observation_paths_3d(
            source_xyz,
            receiver_xyz,
            scatter_xyz,
            velocity_model,
            reference_attenuation,
            reference_params,
            candidate_weight=scatter_weight,
        )
        reference_synthetic = synthesize_gather_from_observation_paths(reference_params, reference_paths)
        reference_direct = reference_synthetic["direct_data"]
        reference_scatter = reference_synthetic["scatter_data"]
        no_attenuation_data = apply_das_like_response(reference_direct + reference_scatter, reference_params)
        attenuation_summary.update(attenuation_comparison_summary(das_like_data, no_attenuation_data))

    if params.noise.enabled:
        rng = np.random.default_rng(params.project.random_seed)
        synthetic_data = add_gaussian_noise(das_like_data, params.noise.snr_db, rng)
    else:
        synthetic_data = das_like_data

    return {
        "direct_data": direct_data,
        "scatter_data": scatter_data,
        "synthetic_data": synthetic_data,
        "synthetic_data_no_attenuation": no_attenuation_data,
        "attenuation_summary": attenuation_summary,
        "observation_paths_3d": observation_paths,
        "observation_kernel_metadata": {
            **observation_paths.metadata,
            "forward_uses_observation_kernel": bool(forward_uses_kernel),
            "kernel_based_synthesis_smoke": True,
            "direct_scatter_legacy_available": True,
        },
    }
