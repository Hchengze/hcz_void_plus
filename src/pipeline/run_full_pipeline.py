"""Stage 1 full_pipeline 占位流程。"""

from __future__ import annotations

from types import SimpleNamespace
from typing import Any

from src.pipeline.run_forward_pipeline import run_forward_pipeline


def run_full_pipeline(params: SimpleNamespace) -> dict[str, Any]:
    """运行当前阶段的 full_pipeline。

    Stage 1 的 full_pipeline 先调用 run_forward_pipeline，报告和 metadata 中会说明
    scan、confidence、robustness、多炮联合定位和局部全波场验证属于后续阶段。
    """

    result = run_forward_pipeline(params)
    result["full_pipeline_note"] = (
        "Stage 1 full_pipeline currently delegates to forward pipeline; "
        "scan/confidence/robustness will be implemented in later stages."
    )
    return result
