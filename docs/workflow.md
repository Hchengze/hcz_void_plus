# Workflow

Stage 2 运行流程：

1. `main.py` 解析所有命令行参数。
2. `main.py` 校验原始参数。
3. `main.py` 派生 `channel_x`、`receiver_xyz`、`shot_x`、`source_xyz`、`time_axis`、`nt`、扫描网格和输出目录。
4. forward pipeline 生成 DAS-like 运动学多炮合成数据。
5. forward pipeline 保存中文几何图、有限数量炮集图、运动学伪波场快照和可选 GIF。
6. scan pipeline 预测直达波到时。
7. scan pipeline 可选执行直达波 mute。
8. scan pipeline 对 x-y-h 候选网格计算理论散射走时。
9. scan pipeline 沿走时时间窗提取局部能量，生成 `score_volume`。
10. scan pipeline 输出 best_location、truth_error、扫描切片图和中文报告。

`full_pipeline` 会完成正演、伪波场、扫描和综合报告。

所有结果仍然必须标注 `kinematic approximation` 和 `DAS-like response approximation`。
