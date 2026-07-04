"""2D elastic 正演规划包。

Stage 5B 只建立设计和占位入口，不实现完整 elastic2d。真实 Rayleigh/free-surface/
void scattering 的局部全波场验证应在后续阶段进入本包。
"""

from src.forward.elastic2d.das_response import build_elastic_das_response, compute_gauge_length_strain
from src.forward.elastic2d.elastic_fdtd import Elastic2DResult, run_elastic2d_prototype
from src.forward.elastic2d.grid import Elastic2DGrid
from src.forward.elastic2d.model import Elastic2DModel, build_uniform_elastic_model
from src.forward.elastic2d.placeholder import elastic2d_status

__all__ = [
    "Elastic2DGrid",
    "Elastic2DModel",
    "Elastic2DResult",
    "build_elastic_das_response",
    "build_uniform_elastic_model",
    "compute_gauge_length_strain",
    "elastic2d_status",
    "run_elastic2d_prototype",
]
