import numpy as np

from src.localization.connected_components_3d import label_probability_components


def test_connected_components_3d_detects_multiple_regions():
    mask = np.zeros((4, 4, 3), dtype=bool)
    mask[0, 0, 0] = True
    mask[0, 1, 0] = True
    mask[3, 3, 2] = True
    result = label_probability_components(mask, np.arange(4.0), np.arange(4.0), np.arange(3.0))
    assert result["component_count"] == 2
    assert result["multi_peak_warning"] is True
    assert result["largest_component_box"]["point_count"] == 2
