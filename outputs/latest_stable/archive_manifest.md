# archive manifest

Stage 5J 不再把历史图件堆进 latest_stable 当前精选目录。

## 已移出当前精选视图的内容

- 旧 x-y pseudo wavefield 和单炮地表快照：Stage 5J 由 x-y-depth 三维运动学体响应 proxy 替代。
- 未叠加速度模型上下文的旧 shot gather：Stage 5J 由 direct/scatter 到时曲线与 uniform/layered 对比炮集替代。
- 无 attenuation context 的旧 gather 图：Stage 5J 由经验 Q attenuation 前后对照替代。
- acoustic2d shot gather 与 acoustic2d wavefield snapshots：F2 基础设施验证，不再占据当前主视图。
- forward_engine_comparison 与 layered_kinematic_vs_baseline_gather：转为历史诊断，不再进入 Stage 5J 精选。
- 重复 confidence/uncertainty 图：仅保留能说明三维不确定性的少量定位图。
- 旧 core/diagnostics/uncertainty/reference_only 细分类目录：继续合并为 forward/localization/error_analysis 三类。

完整历史输出仍可从时间戳运行目录或 Git 历史追溯；latest_stable 只表达当前最稳定结论。