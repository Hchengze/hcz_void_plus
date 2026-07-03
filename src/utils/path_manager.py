"""输出目录管理。"""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace


def ensure_output_subdirs(params: SimpleNamespace) -> dict[str, Path]:
    """创建本次运行所需的规范化输出子目录。

    Stage 2 统一内部结构：
        arrays/ 保存 arr_ 前缀数组；
        figures/ 保存 fig_ 前缀普通静态图；
        snapshots/ 保存 snap_ 前缀运动学伪波场快照；
        animations/ 保存 anim_ 前缀动图；
        reports/ 保存 report_ 前缀 Markdown 报告；
        logs/ 保存 log_ 前缀日志；
        metadata/ 保存 meta_ 和 params_ 前缀可追溯信息。

    限制：
        不创建 config 或 para 目录；同一类数据只按规范名称保存一次。
    """

    root = Path(params.derived.output_run_dir)
    subdirs = {
        "root": root,
        "arrays": root / "arrays",
        "figures": root / "figures",
        "snapshots": root / "snapshots",
        "animations": root / "animations",
        "reports": root / "reports",
        "logs": root / "logs",
        "metadata": root / "metadata",
    }
    for path in subdirs.values():
        path.mkdir(parents=True, exist_ok=True)
    return subdirs
