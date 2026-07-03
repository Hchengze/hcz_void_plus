# depth prior 敏感性报告

本报告基于 unweighted score volume 快速评估不同 Rayleigh depth prior 因子对 best depth 的影响。

| factor | penetration_depth_m | best_location | best_depth_at_boundary |
|---|---:|---|---|
| 0.5 | 4.333333333333333 | {'x_m': 60.0, 'y_m': 10.0, 'depth_m': 0.5} | True |
| 1.0 | 8.666666666666666 | {'x_m': 60.0, 'y_m': 10.0, 'depth_m': 0.5} | True |
| 2.0 | 17.333333333333332 | {'x_m': 60.0, 'y_m': 10.0, 'depth_m': 0.5} | True |
| off | None | {'x_m': 60.0, 'y_m': 10.0, 'depth_m': 2.5} | False |

该诊断不是严格 Rayleigh 模态核，只用于检查 depth prior 是否支配定位结果。