from pathlib import Path


def test_testing_strategy_documents_three_layers():
    text = Path("docs/testing_strategy.md").read_text(encoding="utf-8")
    tests_readme = Path("tests/README.md").read_text(encoding="utf-8")
    for key in ["core_contract", "lightweight_smoke", "archive_or_reduce"]:
        assert key in text
        assert key in tests_readme
    assert "三维" in text
    assert "latest_stable" in text
    assert "tree snapshot" in text
    assert "manual review" in text
    assert "不再为每一张静态图" in text
