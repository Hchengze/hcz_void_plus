from main import args_to_params, parse_arguments
from src.forward.forward_registry import get_forward_engine_spec, list_forward_engines


def test_forward_registry_lists_stage5b_engines():
    engines = list_forward_engines()
    assert "kinematic_baseline" in engines
    assert "layered_kinematic" in engines
    assert "acoustic2d_prototype" in engines
    assert get_forward_engine_spec("layered_kinematic").is_default_localization_forward is True
    assert get_forward_engine_spec("acoustic2d_prototype").is_default_localization_forward is False


def test_default_forward_engine_is_layered_kinematic():
    params = args_to_params(parse_arguments([]))
    assert params.forward.engine == "layered_kinematic"
    assert params.forward.acoustic2d_enabled is False
    assert params.forward.acoustic2d_snapshot_count == 6
