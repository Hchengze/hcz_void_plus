from pathlib import Path


def test_reference_algorithm_matrix_contains_core_algorithm_points():
    text = Path("docs/reference_algorithm_matrix.md").read_text(encoding="utf-8")
    required = [
        "直达面波压制",
        "FK / f-v",
        "绕射走时曲线匹配",
        "matched wavelet score",
        "semblance",
        "frequency shift",
        "三维 source-receiver-candidate",
        "三维高分区不确定性表达",
    ]
    for item in required:
        assert item in text
    assert "本项目实现函数" in text
    assert "对应测试" in text
    assert "对应输出图" in text

