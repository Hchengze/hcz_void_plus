# hcz_void_plus

城市道路既有通信光纤 DAS-like 三维空洞探测科研级算法原型平台。

本项目面向城市道路浅层空洞、脱空、松散区、管沟、管线周边扰动、弱夹层和破碎带等异常体。当前系统不是可安装发布软件，也不是工程确诊系统，而是本地可运行、可调试、可持续扩展的科研算法工程。

## 当前最新阶段

当前主线推进到 **Stage 5D：elastic2d 加固 + 速度模型主线核验 + 结果图自检机制**。

Stage 5A 前的结论中，部分 Stage 2/Stage 3/Stage 4 表述只代表历史阶段。当前主线请优先阅读：

- `README.md`
- `docs/current_status.md`
- `docs/current_algorithm_boundary.md`
- `code/current_3d_algorithm/`
- `outputs/latest_stable/summary.md`

## code/ 与 src/ 的区别

- `code/current_3d_algorithm/`：当前最新稳定算法成果区。这里沉淀最值得保留的三维算法主线、稳定 API 和推荐流程。
- `src/`：研发区。这里包含正演、预处理、定位、置信度、消融实验和后续探索模块，不代表所有内容都是当前推荐算法。

`code/current_3d_algorithm/` 不复制第三方无许可证代码，也不维护第二套参数。它通过稳定 API 调用 `src/` 中经过测试的实现。

## 当前稳定算法主线

1. 三维几何：`source_xyz / receiver_xyz / candidate_xyz`。
2. DAS-like 点式接收近似：当前仍不是完整 DAS 仪器响应。
3. 当前主正演：`layered_kinematic`，使用分层/非均匀速度模型的 straight-ray 运动学走时积分。
4. 异常体：`sphere / ellipsoid / box / cylinder / pipe_trench` 的等效散射点表达。
5. 推荐预处理：`bandpass + trace_normalization + taper direct mute`。
6. 主定位：`multi_attribute_unweighted`，不让 depth weighting 默认主导定位。
7. 不确定性表达：`3D high-score region`、连通域、推荐位置类型和 depth/y 区间。
8. 稳定输出：`outputs/latest_stable/` 存放每轮最值得人工检查的精选图件、报告和 metadata。

## 正演技术路线

Stage 5B 起，forward modeling 单独立为主线；Stage 5C 新增最小 `elastic2d_prototype` validation；Stage 5D 在此基础上加固 Rayleigh-like 拾取、void residual、DAS-like gauge response，并核验 active velocity model 是否真正进入 direct / scatter / scan 调用链：

- F0 `kinematic_baseline`：均匀速度运动学快速基线，保留用于对比和回归测试。
- F1 `layered_kinematic`：当前 active forward engine，支持 layered / heterogeneous straight-ray kinematic travel time。
- F2 `acoustic2d_prototype`：二维标量 acoustic FDTD validation，用于验证网格、震源、接收、边界、CFL 和快照输出，不能代表 Rayleigh 波。
- F3 `elastic2d_prototype`：最小 2D velocity-stress validation，用于 Rayleigh-like surface event、free-surface 和 void-like scattering 局部科研检查。
- F4-F6：多剖面 elastic、小域 3D elastic 和外部 solver adapters。

## 速度模型升级

Stage 5A 起，默认速度模型从 `uniform` 升级为 `layered`：

```bash
--velocity-model-type layered
```

当前支持：

- `uniform`：均匀等效 Rayleigh 速度，用作基线对比；
- `layered`：路面结构层、基层和土体层的分层等效 Rayleigh 速度；
- `lateral_gradient`：沿 x/y 的横向速度渐变；
- `localized_low_velocity_zone`：局部低速区；
- `layered_with_anomaly_perturbation`：分层背景叠加异常附近低速扰动。

这些模型通过直线路径采样积分计算走时，即 `straight-ray kinematic approximation`。它们比单一均匀速度更接近近地表情形，但仍不是 3D elastic wavefield、不是射线弯曲模拟，也不是速度反演。

## 如何运行

```bash
D:\HczApp\Anaconda\envs\mywork\python.exe -m pytest
D:\HczApp\Anaconda\envs\mywork\python.exe main.py --task full_pipeline --max-shot-gather-figures 2 --wavefield-snapshot-count 8
```

也可以运行当前稳定算法入口：

```bash
python code/current_3d_algorithm/run_current_3d.py
```

所有参数仍由根目录 `main.py` 的 argparse 管理，不创建 `config/` 或 `para/`。

## 输出在哪里

完整运行结果：

```text
outputs/<run_name>_<timestamp>/
```

精选稳定结果：

```text
outputs/latest_stable/
```

Stage 5D 后，`outputs/latest_stable/` 是分层精选目录，而不是历史图件总仓库。进入 latest_stable 的图件会先经过文件大小、可读性、非空白、分辨率、类别和 stage/forward/velocity metadata 自检。重点新增图件和报告包括：

- `fig_velocity_model_comparison.png`
- `fig_layered_velocity_profile.png`
- `fig_velocity_model_travel_time_residuals.png`
- `fig_model_mismatch_error_summary.png`
- `report_velocity_model_ablation.md`
- `report_model_mismatch.md`
- `fig_forward_engine_comparison.png`
- `fig_layered_kinematic_vs_baseline_gather.png`
- `fig_forward_roadmap_status.png`
- `fig_acoustic2d_wavefield_snapshots.png`
- `fig_acoustic2d_shot_gather.png`
- `fig_elastic2d_rayleigh_wavefield_snapshots.png`
- `fig_elastic2d_surface_gather.png`
- `fig_elastic2d_rayleigh_velocity_check.png`
- `fig_elastic2d_void_scattering_residual.png`
- `fig_elastic2d_void_diffraction_overlay.png`
- `fig_elastic2d_das_gauge_response.png`
- `fig_elastic_vs_kinematic_overlay.png`
- `fig_velocity_model_profile_current.png`
- `fig_velocity_model_2d_slice_current.png`
- `fig_velocity_sampling_paths_current.png`
- `fig_uniform_vs_layered_travel_time_difference.png`
- `fig_velocity_model_active_badge.png`
- `fig_elastic2d_rayleigh_pick_diagnostics.png`
- `fig_elastic2d_void_parameter_sensitivity.png`
- `fig_elastic2d_void_residual_energy_map.png`
- `fig_elastic2d_das_component_comparison.png`
- `fig_elastic2d_das_gauge_length_sensitivity.png`
- `fig_elastic_vs_kinematic_energy_partition.png`
- `report_forward_engine_ablation.md`
- `report_acoustic2d_prototype.md`
- `report_repository_health.md`
- `report_figure_self_check.md`
- `report_velocity_model_audit.md`
- `report_velocity_model_visualization.md`
- `report_elastic2d_rayleigh_validation.md`
- `report_elastic2d_void_scattering.md`
- `report_elastic2d_das_response.md`
- `report_elastic_vs_kinematic.md`

## 当前最可信的结果表达

当前结果应表达为三维候选体和不确定性区间，而不是工程确诊点。对于单侧或准单侧 DAS-like 观测几何，y-depth 耦合仍是核心风险。即使 x 方向聚焦较稳定，y 和 depth 也必须结合高分区跨度、连通域、模型错配和速度模型消融共同解释。

## 当前仍然存在的问题

- 当前是 `DAS-like response approximation`。
- 当前是 `kinematic approximation`。
- 分层/非均匀速度是 `straight-ray kinematic approximation`。
- 当前不是完整 DAS 仪器响应。
- 当前不是 3D elastic wavefield。
- 当前 `acoustic2d_prototype` 不是 Rayleigh 波正演，只是 acoustic wave-equation infrastructure validation。
- `elastic2d_prototype` 是 Rayleigh/free-surface/void scattering 的局部物理验证起点，但仍不是工业级模拟。
- 当前异常体是 `equivalent scatter representation`，不是真实边界散射。
- 当前结果是科研候选区，不是工程确诊。
- 真实道路三维场景中，速度模型不确定性、观测几何和 y-depth 耦合仍是核心风险。

## 下一步方向

1. 用更多三维观测几何实验优化 source 方位覆盖。
2. 继续增强 layered / heterogeneous velocity 的可解释性和参数敏感性。
3. 加固 `elastic2d_prototype` 的数值稳定性、自由表面处理和 void scattering 验证，但仍与主流程的运动学算法保持边界清晰。
4. 在真实或半真实数据上验证预处理、multi-attribute score 和模型错配诊断是否稳定。
