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
                "true",
                "--save-wavefield-animation",
                "false",
                "--wavefield-snapshot-count",
                "3",
                "--wavefield-grid-nx",
                "30",
                "--wavefield-grid-ny",
                "20",
                "--max-shot-gather-figures",
                "1",
            ]
        )
    )
    create_output_dir(params)
    result = run_forward_pipeline(params)

    output_dir = Path(result["output_run_dir"])
    assert output_dir.exists()
    for name in ["arrays", "figures", "snapshots", "animations", "reports", "logs", "metadata"]:
        assert (output_dir / name).exists()
    assert (output_dir / "metadata" / "meta_run.json").exists()
    assert (output_dir / "metadata" / "params_snapshot.json").exists()
    assert (output_dir / "arrays" / "arr_synthetic_data.npy").exists()
    assert (output_dir / "figures" / "fig_shot_gather_000.png").exists()
    assert not (output_dir / "figures" / "fig_shot_gather_001.png").exists()
    assert len(list((output_dir / "snapshots").glob("snap_*.png"))) == 3
    assert not (output_dir / "animations" / "anim_pseudo_wavefield.gif").exists()


def test_pipeline_can_disable_wavefield_snapshots(tmp_path):
    params = args_to_params(
        parse_arguments(
            [
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
                "--save-wavefield-snapshots",
                "false",
                "--save-wavefield-animation",
                "false",
            ]
        )
    )
    create_output_dir(params)
    result = run_forward_pipeline(params)
    output_dir = Path(result["output_run_dir"])
    assert len(list((output_dir / "snapshots").glob("snap_*.png"))) == 0
