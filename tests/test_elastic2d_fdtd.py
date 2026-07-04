from main import args_to_params, parse_arguments
from src.forward.elastic2d.elastic_fdtd import run_elastic2d_prototype


def test_elastic2d_fdtd_outputs_surface_gather_and_snapshots():
    params = args_to_params(
        parse_arguments(
            [
                "--elastic2d-nx",
                "41",
                "--elastic2d-nz",
                "31",
                "--elastic2d-duration-s",
                "0.025",
                "--elastic2d-snapshot-count",
                "3",
            ]
        )
    )
    result = run_elastic2d_prototype(params, with_void=False)
    assert result.surface_vz_gather.ndim == 2
    assert result.surface_vx_gather.shape == result.surface_vz_gather.shape
    assert result.wavefield_snapshots_vz.shape[0] == 3
    assert result.cfl_info["stable"] is True
    assert result.diagnostics["max_abs_surface"] >= 0.0
