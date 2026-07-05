import json
from pathlib import Path

from main import args_to_params, create_output_dir, parse_arguments
from src.pipeline.run_forward_pipeline import run_forward_pipeline
from src.pipeline.run_full_pipeline import run_full_pipeline


def _small_forward_args(tmp_path):
    return [
        "--output-root-dir",
        str(tmp_path),
        "--fiber-channel-count",
        "12",
        "--source-shot-count",
        "2",
        "--time-record-length-s",
        "0.20",
        "--gauge-length-m",
        "4",
        "--max-shot-gather-figures",
        "1",
        "--volume-wavefield-nx",
        "10",
        "--volume-wavefield-ny",
        "6",
        "--volume-wavefield-nh",
        "4",
        "--volume-wavefield-frame-count",
        "3",
        "--volume-wavefield-max-scatter-points",
        "2",
    ]


def test_forward_pipeline_stage5k_outputs_kernel_volume_and_attenuation_context(tmp_path):
    params = args_to_params(
        parse_arguments(
            [
                "--task",
                "forward",
                "--run-name",
                "pytest_forward_stage5k",
                *_small_forward_args(tmp_path),
                "--save-wavefield-animation",
                "false",
                "--save-wavefield-snapshots",
                "false",
            ]
        )
    )
    create_output_dir(params)
    result = run_forward_pipeline(params)
    output_dir = Path(result["output_run_dir"])

    assert (output_dir / "arrays" / "arr_synthetic_data.npy").exists()
    assert (output_dir / "arrays" / "arr_synthetic_data_no_attenuation.npy").exists()
    assert (output_dir / "arrays" / "arr_volume_wavefield_frames.npy").exists()
    assert (output_dir / "figures" / "fig_volume_wavefield_xyz_slices.png").exists()
    assert (output_dir / "figures" / "fig_volume_wavefield_3d_energy_proxy.png").exists()
    assert (output_dir / "figures" / "fig_shot_gather_with_velocity_model.png").exists()
    assert (output_dir / "figures" / "fig_shot_gather_attenuation_comparison.png").exists()

    metadata = json.loads((output_dir / "metadata" / "meta_run.json").read_text(encoding="utf-8"))
    assert metadata["stage"] == "Stage 5K unified 3D observation kernel and receiver-consistent imaging"
    assert metadata["physics"]["attenuation"]["attenuation_enabled"] is True
    assert metadata["visualization"]["volume_wavefield_available"] is True
    assert metadata["approximation"]["volume_wavefield_is_kinematic_proxy"] is True
    assert metadata["approximation"]["volume_proxy_used_for_localization"] is False
    assert metadata["approximation"]["forward_uses_observation_kernel"] is True
    assert result["attenuation_summary"]["relative_rms_difference"] > 0.0
    assert result["volume_response_metadata"]["volume_uses_velocity_path_integration"] is True
    assert result["volume_response_metadata"]["volume_proxy_role"] == "visualization_only"
    assert result["observation_kernel_metadata"]["forward_uses_observation_kernel"] is True


def test_full_pipeline_stage5k_latest_stable_contract(tmp_path):
    params = args_to_params(
        parse_arguments(
            [
                "--task",
                "full_pipeline",
                "--run-name",
                "pytest_full_stage5k",
                *_small_forward_args(tmp_path),
                "--save-wavefield-animation",
                "true",
                "--save-wavefield-snapshots",
                "false",
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
    latest_stable = tmp_path / "latest_stable"

    assert (output_dir / "figures" / "fig_receiver_consistent_imaging_volume.png").exists()
    assert (output_dir / "figures" / "fig_kernel_shared_posterior_volume.png").exists()
    assert (output_dir / "figures" / "fig_module_coordination_summary.png").exists()
    assert (output_dir / "figures" / "fig_receiver_imaging_vs_volume_proxy.png").exists()
    assert (latest_stable / "figures" / "forward" / "fig_volume_wavefield_xyz_slices.png").exists()
    assert (latest_stable / "figures" / "forward" / "fig_shot_gather_with_velocity_model.png").exists()
    assert (latest_stable / "figures" / "forward" / "fig_shot_gather_attenuation_comparison.png").exists()
    assert (latest_stable / "animations" / "forward" / "anim_single_shot_volume_wavefield.gif").exists()
    assert (latest_stable / "figures" / "localization" / "fig_receiver_consistent_imaging_volume.png").exists()
    assert (latest_stable / "figures" / "localization" / "fig_kernel_shared_posterior_volume.png").exists()
    assert (latest_stable / "figures" / "error_analysis" / "fig_module_coordination_summary.png").exists()
    assert (latest_stable / "figures" / "error_analysis" / "fig_receiver_imaging_vs_volume_proxy.png").exists()
    assert (latest_stable / "figures" / "error_analysis" / "fig_stage5j_status_badge.png").exists()
    assert 18 <= len(list((latest_stable / "figures").glob("*/*.png"))) <= 24

    latest_meta = json.loads((latest_stable / "metadata" / "meta_run.json").read_text(encoding="utf-8"))
    assert latest_meta["stage"] == "Stage 5K unified 3D observation kernel and receiver-consistent imaging"
    assert latest_meta["stage5j_validation"]["volume_wavefield_uses_depth"] is True
    assert latest_meta["stage5j_validation"]["volume_wavefield_uses_velocity_path_integration"] is True
    assert latest_meta["stage5j_validation"]["direct_attenuation_applied"] is True
    assert latest_meta["stage5j_validation"]["scatter_attenuation_applied"] is True
    assert latest_meta["stage5j_validation"]["validation_scripts_added_count"] == 1
    assert latest_meta["stage5j_validation"]["new_test_files_count"] == 3
    assert latest_meta["stage5j_validation"]["tests_reduced_count"] >= 5
    assert latest_meta["stage5j_validation"]["ready_for_2p5d"] is False
    assert latest_meta["stage5k_validation"]["observation_kernel_3d_available"] is True
    assert latest_meta["stage5k_validation"]["forward_localization_share_kernel"] is True
    assert latest_meta["stage5k_validation"]["receiver_consistent_imaging_available"] is True
    assert latest_meta["stage5k_validation"]["volume_proxy_used_for_localization"] is False
    assert latest_meta["stage5k_validation"]["validation_scripts_added_count"] == 0
    assert latest_meta["stage5k_validation"]["new_test_files_count"] == 2

    summary_text = (latest_stable / "summary.md").read_text(encoding="utf-8")
    assert "Stage 5K" in summary_text
    assert "observation_kernel_3d_available" in summary_text
    assert "receiver_consistent_imaging_available" in summary_text
    assert "volume_proxy_used_for_localization" in summary_text
    assert "volume_wavefield_available" in summary_text
    assert "attenuation_model_enabled" in summary_text
    assert "forward_localization_link_status" in summary_text
