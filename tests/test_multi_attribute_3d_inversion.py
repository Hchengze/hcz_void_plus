import numpy as np

from main import args_to_params, parse_arguments
from src.localization.multishot_scan import run_multishot_scan
from src.localization.scan_grid import build_scan_grid
from src.model.velocity_model import build_velocity_model


def test_multi_attribute_3d_inversion_outputs_required_volumes():
    params = args_to_params(
        parse_arguments(
            [
                "--fiber-channel-count",
                "8",
                "--source-shot-count",
                "2",
                "--time-record-length-s",
                "0.12",
                "--gauge-length-m",
                "4",
                "--scan-x-min-m",
                "56",
                "--scan-x-max-m",
                "60",
                "--scan-x-step-m",
                "2",
                "--scan-y-min-m",
                "8",
                "--scan-y-max-m",
                "10",
                "--scan-y-step-m",
                "1",
                "--scan-depth-min-m",
                "1",
                "--scan-depth-max-m",
                "3",
                "--scan-depth-step-m",
                "1",
            ]
        )
    )
    data = np.ones((params.source.shot_count, params.derived.nt, params.fiber.channel_count), dtype=float)
    result = run_multishot_scan(
        data,
        params.derived.time_axis,
        params.derived.source_xyz,
        params.derived.receiver_xyz,
        build_velocity_model(params),
        build_scan_grid(params),
        params,
    )
    required = [
        "score_volume_energy",
        "score_volume_normalized_energy",
        "score_volume_matched_wavelet",
        "score_volume_semblance",
        "score_volume_frequency_shift",
        "score_volume_combined",
        "posterior_probability_volume",
    ]
    for key in required:
        assert result[key].shape == params.derived.scan_shape
    assert result["multi_attribute_inversion_enabled"] is True
    assert result["posterior_volume_status"] == "generated"
    assert np.isclose(np.sum(result["posterior_probability_volume"]), 1.0)
