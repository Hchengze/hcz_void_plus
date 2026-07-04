from main import args_to_params, parse_arguments
from src.forward.elastic2d.staggered_diagnostics import check_staggered_elastic_cfl
from src.forward.elastic2d.staggered_fdtd import run_staggered_elastic2d_prototype
from src.forward.elastic2d.staggered_grid import StaggeredGrid2D


def test_staggered_grid_shapes_are_documented():
    grid = StaggeredGrid2D(nx=41, nz=31, dx_m=0.1, dz_m=0.1)
    assert grid.nx == 41
    assert grid.nz == 31
    assert grid.width_m > 0
    assert grid.depth_m > 0
    assert (grid.nz, grid.nx) == (31, 41)
    assert (grid.nz, grid.nx + 1) == (31, 42)
    assert (grid.nz + 1, grid.nx) == (32, 41)
    assert (grid.nz + 1, grid.nx + 1) == (32, 42)


def test_staggered_cfl_and_prototype_outputs():
    params = args_to_params(
        parse_arguments(
            [
                "--elastic2d-nx",
                "41",
                "--elastic2d-nz",
                "31",
                "--elastic2d-duration-s",
                "0.015",
                "--elastic2d-snapshot-count",
                "2",
            ]
        )
    )
    result = run_staggered_elastic2d_prototype(params, source_type="horizontal_force")
    assert result.scheme == "staggered"
    assert result.cfl_info["stable"] is True
    assert result.surface_vx_gather.shape == result.surface_vz_gather.shape
    assert result.surface_vz_gather.shape[0] == len(result.time_axis_s)
    assert result.wavefield_snapshots_vz.shape[0] == 2
    assert result.source_type == "horizontal_force"

    cfl = check_staggered_elastic_cfl(result.cfl_info["vmax_mps"], 1.0e-5, 0.1, 0.1)
    assert "cfl_number" in cfl
