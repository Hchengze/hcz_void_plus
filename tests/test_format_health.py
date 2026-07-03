from pathlib import Path


def test_key_python_files_are_not_one_line():
    key_files = [
        Path("main.py"),
        Path("src/localization/attribute_scoring.py"),
        Path("src/localization/multishot_scan.py"),
        Path("src/confidence/uncertainty_region.py"),
        Path("src/utils/stable_export.py"),
        Path("tests/test_confidence.py"),
    ]
    for path in key_files:
        text = path.read_text(encoding="utf-8")
        assert text.count("\n") > 20, f"{path} looks too compressed for audit"
        assert "def " in text or path.suffix == ".md"


def test_markdown_files_have_normal_structure():
    key_files = [
        Path("README.md"),
        Path("docs/reference_algorithm_matrix.md"),
        Path("docs/reference_inventory.md"),
    ]
    for path in key_files:
        text = path.read_text(encoding="utf-8")
        assert text.count("\n") > 10
        assert "#" in text

    latest_summary = Path("outputs/latest_stable/summary.md")
    if latest_summary.exists():
        text = latest_summary.read_text(encoding="utf-8")
        assert text.count("\n") > 20
        assert "latest_stable" in text

