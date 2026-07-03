# Workflow

Stage 2 运行流程：

1. `main.py` 解析所有命令行参数。
2. `main.py` 校验原始参数。
3. `main.py` 派生 `channel_x`、`receiver_xyz`、`shot_x`、`source_xyz`、`time_axis`、`nt`、扫描网格和输出目录。
4. forward pipeline 生成 DAS-like 运动学多炮合成数据。
5. forward pipeline 保存中文几何图、有限数量炮集图、运动学地表响应示意图和可选 GIF。
6. scan pipeline 预测直达波到时。
7. scan pipeline 可选执行直达波 mute。
8. scan pipeline 对 x-y-h 候选网格计算理论散射走时。
9. scan pipeline 沿走时时间窗提取局部能量，生成 `score_volume`。
10. scan pipeline 可选加入 Rayleigh 简化深度敏感性权重，保存 raw 和 depth-weighted score volume。
11. scan pipeline 输出 best_location、truth_error、扫描切片图、路径剖面、深度敏感性图、绕射走时曲线和中文报告。

`full_pipeline` 会完成正演、伪波场、扫描和综合报告。

所有结果仍然必须标注 `kinematic approximation` 和 `DAS-like response approximation`。

地表响应图不能称为真实波场快照；它只是 Rayleigh 波走时控制的地表响应示意。绕射走时曲线图是判断当前基础扫描是否合理的核心 QC 图件。
