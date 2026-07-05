import numpy as np

from main import args_to_params, parse_arguments
from src.forward.amplitude_model import compute_direct_amplitude, compute_scatter_amplitude
from src.model.attenuation_model import build_attenuation_model


def _params(extra=None):
    args = ["--save-figures", "false"]
    if extra:
        args.extend(extra)
    return args_to_params(parse_arguments(args))


def test_q_attenuation_decay_reduces_longer_travel_time():
    params = _params()
    attenuation = build_attenuation_model(params)

    short = attenuation.q_decay(np.array([0.05]), params.task.wavelet_dominant_frequency_hz, np.array([35.0]))
    long = attenuation.q_decay(np.array([0.30]), params.task.wavelet_dominant_frequency_hz, np.array([35.0]))

    assert 0.0 < float(long[0]) < float(short[0]) <= 1.0
    assert attenuation.layer_q.tolist() == [25.0, 35.0, 50.0, 80.0]


def test_direct_and_scatter_amplitude_apply_q_and_preserve_scatter_sign():
    params = _params()
    params_no_q = _params(["--attenuation-enabled", "false"])
    source = np.array([0.0, 0.0, 0.0])
    scatter = np.array([5.0, 2.0, 3.0])
    receiver = np.array([10.0, 0.0, 0.0])
    travel_time = np.array(0.12)

    attenuated_direct = compute_direct_amplitude(params, source, receiver, travel_time)
    reference_direct = compute_direct_amplitude(params_no_q, source, receiver, travel_time)
    assert float(attenuated_direct) < float(reference_direct)

    signed_scatter = compute_scatter_amplitude(params, source, scatter, receiver, travel_time, -0.8)
    assert float(signed_scatter) < 0.0
