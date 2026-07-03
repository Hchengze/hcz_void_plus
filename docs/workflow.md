# Workflow

Stage 4A 运行流程：

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
12. full_pipeline 对 score volume 和最佳候选点执行基础置信度诊断。
13. full_pipeline 输出 `arr_confidence_metrics.json`、`fig_confidence_diagnostics.png` 和 `report_confidence.md`。
14. Stage 3B 同时比较 unweighted_best 与 weighted_best，检查深度边界、宽 y 高分区、unweighted/weighted 分歧和浅部偏置。
15. Stage 3C 根据 warning、score_method 对比和三维高分区生成 recommended_location 或不确定性区间。
16. Stage 4A 在扫描前执行可选预处理，包括 bandpass、AGC、包络、道归一化和简化 f-k 滤波。
17. Stage 4A 使用 multi_attribute score，将 energy、normalized energy、matched wavelet 和 semblance 按权重组合。
18. Stage 4A 输出三维几何、异常体散射点、多属性评分和 depth prior 敏感性诊断图。
19. full_pipeline 默认刷新 `outputs/latest_stable/`，只保留精选图件、报告、metadata 和 `summary.md`，供人工快速检查。

`full_pipeline` 会完成正演、地表响应示意、扫描、基础置信度诊断、综合报告和 latest_stable 精选导出。

所有结果仍然必须标注 `kinematic approximation` 和 `DAS-like response approximation`。

地表响应图不能称为真实波场快照；它只是 Rayleigh 波走时控制的地表响应示意。绕射走时曲线图是判断当前基础扫描是否合理的核心 QC 图件。

Stage 3 的 confidence flag 只是规则型科研诊断标签，不是概率置信度，也不是工程确诊结论。

Stage 3C 的 `arr_score_volume.npy` 仍作为当前展示主结果保留，但报告会说明它对应 unweighted 还是 depth-weighted；`arr_score_volume_unweighted.npy`、`arr_score_volume_depth_weighted.npy` 和 `arr_score_volume_active.npy` 始终并列保存。

Stage 4A 后，默认主结果来自 `multi_attribute_unweighted`，depth weighting 不再自动支配主定位；它只作为 Rayleigh 浅层敏感性的简化辅助诊断。当前几何、走时和扫描均使用三维 `source_xyz/receiver_xyz/candidate_xyz`，但仍是 3D kinematic geometry，不是完整三维弹性波全波场模拟。
# 历史阶段提示

本文件保留 Stage 4A 运行流程说明。Stage 5A 已将稳定算法沉淀到 `code/current_3d_algorithm/`，并将默认速度模型升级为 `layered`。当前主线请以 `README.md`、`docs/current_status.md` 和 `docs/current_algorithm_boundary.md` 为准。
