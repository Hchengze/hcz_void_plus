import numpy as np

from main import args_to_params, parse_arguments
from src.validation.velocity_model_audit import run_velocity_model_audit


def test_velocity_model_audit_confirms_layered_travel_time_usage():
    params = args_to_params(parse_arguments([]))
    scatter_xyz = np.array([[params.anomaly.x0_m, params.anomaly.y0_m, params.anomaly.depth_m]], dtype=float)
    result = run_velocity_model_audit(
        params,
        params.derived.source_xyz,
        params.derived.receiver_xyz,
        scatter_xyz,
    )
    assert result["active_velocity_model_type"] == "layered"
    assert result["active_velocity_model_confirmed"] is True
    assert result["velocity_model_used_by_direct"] is True
    assert result["velocity_model_used_by_scatter"] is True
    assert result["velocity_model_used_by_scan"] is True
    assert result["travel_time_difference"]["direct_diff_rms_ms"] > 0.0
