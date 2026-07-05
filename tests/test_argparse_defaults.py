from main import args_to_params, parse_arguments


def test_argparse_defaults_can_parse():
    args = parse_arguments([])
    params = args_to_params(args)

    assert params.project.task == "debug"
    assert params.project.run_name == "stage5j_run"
    assert params.fiber.channel_count >= 2
    assert params.source.shot_count >= 1
    assert params.derived.nt == len(params.derived.time_axis)
    assert params.derived.receiver_xyz.shape == (params.fiber.channel_count, 3)
    assert params.output.figure_language == "zh"
    assert params.output.max_shot_gather_figures == 3
    assert params.output.save_wavefield_snapshots is True
    assert params.output.save_wavefield_animation is True
    assert params.output.wavefield_snapshot_count == 12
    assert params.output.wavefield_grid_nx == 160
    assert params.output.wavefield_grid_ny == 80
    assert params.output.volume_wavefield_enabled is True
    assert params.output.volume_wavefield_nx == 72
    assert params.output.volume_wavefield_ny == 24
    assert params.output.volume_wavefield_nh == 12
    assert params.output.volume_wavefield_frame_count == 8
    assert params.attenuation.enabled is True
    assert params.attenuation.q_default == 35.0
    assert params.attenuation.layer_q == [25.0, 35.0, 50.0, 80.0]
    assert params.scan.enabled is True
    assert params.scan.score_method == "diffraction_energy_stack"
    assert params.scan.direct_mute_mode == "taper"
    assert params.scan.use_depth_weight is True
    assert params.scan.compare_score_methods is True
    assert params.scan.score_method_list == ["diffraction_energy_stack", "normalized_energy_stack"]
    assert params.scan.multi_attribute_ablation_enabled is True
    assert params.scan.geometry_ablation_enabled is True
    assert params.scan.velocity_ablation_enabled is True
    assert params.scan.rayleigh_penetration_factor == 1.0
    assert params.forward.engine == "layered_kinematic"
    assert params.forward.acoustic2d_enabled is False
    assert params.forward.acoustic2d_nx == 201
    assert params.forward.acoustic2d_nz == 101
    assert params.forward.acoustic2d_snapshot_count == 6
    assert params.forward.elastic2d_enabled is False
    assert params.forward.elastic2d_nx == 201
    assert params.forward.elastic2d_nz == 101
    assert params.forward.elastic2d_snapshot_count == 6
    assert params.forward.elastic2d_vp_mps == 500.0
    assert params.forward.elastic2d_vs_mps == 250.0
    assert params.forward.elastic2d_void_enabled is True
    assert params.forward.elastic2d_source_type == "vertical_force"
    assert params.forward.elastic2d_source_depth_m == 0.2
    assert params.forward.elastic2d_rayleigh_pick_vmin_factor == 0.7
    assert params.forward.elastic2d_rayleigh_pick_vmax_factor == 1.1
    assert params.forward.elastic2d_sponge_strength_mode == "medium"
    assert params.forward.elastic2d_free_surface_mode == "approximate"
    assert params.forward.elastic2d_receiver_depth_index == "surface"
    assert params.velocity.model_type == "layered"
    assert params.velocity.layer_depths_m == [0.3, 1.0, 3.0, 8.0]
    assert params.velocity.layer_rayleigh_velocities_mps == [120.0, 180.0, 260.0, 350.0]
    assert params.velocity.low_velocity_factor == 0.7
    assert params.preprocessing.ablation_enabled is True
    assert params.task.wavelet_dominant_frequency_hz == 30.0
    assert params.output.export_latest_stable is True
    assert params.output.latest_stable_dirname == "latest_stable"
    assert params.confidence.threshold_ratio == 0.9
    assert params.confidence.neighborhood_radius == 1
    assert params.confidence.consistency_warning_cv_threshold == 0.8
    assert params.confidence.coupling_warning_span_y_m == 4.0
    assert params.confidence.coupling_warning_span_depth_m == 2.0
    assert params.confidence.raw_weighted_depth_diff_warning_m == 1.0
    assert params.confidence.raw_weighted_location_diff_warning_m == 2.0
    assert params.derived.scan_grid_point_count > 0
    assert params.derived.estimated_wavelength_m == params.velocity.rayleigh_velocity_mps / params.task.wavelet_dominant_frequency_hz
    assert params.derived.rayleigh_penetration_depth_m == params.derived.estimated_wavelength_m
    assert params.derived.latest_stable_dir.endswith("latest_stable")


def test_stage2_visualization_parameter_validation():
    for bad_args in (
        ["--wavefield-snapshot-count", "0"],
        ["--wavefield-grid-nx", "9"],
        ["--wavefield-grid-ny", "9"],
        ["--wavelet-dominant-frequency-hz", "0"],
        ["--rayleigh-penetration-factor", "0"],
        ["--confidence-threshold-ratio", "0"],
        ["--confidence-threshold-ratio", "1.5"],
        ["--confidence-neighborhood-radius", "-1"],
        ["--consistency-warning-cv-threshold", "0"],
        ["--coupling-warning-span-y-m", "0"],
        ["--coupling-warning-span-depth-m", "0"],
        ["--latest-stable-dirname", "bad/name"],
        ["--raw-weighted-depth-diff-warning-m", "0"],
        ["--raw-weighted-location-diff-warning-m", "0"],
        ["--forward-engine", "acoustic2d_prototype"],
        ["--forward-engine", "elastic2d_prototype"],
        ["--acoustic2d-nx", "19"],
        ["--acoustic2d-nz", "19"],
        ["--acoustic2d-dx-m", "0"],
        ["--acoustic2d-dz-m", "0"],
        ["--acoustic2d-duration-s", "0"],
        ["--acoustic2d-snapshot-count", "0"],
        ["--elastic2d-nx", "19"],
        ["--elastic2d-nz", "19"],
        ["--elastic2d-dx-m", "0"],
        ["--elastic2d-dz-m", "0"],
        ["--elastic2d-duration-s", "0"],
        ["--elastic2d-snapshot-count", "0"],
        ["--elastic2d-vp-mps", "100", "--elastic2d-vs-mps", "100"],
        ["--elastic2d-rho-kgm3", "0"],
        ["--elastic2d-void-radius-m", "0"],
        ["--elastic2d-void-vs-factor", "0"],
        ["--elastic2d-source-depth-m", "-0.1"],
        ["--elastic2d-rayleigh-pick-vmin-factor", "0"],
        ["--elastic2d-rayleigh-pick-vmin-factor", "1.0", "--elastic2d-rayleigh-pick-vmax-factor", "1.0"],
    ):
        try:
            args_to_params(parse_arguments(bad_args))
        except ValueError:
            pass
        else:
            raise AssertionError(f"参数应触发校验错误: {bad_args}")
