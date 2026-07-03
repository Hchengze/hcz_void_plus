from main import args_to_params, parse_arguments
from src.geometry.acquisition_geometry import generate_receiver_xyz, generate_source_xyz
from src.model.anomalies import anomaly_to_scatter_points, build_anomaly_from_params
from src.validation.forward_engine_ablation import (
    run_forward_engine_ablation,
    strip_forward_engine_ablation_arrays,
)


def test_forward_engine_ablation_runs_all_stage5b_engines():
    params = args_to_params(
        parse_arguments(
            [
                "--fiber-channel-count",
                "12",
                "--source-shot-count",
                "2",
                "--time-record-length-s",
                "0.18",
                "--acoustic2d-nx",
                "41",
                "--acoustic2d-nz",
                "31",
                "--acoustic2d-duration-s",
                "0.04",
                "--acoustic2d-snapshot-count",
                "3",
            ]
        )
    )
    receiver_xyz = generate_receiver_xyz(params)
    source_xyz = generate_source_xyz(params)
    anomaly = build_anomaly_from_params(params)
    scatter_xyz, scatter_weight = anomaly_to_scatter_points(anomaly, params.anomaly.scatter_point_mode)

    result = run_forward_engine_ablation(params, source_xyz, receiver_xyz, scatter_xyz, scatter_weight)
    assert result["active_forward_engine"] == "layered_kinematic"
    assert result["engines"]["kinematic_baseline"]["forward_stage"] == "F0"
    assert result["engines"]["layered_kinematic"]["forward_stage"] == "F1"
    assert result["engines"]["acoustic2d_prototype"]["forward_stage"] == "F2"
    assert result["layered_vs_baseline"]["travel_time_residual_rms_ms"] >= 0.0
    stripped = strip_forward_engine_ablation_arrays(result)
    assert "baseline_synthetic_data" not in stripped
    assert stripped["next_required_forward"] == "elastic2d"
