from pathlib import Path

from tools.check_text_health import collect_text_health, default_paths


def test_key_text_files_have_real_lf_lines_and_no_cr_only():
    paths = default_paths(Path("."))
    results = collect_text_health(paths)
    assert results
    by_name = {Path(item.path).as_posix(): item for item in results}
    for required in [
        "README.md",
        "main.py",
        "docs/forward_modeling_roadmap.md",
        "docs/forward_modeling_boundary.md",
        "docs/elastic2d_forward_design.md",
        "src/forward/acoustic2d/acoustic_fdtd.py",
        "src/forward/forward_registry.py",
        "code/current_3d_algorithm/stable_api.py",
        "outputs/latest_stable/summary.md",
    ]:
        assert required in by_name
        assert by_name[required].cr_only_count == 0
        assert by_name[required].logical_line_count >= 5
        assert by_name[required].healthy is True


def test_text_health_reports_line_statistics():
    results = collect_text_health(default_paths(Path(".")))
    line_counts = {Path(item.path).name: item.logical_line_count for item in results}
    assert line_counts["README.md"] > 20
    assert line_counts["main.py"] > 100
    assert line_counts["summary.md"] > 20
