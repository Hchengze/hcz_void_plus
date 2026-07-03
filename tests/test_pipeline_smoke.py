from pathlib import Path
import json

from main import args_to_params, create_output_dir, parse_arguments
from src.pipeline.run_forward_pipeline import run_forward_pipeline
from src.pipeline.run_full_pipeline import run_full_pipeline


def test_pipeline_smoke_generates_output_and_metadata(tmp_path):
    params = args_to_params(
        parse_arguments(
            [
                "--task",
                "forward",
                "--run-name",
                "pytest_smoke",
                "--output-root-dir",
                str(tmp_path),
                "--fiber-channel-count",
                "12",
                "--source-shot-count",
                "2",
                "--time-record-length-s",
                "0.2",
                "--gauge-length-m",
                "4",
                "--save-figures",
                "true",
                "--save-wavefield-animation",
                "false",
                "--wavefield-snapshot-count",
                "3",
                "--wavefield-grid-nx",
                "30",
                "--wavefield-grid-ny",
                "20",
                "--max-shot-gather-figures",
                "1",
            ]
        )
    )
    create_output_dir(params)
    result = run_forward_pipeline(params)

    output_dir = Path(result["output_run_dir"])
    assert output_dir.exists()
    for name in ["arrays", "figures", "snapshots", "animations", "reports", "logs", "metadata"]:
        assert (output_dir / name).exists()
    assert (output_dir / "metadata" / "meta_run.json").exists()
    assert (output_dir / "metadata" / "params_snapshot.json").exists()
    assert (output_dir / "arrays" / "arr_synthetic_data.npy").exists()
    assert (output_dir / "figures" / "fig_shot_gather_000.png").exists()
    assert not (output_dir / "figures" / "fig_shot_gather_001.png").exists()
    assert len(list((output_dir / "snapshots").glob("snap_*.png"))) == 3
    assert not (output_dir / "animations" / "anim_pseudo_wavefield.gif").exists()
    assert (output_dir / "figures" / "fig_geometry_layout_check.png").exists()
    metadata = json.loads((output_dir / "metadata" / "meta_run.json").read_text(encoding="utf-8"))
    assert metadata["geometry"]["pseudo_wavefield_plane"] == "x-y surface plane, z=0"
    assert metadata["geometry"]["anomaly_depth_used_as_z"] is True
    assert metadata["geometry"]["anomaly_depth_used_as_y"] is False


def test_pipeline_can_disable_wavefield_snapshots(tmp_path):
    params = args_to_params(
        parse_arguments(
            [
                "--output-root-dir",
                str(tmp_path),
                "--fiber-channel-count",
                "12",
                "--source-shot-count",
                "2",
                "--time-record-length-s",
                "0.2",
                "--gauge-length-m",
                "4",
                "--save-figures",
                "false",
                "--save-wavefield-snapshots",
                "false",
                "--save-wavefield-animation",
                "false",
            ]
        )
    )
    create_output_dir(params)
    result = run_forward_pipeline(params)
    output_dir = Path(result["output_run_dir"])
    assert len(list((output_dir / "snapshots").glob("snap_*.png"))) == 0


def test_full_pipeline_saves_depth_weighted_scan_and_diagnostics(tmp_path):
    params = args_to_params(
        parse_arguments(
            [
                "--task",
                "full_pipeline",
                "--output-root-dir",
                str(tmp_path),
                "--fiber-channel-count",
                "18",
                "--source-shot-count",
                "2",
                "--time-record-length-s",
                "0.22",
                "--gauge-length-m",
                "4",
                "--save-wavefield-snapshots",
                "false",
                "--save-wavefield-animation",
                "false",
                "--max-shot-gather-figures",
                "1",
                "--scan-x-min-m",
                "56",
                "--scan-x-max-m",
                "64",
                "--scan-x-step-m",
                "4",
                "--scan-y-min-m",
                "8",
                "--scan-y-max-m",
                "10",
                "--scan-y-step-m",
                "1",
                "--scan-depth-min-m",
                "2",
                "--scan-depth-max-m",
                "4",
                "--scan-depth-step-m",
                "1",
            ]
        )
    )
    create_output_dir(params)
    result = run_full_pipeline(params)
    output_dir = Path(result["output_run_dir"])

    assert (output_dir / "arrays" / "arr_score_volume_raw.npy").exists()
    assert (output_dir / "arrays" / "arr_score_volume_depth_weighted.npy").exists()
    assert (output_dir / "figures" / "fig_source_anomaly_receiver_path_section.png").exists()
    assert (output_dir / "figures" / "fig_rayleigh_depth_sensitivity.png").exists()
    assert (output_dir / "figures" / "fig_diffraction_travel_time_curves.png").exists()
    assert (output_dir / "figures" / "fig_confidence_diagnostics.png").exists()
    assert (output_dir / "figures" / "fig_raw_vs_weighted_best_location.png").exists()
    assert (output_dir / "figures" / "fig_raw_vs_weighted_x_depth_slice.png").exists()
    assert (output_dir / "figures" / "fig_y_high_score_width_check.png").exists()
    assert (output_dir / "figures" / "fig_score_method_depth_comparison.png").exists()
    assert (output_dir / "figures" / "fig_3d_high_score_uncertainty_summary.png").exists()
    assert (output_dir / "figures" / "fig_x_y_depth_uncertainty_slices.png").exists()
    assert (output_dir / "figures" / "fig_preprocessing_ablation_summary.png").exists()
    assert (output_dir / "figures" / "fig_fk_spectrum_before_after.png").exists()
    assert (output_dir / "figures" / "fig_fk_filter_effect_on_gather.png").exists()
    assert (output_dir / "figures" / "fig_matched_wavelet_score_comparison.png").exists()
    assert (output_dir / "figures" / "fig_semblance_score_volume_slice.png").exists()
    assert (output_dir / "figures" / "fig_frequency_shift_attribute.png").exists()
    assert (output_dir / "figures" / "fig_geometry_ablation_best_locations.png").exists()
    assert (output_dir / "figures" / "fig_geometry_ablation_uncertainty_spans.png").exists()
    assert (output_dir / "figures" / "fig_multi_attribute_ablation.png").exists()
    assert (output_dir / "figures" / "fig_3d_high_score_components.png").exists()
    assert (output_dir / "figures" / "fig_recommendation_decision_flow.png").exists()
    assert (output_dir / "reports" / "report_confidence.md").exists()
    assert (output_dir / "reports" / "report_preprocessing_ablation.md").exists()
    assert (output_dir / "reports" / "report_fk_filter_validation.md").exists()
    assert (output_dir / "reports" / "report_matched_wavelet_validation.md").exists()
    assert (output_dir / "reports" / "report_semblance_validation.md").exists()
    assert (output_dir / "reports" / "report_frequency_shift_attribute.md").exists()
    assert (output_dir / "reports" / "report_geometry_ablation.md").exists()
    assert (output_dir / "reports" / "report_multi_attribute_ablation.md").exists()
    assert (output_dir / "arrays" / "arr_confidence_metrics.json").exists()
    latest_stable = tmp_path / "latest_stable"
    assert latest_stable.exists()
    assert (latest_stable / "summary.md").exists()
    assert (latest_stable / "figures" / "fig_geometry_layout_check.png").exists()
    assert (latest_stable / "figures" / "fig_confidence_diagnostics.png").exists()
    assert (latest_stable / "figures" / "fig_raw_vs_weighted_best_location.png").exists()
    assert (latest_stable / "figures" / "fig_raw_vs_weighted_x_depth_slice.png").exists()
    assert (latest_stable / "figures" / "fig_y_high_score_width_check.png").exists()
    assert (latest_stable / "figures" / "fig_score_method_depth_comparison.png").exists()
    assert (latest_stable / "figures" / "fig_3d_high_score_uncertainty_summary.png").exists()
    assert (latest_stable / "figures" / "fig_x_y_depth_uncertainty_slices.png").exists()
    assert (latest_stable / "figures" / "fig_preprocessing_ablation_summary.png").exists()
    assert (latest_stable / "figures" / "fig_fk_spectrum_before_after.png").exists()
    assert (latest_stable / "figures" / "fig_fk_filter_effect_on_gather.png").exists()
    assert (latest_stable / "figures" / "fig_matched_wavelet_score_comparison.png").exists()
    assert (latest_stable / "figures" / "fig_semblance_score_volume_slice.png").exists()
    assert (latest_stable / "figures" / "fig_frequency_shift_attribute.png").exists()
    assert (latest_stable / "figures" / "fig_geometry_ablation_best_locations.png").exists()
    assert (latest_stable / "figures" / "fig_geometry_ablation_uncertainty_spans.png").exists()
    assert (latest_stable / "figures" / "fig_multi_attribute_ablation.png").exists()
    assert (latest_stable / "figures" / "fig_3d_high_score_components.png").exists()
    assert (latest_stable / "figures" / "fig_recommendation_decision_flow.png").exists()
    assert (latest_stable / "reports" / "report_full_pipeline.md").exists()
    assert (latest_stable / "reports" / "report_confidence.md").exists()
    assert (latest_stable / "reports" / "report_score_method_comparison.md").exists()
    assert (latest_stable / "reports" / "report_preprocessing_ablation.md").exists()
    assert (latest_stable / "reports" / "report_fk_filter_validation.md").exists()
    assert (latest_stable / "reports" / "report_matched_wavelet_validation.md").exists()
    assert (latest_stable / "reports" / "report_semblance_validation.md").exists()
    assert (latest_stable / "reports" / "report_frequency_shift_attribute.md").exists()
    assert (latest_stable / "reports" / "report_geometry_ablation.md").exists()
    assert (latest_stable / "reports" / "report_multi_attribute_ablation.md").exists()
    assert (latest_stable / "metadata" / "meta_run.json").exists()
    metadata = json.loads((output_dir / "metadata" / "meta_run.json").read_text(encoding="utf-8"))
    assert metadata["physics"]["rayleigh_depth_sensitivity_enabled"] is True
    assert metadata["scan"]["use_depth_weight"] is True
    assert metadata["scan"]["score_volume_raw_saved"] is True
    assert metadata["scan"]["score_volume_depth_weighted_saved"] is True
    assert metadata["scan"]["raw_best_location"] is not None
    assert metadata["scan"]["weighted_best_location"] is not None
    assert metadata["scan"]["raw_weighted_difference"] is not None
    assert metadata["scan"]["recommended_location"] is not None
    assert metadata["scan"]["score_method_comparison"] is not None
    assert metadata["diagnostics"]["diffraction_travel_time_curve_figure"]
    assert metadata["confidence"]["peak_sharpness"] is not None
    assert metadata["confidence"]["best_depth_at_boundary_warning"] is not None
    assert metadata["confidence"]["wide_y_high_score_zone_warning"] is not None
    assert metadata["confidence"]["raw_weighted_divergence_warning"] is not None
    assert metadata["output"]["latest_stable_exported"] is True
    assert metadata["stage4b_validation"]["preprocessing_ablation"] is not None
    assert metadata["stage4b_validation"]["fk_filter_validation"] is not None
    assert metadata["stage4b_validation"]["multi_attribute_ablation"] is not None
    assert metadata["stage4b_validation"]["geometry_ablation"] is not None
    summary_text = (latest_stable / "summary.md").read_text(encoding="utf-8")
    assert "unweighted_best" in summary_text
    assert "weighted_best" in summary_text
    assert "shallow bias warning" in summary_text
    assert "recommended_location" in summary_text
    assert "3D high-score span" in summary_text
    assert "Stage 4B" in summary_text
    assert "multi_attribute improved over energy" in summary_text
