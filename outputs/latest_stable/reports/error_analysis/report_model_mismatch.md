# 正演模型与扫描模型错配报告

真实道路介质与反演速度假设通常不一致。本报告用轻量三维运动学实验检查这种错配对定位的影响。

| case | forward model | scan model | best | error_m | y_span_m | depth_span_m | flag |
|---|---|---|---|---:|---:|---:|---|
| uniform_forward_uniform_scan | uniform | uniform | x=60.0, y=10.0, h=2.5, error=1.118033988749895 | 1.118 | 8 | 5 | low |
| layered_forward_layered_scan | layered | layered | x=60.0, y=10.0, h=2.5, error=1.118033988749895 | 1.118 | 4 | 0 | low |
| layered_forward_uniform_scan | layered | uniform | x=64.0, y=18.0, h=7.5, error=10.828203913853857 | 10.83 | 16 | 5 | low |
| localized_low_velocity_forward_uniform_scan | localized_low_velocity_zone | uniform | x=60.0, y=4.0, h=7.5, error=6.726812023536855 | 6.727 | 16 | 3 | low |
| layered_perturbation_forward_layered_scan | layered_with_anomaly_perturbation | layered | x=60.0, y=10.0, h=2.5, error=1.118033988749895 | 1.118 | 12 | 0 | low |

## 风险解释

- 误差最小案例：`uniform_forward_uniform_scan`。
- 误差最大案例：`layered_forward_uniform_scan`。
- 当前最低推荐速度模型：`layered`。
- 如果真实为 layered 但扫描仍用 uniform，depth 与 y-depth 耦合可能出现系统偏差。
- 本报告只用于科研算法风险诊断，不能作为工程确诊或速度结构反演结论。