from pathlib import Path


def test_latest_stable_has_only_three_result_categories():
    latest = Path("outputs/latest_stable")
    expected = {"forward", "localization", "error_analysis"}
    assert {path.name for path in (latest / "figures").iterdir() if path.is_dir()} == expected
    assert {path.name for path in (latest / "animations").iterdir() if path.is_dir()} == expected
    assert {path.name for path in (latest / "reports").iterdir() if path.is_dir()} == expected


def test_latest_stable_static_and_animation_counts_are_controlled():
    latest = Path("outputs/latest_stable")
    static_count = len(list((latest / "figures").glob("*/*.png")))
    animation_count = len(list((latest / "animations").glob("*/*.gif")))
    assert 18 <= static_count <= 24
    assert 2 <= animation_count <= 4
