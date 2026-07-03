"""稳定三维主流程封装。"""

from __future__ import annotations

from typing import Any

from main import args_to_params, parse_arguments
from src.pipeline.run_full_pipeline import run_full_pipeline


def build_current_params(extra_args: list[str] | None = None):
    """构建当前稳定算法参数。

    参数仍由根目录 main.py 的 argparse 定义和校验。这里仅提供稳定入口的默认覆盖：
    使用 full_pipeline、layered velocity 和 multi_attribute_unweighted 主定位。
    """

    args = [
        "--task",
        "full_pipeline",
        "--velocity-model-type",
        "layered",
        "--active-score-kind",
        "multi_attribute_unweighted",
    ]
    if extra_args:
        args.extend(extra_args)
    return args_to_params(parse_arguments(args))


def run_current_pipeline(extra_args: list[str] | None = None) -> dict[str, Any]:
    """运行当前稳定三维算法主流程。"""

    params = build_current_params(extra_args)
    return run_full_pipeline(params)


def smoke_current_pipeline() -> dict[str, Any]:
    """轻量 smoke 配置，供测试确认稳定入口可调用。"""

    return {
        "params": build_current_params(
            [
                "--save-figures",
                "false",
                "--save-wavefield-snapshots",
                "false",
                "--save-wavefield-animation",
                "false",
                "--max-shot-gather-figures",
                "0",
                "--preprocessing-ablation-enabled",
                "false",
                "--multi-attribute-ablation-enabled",
                "false",
                "--geometry-ablation-enabled",
                "false",
                "--velocity-ablation-enabled",
                "false",
                "--export-latest-stable",
                "false",
            ]
        )
    }
