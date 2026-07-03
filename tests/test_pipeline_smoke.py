from pathlib import Path

from main import args_to_params, create_output_dir, parse_arguments
from src.pipeline.run_forward_pipeline import run_forward_pipeline


def test_pipeline_smoke_generates_output_and_metadata(tmp_path):
    params = args_to_params(
        parse_arguments(
            [
                "--task",
                "forward",
                "--run-name",
                "pytest_smoke",
                "--output-root-dir",
                str(tmp_path),
                "--fiber-channel-count",
                "12",
                "--source-shot-count",
                "2",
                "--time-record-length-s",
                "0.2",
                "--gauge-length-m",
                "4",
                "--save-figures",
                "false",
            ]
        )
    )
    create_output_dir(params)
    result = run_forward_pipeline(params)

    output_dir = Path(result["output_run_dir"])
    assert output_dir.exists()
    assert (output_dir / "metadata.json").exists()
    assert (output_dir / "params_snapshot.json").exists()
    assert (output_dir / "saved_arrays" / "synthetic_data.npy").exists()
