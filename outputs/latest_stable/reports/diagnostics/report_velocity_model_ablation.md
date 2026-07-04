# 速度模型消融报告

本报告比较 uniform、layered、lateral gradient、localized low velocity zone 等等效 Rayleigh 速度模型。
所有结果仍是 straight-ray kinematic approximation，不是 3D elastic wavefield。

| velocity model | best | error_m | y_span_m | depth_span_m | residual_rms_ms | flag |
|---|---|---:|---:|---:|---:|---|
| uniform | x=60.0, y=10.0, h=2.5, error=1.118033988749895 | 1.118 | 8 | 5 | 0 | low |
| layered | x=60.0, y=10.0, h=2.5, error=1.118033988749895 | 1.118 | 4 | 0 | 57.08 | low |
| lateral_gradient | x=60.0, y=10.0, h=2.5, error=1.118033988749895 | 1.118 | 6 | 5 | 5.644 | low |
| localized_low_velocity_zone | x=60.0, y=8.0, h=3.5, error=1.118033988749895 | 1.118 | 4 | 6 | 12.7 | low |
| layered_with_anomaly_perturbation | x=60.0, y=12.0, h=2.5, error=3.0413812651491097 | 3.041 | 12 | 0 | 69.38 | low |

## 结论

- 真值误差最小模型：`uniform`。
- 深度误差最小模型：`uniform`。
- 相对 uniform 走时残差最大模型：`layered_with_anomaly_perturbation`。
- 如果 layered 与 uniform 的走时残差不可忽略，真实数据反演不应继续只依赖 uniform 速度。
- 局部低速带可能导致定位偏移，也可能被误解释为空洞响应，因此必须在报告中作为风险列出。