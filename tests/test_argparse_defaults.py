from main import args_to_params, parse_arguments


def test_argparse_defaults_can_parse():
    args = parse_arguments([])
    params = args_to_params(args)

    assert params.project.task == "debug"
    assert params.fiber.channel_count >= 2
    assert params.source.shot_count >= 1
    assert params.derived.nt == len(params.derived.time_axis)
    assert params.derived.receiver_xyz.shape == (params.fiber.channel_count, 3)
