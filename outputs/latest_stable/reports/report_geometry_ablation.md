# 三维几何消融报告

每个案例都重新合成运动学 DAS-like 数据，并在三维诊断网格上扫描。

| geometry case | best | y_span_m | depth_span_m | source_y_span_m | receiver_y_span_m | flag |
|---|---|---:|---:|---:|---:|---|
| geometry_case_A_single_side_line | x=60.0, y=10.0, h=2.5, error=1.118033988749895 | 4 | 0 | 0 | 0 | low |
| geometry_case_B_non_collinear_sources | x=60.0, y=8.0, h=2.5, error=1.118033988749895 | 6 | 0 | 3.96 | 0 | low |
| geometry_case_C_two_side_sources | x=60.0, y=8.0, h=2.5, error=1.118033988749895 | 4 | 0 | 18 | 0 | low |
| geometry_case_D_polyline_receiver | x=60.0, y=10.0, h=2.5, error=1.118033988749895 | 4 | 0 | 0 | 1.44 | low |

- y 方向跨度改善最明显：`geometry_case_A_single_side_line`。
- depth 稳定性最好：`geometry_case_A_single_side_line`。
- 真值误差最小：`geometry_case_A_single_side_line`。

若非共线或双侧震源明显缩小 y/depth 跨度，说明当前场景更应优先增加震源方位覆盖，而不是只调 score。