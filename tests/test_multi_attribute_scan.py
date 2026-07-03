import numpy as np

from main import args_to_params, parse_arguments
from src.localization.attribute_scoring import score_candidate_attributes
from src.localization.multishot_scan import run_multishot_scan
from src.localization.scan_grid import build_scan_grid
from src.model.velocity_model import build_velocity_model


def test_matched_and_semblance_scores_compute():
    params = args_to_params(parse_arguments(["--fiber-channel-count", "6", "--source-shot-count", "2", "--time-record-length-s", "0.1", "--gauge-length-m", "4"]))
    data = np.ones((2, params.derived.nt, 6), dtype=float)
    cumulative = np.concatenate([np.zeros((2, 1, 6)), np.cumsum(data * data, axis=1)], axis=1)
    trace_energy = cumulative[:, -1, :]
    target_times = np.full((2, 6), 0.05)
    scores = score_candidate_attributes(data, cumulative, trace_energy, params.derived.time_axis, target_times, 0.01)
    assert scores["matched_wavelet_score"] >= 0.0
    assert scores["semblance_score"] >= 0.0


def test_multi_attribute_score_volume_shape():
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
                "58",
                "--scan-x-max-m",
                "60",
                "--scan-y-min-m",
                "8",
                "--scan-y-max-m",
                "9",
                "--scan-depth-min-m",
                "1",
                "--scan-depth-max-m",
                "2",
            ]
        )
    )
    data = np.ones((2, params.derived.nt, 8), dtype=float)
    result = run_multishot_scan(data, params.derived.time_axis, params.derived.source_xyz, params.derived.receiver_xyz, build_velocity_model(params), build_scan_grid(params), params)
    assert result["score_volume"].shape == params.derived.scan_shape
    assert "matched_wavelet_score" in result["attribute_score_volumes"]

