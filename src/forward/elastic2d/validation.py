"""elastic2d validation 参数辅助函数。"""

from __future__ import annotations

from types import SimpleNamespace

from src.validation.common import clone_params


def make_elastic2d_validation_params(params: SimpleNamespace) -> SimpleNamespace:
    """生成轻量 elastic2d validation 参数副本。

    full_pipeline 默认三维扫描已经有较多诊断。为保证本地快速可跑，elastic2d 验证
    在副本中限制网格和时长；所有原始默认值仍由 main.py 提供。
    """

    trial = clone_params(params)
    trial.forward.elastic2d_nx = min(params.forward.elastic2d_nx, 81)
    trial.forward.elastic2d_nz = min(params.forward.elastic2d_nz, 51)
    trial.forward.elastic2d_duration_s = min(params.forward.elastic2d_duration_s, 0.08)
    trial.forward.elastic2d_snapshot_count = min(params.forward.elastic2d_snapshot_count, 4)
    trial.forward.elastic2d_void_x_m = None
    trial.forward.elastic2d_void_z_m = None
    trial.forward.elastic2d_void_radius_m = min(params.forward.elastic2d_void_radius_m, 0.9)
    return trial
