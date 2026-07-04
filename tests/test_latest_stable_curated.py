from pathlib import Path


def test_latest_stable_curated_structure_exists():
    latest = Path("outputs/latest_stable")
    assert (latest / "README.md").exists()
    assert (latest / "archive_manifest.md").exists()
    for category in ["core", "forward", "localization", "uncertainty", "diagnostics"]:
        assert (latest / "figures" / category).exists()
        assert (latest / "reports" / category).exists()


def test_latest_stable_root_figures_are_not_flat_png_dump():
    latest = Path("outputs/latest_stable")
    root_pngs = list((latest / "figures").glob("*.png"))
    assert len(root_pngs) == 0
    assert len(list((latest / "figures" / "core").glob("*.png"))) <= 8
    summary = (latest / "summary.md").read_text(encoding="utf-8")
    assert "Stage 5C" in summary
    assert "latest_stable_curated" in summary
