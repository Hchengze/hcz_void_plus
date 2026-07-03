# 稳定输出说明

当前稳定成果默认导出到：

```text
outputs/latest_stable/
```

该目录只保存最值得人工检查的精选图件、报告和 metadata。完整数组、快照帧和中间结果仍保存在时间戳运行目录中，默认不全部提交到 Git。

Stage 5A 以后，`latest_stable` 应重点包含：

- `fig_velocity_model_comparison.png`
- `fig_layered_velocity_profile.png`
- `fig_velocity_model_travel_time_residuals.png`
- `fig_model_mismatch_error_summary.png`
- `report_velocity_model_ablation.md`
- `report_model_mismatch.md`

这些输出用于判断分层/非均匀速度模型是否改变定位结果和不确定性，不用于工程确诊。
