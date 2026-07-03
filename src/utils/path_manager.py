"""输出目录管理。"""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace


def ensure_output_subdirs(params: SimpleNamespace) -> dict[str, Path]:
    """创建本次运行所需的输出子目录。

    输出目录约定：
        saved_arrays/ 保存 numpy 数组；
        figures/ 保存几何图和炮集图；
        reports/ 保存 Markdown 报告；
        logs/ 保存简要运行日志。

    限制：
        不创建 config 或 para 目录；参数快照直接写入本次 run 根目录。
    """

    root = Path(params.derived.output_run_dir)
    subdirs = {
        "root": root,
        "arrays": root / "saved_arrays",
        "figures": root / "figures",
        "reports": root / "reports",
        "logs": root / "logs",
    }
    for path in subdirs.values():
        path.mkdir(parents=True, exist_ok=True)
    return subdirs
