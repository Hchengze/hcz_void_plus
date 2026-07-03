"""简化 f-k / f-v 滤波有效性验证。"""

from __future__ import annotations

from types import SimpleNamespace
from typing import Any

import numpy as np

from src.features.direct_wave_mute import mute_direct_wave
from src.preprocessing.fk_filter import fk_velocity_filter
from src.validation.preprocessing_ablation import _curve_energy_ratio


def compute_fk_amplitude_spectrum(gather: np.ndarray, dt_s: float, dx_m: float) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """计算单炮 time-channel 记录的 f-k 幅度谱。

    返回 ``freq, wavenumber, amplitude``，其中 amplitude shape = ``n_freq x n_k``。
    这里使用 numpy FFT 的最小实现，只用于 QC 图件，不是成熟 FK 处理软件。
    """

    spectrum = np.fft.fftshift(np.fft.fft2(gather), axes=(0, 1))
    freq = np.fft.fftshift(np.fft.fftfreq(gather.shape[0], d=dt_s))
    wavenumber = np.fft.fftshift(np.fft.fftfreq(gather.shape[1], d=dx_m))
    amplitude = np.log1p(np.abs(spectrum))
    return freq, wavenumber, amplitude


def run_fk_filter_validation(
    params: SimpleNamespace,
    scan_data: np.ndarray,
    direct_times: np.ndarray,
    truth_diffraction_times: np.ndarray,
) -> dict[str, Any]:
    """验证简化 FK 滤波对直达波和绕射曲线能量的影响。

    若 receiver geometry 不是 straight，f-k 频谱的均匀通道间距假设不严格成立。
    本函数仍可返回 warning，但不会让主流程崩溃。
    """

    warning = None
    if params.fiber.geometry_mode != "straight":
        warning = "receiver_geometry_mode 不是 straight，当前 f-k 结果仅作近似 QC，不建议解释为严格 f-k 滤波。"
    dx_m = float(params.fiber.channel_spacing_m)
    filtered = fk_velocity_filter(
        scan_data,
        params.time.dt_s,
        dx_m,
        params.preprocessing.fk_velocity_min_mps,
        params.preprocessing.fk_velocity_max_mps,
    )
    before_direct = _curve_energy_ratio(scan_data, params.derived.time_axis, direct_times, params.scan.direct_mute_half_width_s)
    after_direct = _curve_energy_ratio(filtered, params.derived.time_axis, direct_times, params.scan.direct_mute_half_width_s)
    before_diffraction = _curve_energy_ratio(
        scan_data,
        params.derived.time_axis,
        truth_diffraction_times,
        params.scan.time_window_half_width_s,
    )
    after_diffraction = _curve_energy_ratio(
        filtered,
        params.derived.time_axis,
        truth_diffraction_times,
        params.scan.time_window_half_width_s,
    )
    direct_reduction_ratio = 1.0 - after_direct / max(before_direct, 1.0e-12)
    diffraction_preservation_ratio = after_diffraction / max(before_diffraction, 1.0e-12)
    return {
        "filtered_data": filtered,
        "warning": warning,
        "before_direct_wave_residual_ratio": before_direct,
        "after_direct_wave_residual_ratio": after_direct,
        "direct_wave_reduction_ratio": float(direct_reduction_ratio),
        "before_diffraction_curve_energy_ratio": before_diffraction,
        "after_diffraction_curve_energy_ratio": after_diffraction,
        "diffraction_preservation_ratio": float(diffraction_preservation_ratio),
        "shape_preserved": filtered.shape == scan_data.shape,
        "applicable_as_strict_fk": params.fiber.geometry_mode == "straight",
    }

