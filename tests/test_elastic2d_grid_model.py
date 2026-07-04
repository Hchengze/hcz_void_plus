import numpy as np

from src.forward.elastic2d.grid import Elastic2DGrid
from src.forward.elastic2d.model import apply_void_like_anomaly, build_uniform_elastic_model


def test_elastic2d_model_builds_lame_parameters_and_void():
    grid = Elastic2DGrid(nx=31, nz=21, dx_m=0.1, dz_m=0.1)
    model = build_uniform_elastic_model(grid, vp_mps=500.0, vs_mps=250.0, rho_kgm3=1800.0)
    assert model.vp_mps.shape == (21, 31)
    assert model.vs_mps.shape == (21, 31)
    assert model.rho_kgm3.shape == (21, 31)
    assert np.all(model.mu_pa > 0.0)
    assert np.all(model.lambda_pa > 0.0)

    anomaly = apply_void_like_anomaly(model, grid, 1.5, 1.0, 0.4, 0.5, 0.2, 0.5)
    assert np.min(anomaly.vs_mps) < np.min(model.vs_mps)
    assert np.min(anomaly.vp_mps) < np.min(model.vp_mps)
    assert np.min(anomaly.rho_kgm3) < np.min(model.rho_kgm3)
