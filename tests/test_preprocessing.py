import numpy as np

from main import args_to_params, parse_arguments
from src.preprocessing.agc import apply_agc
from src.preprocessing.bandpass import bandpass_filter
from src.preprocessing.preprocessing_pipeline import run_preprocessing_pipeline
from src.preprocessing.trace_normalization import trace_normalization


def test_preprocessing_keeps_shape():
    data = np.random.default_rng(0).normal(size=(2, 128, 8))
    assert bandpass_filter(data, 0.001, 5.0, 80.0).shape == data.shape
    assert apply_agc(data, 0.001, 0.02).shape == data.shape
    assert trace_normalization(data, "rms").shape == data.shape


def test_preprocessing_pipeline_returns_processed_data():
    params = args_to_params(parse_arguments(["--fiber-channel-count", "8", "--source-shot-count", "2", "--gauge-length-m", "4"]))
    data = np.random.default_rng(1).normal(size=(2, params.derived.nt, 8))
    processed, info = run_preprocessing_pipeline(data, params)
    assert processed.shape == data.shape
    assert info["enabled"] is True
