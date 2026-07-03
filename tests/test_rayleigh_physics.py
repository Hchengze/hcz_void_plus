import numpy as np

from main import args_to_params, parse_arguments
from src.physics.rayleigh import estimate_penetration_depth, estimate_rayleigh_wavelength, rayleigh_depth_weight


def test_rayleigh_wavelength_and_penetration_depth_from_params():
    params = args_to_params(
        parse_arguments(
            [
                "--rayleigh-velocity-mps",
                "300",
                "--wavelet-dominant-frequency-hz",
                "30",
                "--rayleigh-penetration-factor",
                "1.5",
            ]
        )
    )

    assert estimate_rayleigh_wavelength(300.0, 30.0) == 10.0
    assert params.derived.estimated_wavelength_m == 10.0
    assert estimate_penetration_depth(params) == 15.0
    assert params.derived.rayleigh_penetration_depth_m == 15.0


def test_depth_weight_decreases_with_depth():
    weights = rayleigh_depth_weight(np.array([1.0, 3.0, 6.0]), penetration_depth_m=5.0)

    assert weights[0] > weights[1] > weights[2]
    assert np.all(weights > 0)
