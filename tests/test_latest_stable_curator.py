from pathlib import Path

from src.utils.latest_stable_curator import audit_latest_stable_files


def test_latest_stable_curator_accepts_stage5h_count_window(tmp_path):
    latest = tmp_path / "latest_stable"
    for category, count in {
        "forward": 9,
        "localization": 6,
        "error_analysis": 6,
    }.items():
        folder = latest / "figures" / category
        folder.mkdir(parents=True, exist_ok=True)
        for index in range(count):
            (folder / f"fig_{category}_{index}.png").write_bytes(b"fake")
    for category, count in {
        "forward": 2,
        "localization": 0,
        "error_analysis": 0,
    }.items():
        folder = latest / "animations" / category
        folder.mkdir(parents=True, exist_ok=True)
        for index in range(count):
            (folder / f"anim_{category}_{index}.gif").write_bytes(b"fake")
    for category, count in {
        "forward": 5,
        "localization": 1,
        "error_analysis": 6,
    }.items():
        folder = latest / "reports" / category
        folder.mkdir(parents=True, exist_ok=True)
        for index in range(count):
            (folder / f"report_{category}_{index}.md").write_text("ok", encoding="utf-8")

    result = audit_latest_stable_files(latest)
    assert result["stage"] == "Stage 5H"
    assert result["latest_stable_total_figure_count"] == 21
    assert result["latest_stable_total_animation_count"] == 2
    assert result["latest_stable_total_report_count"] == 12
    assert result["status"] == "pass"


def test_latest_stable_curator_warns_when_root_png_exists(tmp_path):
    latest = tmp_path / "latest_stable"
    (latest / "figures").mkdir(parents=True)
    (latest / "figures" / "flat.png").write_bytes(b"fake")
    result = audit_latest_stable_files(latest)
    assert result["figures_root_png_count"] == 1
    assert result["status"] == "warning"
