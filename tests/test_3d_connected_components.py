import numpy as np

from src.localization.connected_components import label_high_score_components


def test_connected_components_detect_two_separate_high_score_regions():
    mask = np.zeros((5, 5, 5), dtype=bool)
    mask[1, 1, 1] = True
    mask[1, 1, 2] = True
    mask[4, 4, 4] = True
    grid = np.arange(5, dtype=float)
    result = label_high_score_components(mask, grid, grid, grid)
    assert result["high_score_component_count"] == 2
    assert result["multi_region_warning"] is True
    assert result["largest_component_box"]["point_count"] == 2

