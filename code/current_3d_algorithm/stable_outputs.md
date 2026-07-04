# 稳定输出说明

当前稳定成果默认导出到：

```text
outputs/latest_stable/
```

Stage 5C 起，该目录是当前精选成果目录，不再是历史阶段所有图件和报告的平铺总仓库。完整数组、快照帧、中间结果和历史阶段详细图件仍保存在时间戳运行目录中。

## 分层结构

```text
outputs/latest_stable/
├── README.md
├── summary.md
├── archive_manifest.md
├── figures/
│   ├── core/
│   ├── forward/
│   ├── localization/
│   ├── uncertainty/
│   └── diagnostics/
├── reports/
│   ├── core/
│   ├── forward/
│   ├── localization/
│   ├── uncertainty/
│   └── diagnostics/
└── metadata/
```

## 当前重点 forward 输出

- `figures/forward/fig_forward_engine_comparison.png`
- `figures/forward/fig_layered_kinematic_vs_baseline_gather.png`
- `figures/forward/fig_forward_roadmap_status.png`
- `figures/forward/fig_acoustic2d_wavefield_snapshots.png`
- `figures/forward/fig_acoustic2d_shot_gather.png`
- `figures/forward/fig_elastic2d_rayleigh_wavefield_snapshots.png`
- `figures/forward/fig_elastic2d_surface_gather.png`
- `figures/forward/fig_elastic2d_rayleigh_velocity_check.png`
- `figures/forward/fig_elastic2d_void_scattering_residual.png`
- `figures/forward/fig_elastic2d_void_diffraction_overlay.png`
- `figures/forward/fig_elastic2d_das_gauge_response.png`
- `figures/forward/fig_elastic_vs_kinematic_overlay.png`
- `reports/forward/report_forward_engine_ablation.md`
- `reports/forward/report_acoustic2d_prototype.md`
- `reports/forward/report_elastic2d_rayleigh_validation.md`
- `reports/forward/report_elastic2d_void_scattering.md`
- `reports/forward/report_elastic2d_das_response.md`
- `reports/forward/report_elastic_vs_kinematic.md`

这些输出用于判断 forward 技术路线是否清晰、layered kinematic 与 baseline 的差异、acoustic2d 基础设施是否可运行，以及 elastic2d_prototype 是否能作为 Rayleigh-like/free-surface/void-like scattering 的局部科研验证起点。它们不能作为工程确诊结论。
