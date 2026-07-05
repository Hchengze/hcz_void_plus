import inspect

import numpy as np

from main import args_to_params, parse_arguments
from src.localization.multishot_scan import run_multishot_scan
from src.localization.scan_grid import build_scan_grid
from src.localization.scan_velocity_model_audit import (
    compute_candidate_diffraction_times_representative_velocity,
    scan_candidate_uses_path_integration,
)
from src.localization.travel_time import compute_candidate_diffraction_times
from src.model.velocity_model import build_velocity_model


def _params(extra=None):
    args = [
        "--fiber-channel-count",
        "10",
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
    if extra:
        args.extend(extra)
    return args_to_params(parse_arguments(args))


def test_candidate_times_use_compute_scatter_travel_time_source_contract():
    source = inspect.getsource(compute_candidate_diffraction_times)
    assert "compute_scatter_travel_time" in source
    assert scan_candidate_uses_path_integration() is True


def test_uniform_and_layered_candidate_travel_times_differ():
    layered = _params()
    uniform = _params(["--velocity-model-type", "uniform"])
    candidate = np.array([58.0, 9.0, 2.0])
    layered_times = compute_candidate_diffraction_times(
        candidate,
        layered.derived.source_xyz,
        layered.derived.receiver_xyz,
        build_velocity_model(layered),
    )
    uniform_times = compute_candidate_diffraction_times(
        candidate,
        uniform.derived.source_xyz,
        uniform.derived.receiver_xyz,
        build_velocity_model(uniform),
    )
    assert layered_times.shape == uniform_times.shape
    assert not np.allclose(layered_times, uniform_times)


def test_layered_active_scan_differs_from_representative_velocity_baseline():
    params = _params()
    model = build_velocity_model(params)
    candidate = np.array([58.0, 9.0, 2.0])
    active = compute_candidate_diffraction_times(candidate, params.derived.source_xyz, params.derived.receiver_xyz, model)
    representative = compute_candidate_diffraction_times_representative_velocity(
        candidate,
        params.derived.source_xyz,
        params.derived.receiver_xyz,
        model,
    )
    assert not np.allclose(active, representative)


def test_multishot_scan_records_path_integration_audit():
    params = _params()
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
    audit = result["scan_velocity_model_audit"]
    assert audit["scan_candidate_uses_path_integration"] is True
    assert audit["scan_uses_representative_velocity"] is False
    assert audit["active_vs_representative_rms_ms"] > 0.0
