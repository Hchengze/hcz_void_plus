import numpy as np

from src.model.heterogeneous_velocity import LateralGradientVelocityModel, LocalizedLowVelocityZoneModel
from src.model.velocity_model import UniformVelocityModel


def test_lateral_gradient_velocity_changes_with_xy():
    model = LateralGradientVelocityModel(
        reference_velocity_mps=200.0,
        gradient_x_mps_per_m=1.0,
        gradient_y_mps_per_m=-2.0,
    )
    points = np.array([[0.0, 0.0, 0.0], [10.0, 0.0, 0.0], [0.0, 5.0, 0.0]])
    values = model.velocity_at(points)
    assert values[1] > values[0]
    assert values[2] < values[0]


def test_localized_low_velocity_zone_reduces_velocity_near_center():
    base = UniformVelocityModel(240.0)
    model = LocalizedLowVelocityZoneModel(
        base_model=base,
        center_xyz_m=np.array([10.0, 5.0, 2.0]),
        radius_m=3.0,
        low_velocity_factor=0.6,
        enabled=True,
    )
    center = np.array([[10.0, 5.0, 2.0]])
    far = np.array([[50.0, 5.0, 2.0]])
    assert model.velocity_at(center)[0] < model.velocity_at(far)[0]
