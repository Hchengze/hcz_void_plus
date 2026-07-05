import numpy as np

from main import args_to_params, parse_arguments
from src.forward import direct_wave, scatter_kinematic
from src.forward.multishot_forward import synthesize_multishot_forward
from src.geometry.acquisition_geometry import generate_receiver_xyz, generate_source_xyz
from src.model.anomalies import anomaly_to_scatter_points, build_anomaly_from_params
from src.model.velocity_model import build_velocity_model
from src.visualization.plot_gather_with_velocity_model import plot_shot_gather_with_velocity_model


def _small_params():
    return args_to_params(
        parse_arguments(
            [
                "--fiber-channel-count",
                "13",
                "--source-shot-count",
                "2",
                "--time-record-length-s",
                "0.20",
                "--save-figures",
                "false",
            ]
        )
    )


def _geometry(params):
    receiver_xyz = generate_receiver_xyz(params)
    source_xyz = generate_source_xyz(params)
    anomaly = build_anomaly_from_params(params)
    scatter_xyz, scatter_weight = anomaly_to_scatter_points(anomaly, params.anomaly.scatter_point_mode)
    velocity_model = build_velocity_model(params)
    return source_xyz, receiver_xyz, scatter_xyz, scatter_weight, velocity_model


def test_direct_and_scatter_forward_call_amplitude_model(monkeypatch):
    params = _small_params()
    source_xyz, receiver_xyz, scatter_xyz, scatter_weight, velocity_model = _geometry(params)
    calls = {"direct": 0, "scatter": 0}

    def fake_direct_amplitude(params, start_xyz, end_xyz, travel_time_s):
        calls["direct"] += 1
        return np.ones_like(travel_time_s, dtype=float)

    def fake_scatter_amplitude(params, source_xyz, scatter_xyz, receiver_xyz, travel_time_s, scatter_weight):
        calls["scatter"] += 1
        return np.ones_like(travel_time_s, dtype=float)

    monkeypatch.setattr(direct_wave, "compute_direct_amplitude", fake_direct_amplitude)
    monkeypatch.setattr(scatter_kinematic, "compute_scatter_amplitude", fake_scatter_amplitude)

    direct_wave.simulate_direct_wave(params, source_xyz, receiver_xyz, velocity_model)
    scatter_kinematic.simulate_scatter_wave(params, source_xyz, receiver_xyz, scatter_xyz, scatter_weight, velocity_model)

    assert calls == {"direct": 1, "scatter": 1}


def test_multishot_forward_and_gather_velocity_overlay(tmp_path):
    params = _small_params()
    source_xyz, receiver_xyz, scatter_xyz, scatter_weight, velocity_model = _geometry(params)
    result = synthesize_multishot_forward(params, source_xyz, receiver_xyz, scatter_xyz, scatter_weight, velocity_model)

    assert result["attenuation_summary"]["attenuation_comparison_available"] is True
    assert result["attenuation_summary"]["relative_rms_difference"] > 0.0

    plot_summary = plot_shot_gather_with_velocity_model(
        params,
        result["synthetic_data"],
        0,
        source_xyz,
        receiver_xyz,
        scatter_xyz,
        velocity_model,
        tmp_path / "gather_velocity_overlay.png",
    )
    assert plot_summary["shot_gather_velocity_overlay_available"] is True
    assert plot_summary["direct_curve_uses_path_integration"] is True
    assert plot_summary["scatter_curve_uses_path_integration"] is True
    assert params.forward.engine == "layered_kinematic"
