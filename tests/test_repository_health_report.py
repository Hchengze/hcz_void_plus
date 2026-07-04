from pathlib import Path

from src.validation.repository_health import build_repository_health_report, write_repository_health_report


def test_repository_health_report_can_be_generated(tmp_path):
    latest = Path("outputs/latest_stable")
    result = build_repository_health_report(Path.cwd(), latest)
    assert "head_commit" in result
    assert "text_health" in result
    assert "latest_stable_stage5g" in result
    assert result["figures_root_png_count"] == 0
    out = tmp_path / "report_repository_health.md"
    write_repository_health_report(out, result)
    text = out.read_text(encoding="utf-8")
    assert "repository health" in text.lower() or "仓库" in text
    assert "Stage 5G" in text
