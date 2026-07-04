from pathlib import Path

import sys

CODE_DIR = str(Path("code").resolve())
if CODE_DIR not in sys.path:
    sys.path.insert(0, CODE_DIR)

from current_3d_algorithm.stable_api import get_current_algorithm_summary


def test_document_cleanup_report_and_archive_exist():
    report = Path("docs/document_cleanup_report.md")
    archive_readme = Path("docs/archive/README.md")
    assert report.exists()
    assert archive_readme.exists()
    text = report.read_text(encoding="utf-8")
    assert "current" in text
    assert "archive" in text
    assert "delete" in text
    assert "generated_only" in text


def test_current_status_is_not_stale_stage5a_or_stage5c():
    status = Path("docs/current_status.md").read_text(encoding="utf-8")
    assert "Stage 5G" in status
    assert "active velocity model" in status
    assert "active forward engine" in status
    assert "当前进入 Stage 5A" not in status
    assert "当前进入 Stage 5C" not in status


def test_current_entrypoints_are_stage_consistent():
    readme = Path("README.md").read_text(encoding="utf-8")
    status = Path("docs/current_status.md").read_text(encoding="utf-8")
    boundary = Path("docs/current_algorithm_boundary.md").read_text(encoding="utf-8")
    summary = get_current_algorithm_summary()
    assert "Stage 5G" in readme
    assert "Stage 5G" in status
    assert "Stage 5G" in boundary
    assert summary["stage"] == "Stage 5G"
