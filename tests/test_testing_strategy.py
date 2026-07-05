from pathlib import Path


def test_testing_strategy_documents_stage5k_reduction():
    text = Path("docs/testing_strategy.md").read_text(encoding="utf-8")
    tests_readme = Path("tests/README.md").read_text(encoding="utf-8")
    for key in ["core_contract", "lightweight_smoke", "Stage 5K"]:
        assert key in text
        assert key in tests_readme
    assert "observation_kernel_3d" in text
    assert "receiver-consistent imaging" in text
    assert "latest_stable" in text
    assert "test_latest_stable_curator.py" in text
    assert "test_manual_review_readiness.py" in text
