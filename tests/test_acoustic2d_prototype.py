from main import args_to_params, parse_arguments
from src.forward.acoustic2d.acoustic_fdtd import run_acoustic2d_prototype


def test_acoustic2d_prototype_outputs_gather_snapshots_and_cfl():
    params = args_to_params(
        parse_arguments(
            [
                "--acoustic2d-nx",
                "41",
                "--acoustic2d-nz",
                "31",
                "--acoustic2d-duration-s",
                "0.04",
                "--acoustic2d-snapshot-count",
                "4",
                "--time-dt-s",
                "0.001",
            ]
        )
    )
    result = run_acoustic2d_prototype(params)
    assert result.shot_gather.ndim == 2
    assert result.wavefield_snapshots.shape[0] == 4
    assert result.velocity_mps.shape == (31, 41)
    assert result.cfl_info["stable"] is True
    assert result.cfl_info["cfl_number"] < result.cfl_info["recommended_max"]
    assert "max_abs_amplitude" in result.diagnostics
