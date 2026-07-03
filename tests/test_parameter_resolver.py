from main import args_to_params, parse_arguments


def test_source_y_defaults_to_road_width():
    params = args_to_params(parse_arguments(["--road-width-m", "22.5"]))

    assert params.source.y_m == 22.5


def test_derived_array_lengths_match_counts():
    params = args_to_params(
        parse_arguments(
            [
                "--fiber-channel-count",
                "17",
                "--source-shot-count",
                "4",
                "--time-dt-s",
                "0.002",
                "--time-record-length-s",
                "0.2",
            ]
        )
    )

    assert len(params.derived.channel_x) == 17
    assert len(params.derived.shot_x) == 4
    assert len(params.derived.time_axis) == params.derived.nt
    assert params.derived.fiber_x_end_m == params.derived.channel_x[-1]
    assert params.derived.source_x_end_m == params.derived.shot_x[-1]
