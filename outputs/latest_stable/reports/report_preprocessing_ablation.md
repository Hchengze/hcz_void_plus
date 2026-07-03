# 预处理消融验证报告

本报告比较不同预处理组合对三维运动学扫描的影响。消融使用轻量三维诊断网格，不是大规模鲁棒性扫描。

| case | best | y_span_m | depth_span_m | diffraction_ratio | direct_residual | flag |
|---|---|---:|---:|---:|---:|---|
| none | x=60.0, y=8.0, h=2.5, error=1.118033988749895 | 8 | 0 | 0.1964 | 0.8795 | low |
| bandpass | x=60.0, y=8.0, h=2.5, error=1.118033988749895 | 8 | 0 | 0.196 | 0.8785 | low |
| bandpass_trace_normalization | x=60.0, y=8.0, h=2.5, error=1.118033988749895 | 6 | 0 | 0.1958 | 0.8444 | low |
| bandpass_trace_normalization_taper_direct_mute | x=60.0, y=10.0, h=2.5, error=1.118033988749895 | 4 | 0 | 0.5364 | 0.4243 | low |
| bandpass_trace_normalization_fk_filter | x=60.0, y=8.0, h=2.5, error=1.118033988749895 | 6 | 0 | 0.184 | 0.824 | low |
| bandpass_trace_normalization_envelope | x=60.0, y=10.0, h=2.5, error=1.118033988749895 | 6 | 0 | 0.1985 | 0.8412 | low |

## 结论

- 最小真值误差组合：`none`。
- y/depth 跨度最小组合：`bandpass_trace_normalization_taper_direct_mute`。
- 若某组合降低 direct_residual 但同时降低 diffraction_ratio，应视为可能误伤有效绕射。
- 当前仍是 kinematic approximation 与 DAS-like response approximation，不能作为工程确诊。