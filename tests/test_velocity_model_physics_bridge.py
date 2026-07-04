from main import args_to_params, parse_arguments
from src.validation.velocity_model_physics_bridge import (
    run_velocity_model_physics_bridge,
    write_velocity_model_physics_bridge_report,
)
from src.visualization.plot_velocity_physics_bridge import (
    plot_elastic_vp_vs_rho_model,
    plot_rayleigh_equivalent_vs_elastic_velocity,
    plot_velocity_model_physics_bridge,
)


def test_velocity_model_physics_bridge_compares_rayleigh_and_elastic_params(tmp_path):
    params = args_to_params(parse_arguments([]))
    result = run_velocity_model_physics_bridge(params)
    assert result["empirical_relation"] == "Rayleigh equivalent velocity ≈ 0.9 * Vs"
    assert len(result["layer_rayleigh_equivalent_velocity_mps"]) == len(params.velocity.layer_depths_m)
    assert result["elastic2d_vs_mps"] == params.forward.elastic2d_vs_mps
    assert result["rayleigh_equivalent_vs_elastic_consistency"] in {"consistent", "mismatch"}
    assert isinstance(result["rayleigh_pick_failure_may_reflect_parameter_mismatch"], bool)

    report = tmp_path / "report_velocity_model_physics_bridge.md"
    write_velocity_model_physics_bridge_report(report, result)
    assert "不同层级的速度模型" in report.read_text(encoding="utf-8")


def test_velocity_model_physics_bridge_figures_can_be_generated(tmp_path):
    params = args_to_params(parse_arguments([]))
    result = run_velocity_model_physics_bridge(params)
    outputs = [
        tmp_path / "fig_rayleigh_equivalent_vs_elastic_velocity.png",
        tmp_path / "fig_elastic_vp_vs_rho_model.png",
        tmp_path / "fig_velocity_model_physics_bridge.png",
    ]
    plot_rayleigh_equivalent_vs_elastic_velocity(result, outputs[0])
    plot_elastic_vp_vs_rho_model(result, outputs[1])
    plot_velocity_model_physics_bridge(result, outputs[2])
    for path in outputs:
        assert path.exists()
        assert path.stat().st_size > 1024
