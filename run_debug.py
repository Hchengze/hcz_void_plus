"""小规模调试入口。

run_debug.py 不维护第二套算法逻辑，只是把一组更小的命令行参数交给 main.py。
所有默认参数、派生参数和校验仍然由 main.py 统一管理。
"""

from main import main


if __name__ == "__main__":
    main(
        [
            "--task",
            "debug",
            "--run-name",
            "debug_small",
            "--fiber-channel-count",
            "41",
            "--source-shot-count",
            "3",
            "--time-record-length-s",
            "0.45",
            "--max-shot-gather-figures",
            "2",
            "--wavefield-snapshot-count",
            "4",
            "--wavefield-grid-nx",
            "60",
            "--wavefield-grid-ny",
            "30",
        ]
    )
