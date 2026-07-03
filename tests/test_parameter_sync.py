from main import args_to_params, parse_arguments


def test_road_width_change_syncs_source_y_and_geometry():
    params = args_to_params(
        parse_arguments(
            [
                "--road-width-m",
                "26.0",
                "--fiber-channel-count",
                "12",
                "--source-shot-count",
                "2",
            ]
        )
    )

    assert params.source.y_m == 26.0
    assert (params.derived.source_xyz[:, 1] == 26.0).all()


def test_explicit_source_y_overrides_road_width():
    params = args_to_params(parse_arguments(["--road-width-m", "26.0", "--source-y-m", "19.0"]))

    assert params.source.y_m == 19.0
    assert (params.derived.source_xyz[:, 1] == 19.0).all()
