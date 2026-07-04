# archive manifest

Stage 5G 不再把历史图件堆进 latest_stable 当前精选目录。

## 已移出当前精选视图的内容

- acoustic2d shot gather 与 acoustic2d wavefield snapshots：F2 基础设施验证，不再占据当前主视图。
- forward_engine_comparison 与 layered_kinematic_vs_baseline_gather：转为历史诊断，不再进入 Stage 5G 精选。
- Stage 5E sensitivity/pick 旧图：由 Stage 5G Rayleigh benchmark 矩阵和速度误差图替代。
- 重复 confidence/uncertainty 图：仅保留能说明三维不确定性的 1-2 张。
- 旧 core/diagnostics/uncertainty/reference_only 细分类目录：合并为 forward/localization/error_analysis 三类。

完整历史输出仍可从时间戳运行目录或 Git 历史追溯；latest_stable 只表达当前最稳定结论。