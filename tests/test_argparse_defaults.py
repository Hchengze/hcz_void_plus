from main import args_to_params, parse_arguments


def test_argparse_defaults_can_parse():
    args = parse_arguments([])
    params = args_to_params(args)

    assert params.project.task == "debug"
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
    assert params.scan.enabled is True
    assert params.scan.score_method == "diffraction_energy_stack"
    assert params.derived.scan_grid_point_count > 0


def test_stage2_visualization_parameter_validation():
    for bad_args in (
        ["--wavefield-snapshot-count", "0"],
        ["--wavefield-grid-nx", "9"],
        ["--wavefield-grid-ny", "9"],
    ):
        try:
            args_to_params(parse_arguments(bad_args))
        except ValueError:
            pass
        else:
            raise AssertionError(f"参数应触发校验错误: {bad_args}")
