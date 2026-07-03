"""2D elastic 正演规划包。

Stage 5B 只建立设计和占位入口，不实现完整 elastic2d。真实 Rayleigh/free-surface/
void scattering 的局部全波场验证应在后续阶段进入本包。
"""

from src.forward.elastic2d.placeholder import elastic2d_status

__all__ = ["elastic2d_status"]
