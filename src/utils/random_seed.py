"""随机种子工具。"""

from __future__ import annotations

import random
from types import SimpleNamespace

import numpy as np


def set_random_seed(params: SimpleNamespace) -> np.random.Generator:
    """设置 Python 和 NumPy 随机种子。

    物理意义：
        随机性主要来自噪声模拟。固定 random_seed 后，同一组参数应产生相同的
        噪声和合成数据，便于科研复现实验。

    输出：
        numpy.random.Generator，可继续传给需要随机数的函数。
    """

    random.seed(params.project.random_seed)
    np.random.seed(params.project.random_seed)
    return np.random.default_rng(params.project.random_seed)
