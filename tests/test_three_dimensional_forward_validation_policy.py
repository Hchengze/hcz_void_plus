from pathlib import Path


def test_three_dimensional_forward_validation_policy_exists_and_sets_gate():
    path = Path("docs/three_dimensional_forward_validation_policy.md")
    assert path.exists()
    text = path.read_text(encoding="utf-8")
    assert "三维道路 DAS-like" in text
    assert "source_xyz" in text
    assert "receiver_xyz" in text
    assert "candidate_xyz" in text
    assert "x-y-depth" in text
    assert "2D elastic" in text
    assert "不得直接替代" in text or "不能直接替代" in text
    assert "ready_for_2p5d" in text
    assert "Rayleigh benchmark" in text
