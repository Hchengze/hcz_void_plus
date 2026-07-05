from pathlib import Path


def test_stage5j_forward_animation_outputs_exist():
    latest = Path("outputs/latest_stable")
    animations = [
        latest / "animations" / "forward" / "anim_multishot_forward_overview.gif",
        latest / "animations" / "forward" / "anim_single_shot_volume_wavefield.gif",
    ]
    for path in animations:
        assert path.exists(), path
        assert path.stat().st_size > 2048
