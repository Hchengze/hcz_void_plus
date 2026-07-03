# hcz_void_plus

城市道路既有通信光纤 DAS-like 三维空洞探测科研级算法原型平台。

本项目面向城市道路浅层空洞、脱空、松散区、管沟、管线周边扰动、弱夹层和破碎带等异常体。当前系统不是可安装发布软件，也不是工程确诊系统，而是本地可运行、可调试、可持续扩展的科研算法工程。

## 当前最新阶段

当前主线推进到 **Stage 5A：项目收口清理 + 稳定算法成果沉淀到 code + 分层/非均匀介质正演与定位升级**。

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
3. 运动学正演：直达 Rayleigh-like 事件 + equivalent scatter response。
4. 异常体：`sphere / ellipsoid / box / cylinder / pipe_trench` 的等效散射点表达。
5. 推荐预处理：`bandpass + trace_normalization + taper direct mute`。
6. 主定位：`multi_attribute_unweighted`，不让 depth weighting 默认主导定位。
7. 不确定性表达：`3D high-score region`、连通域、推荐位置类型和 depth/y 区间。
8. 稳定输出：`outputs/latest_stable/` 存放每轮最值得人工检查的精选图件、报告和 metadata。

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

Stage 5A 重点新增图件和报告：

- `fig_velocity_model_comparison.png`
- `fig_layered_velocity_profile.png`
- `fig_velocity_model_travel_time_residuals.png`
- `fig_model_mismatch_error_summary.png`
- `report_velocity_model_ablation.md`
- `report_model_mismatch.md`

## 当前最可信的结果表达

当前结果应表达为三维候选体和不确定性区间，而不是工程确诊点。对于单侧或准单侧 DAS-like 观测几何，y-depth 耦合仍是核心风险。即使 x 方向聚焦较稳定，y 和 depth 也必须结合高分区跨度、连通域、模型错配和速度模型消融共同解释。

## 当前仍然存在的问题

- 当前是 `DAS-like response approximation`。
- 当前是 `kinematic approximation`。
- 分层/非均匀速度是 `straight-ray kinematic approximation`。
- 当前不是完整 DAS 仪器响应。
- 当前不是 3D elastic wavefield。
- 当前异常体是 `equivalent scatter representation`，不是真实边界散射。
- 当前结果是科研候选区，不是工程确诊。
- 真实道路三维场景中，速度模型不确定性、观测几何和 y-depth 耦合仍是核心风险。

## 下一步方向

1. 用更多三维观测几何实验优化 source 方位覆盖。
2. 继续增强 layered / heterogeneous velocity 的可解释性和参数敏感性。
3. 引入局部全波场小模型验证，但仍与主流程的运动学算法保持边界清晰。
4. 在真实或半真实数据上验证预处理、multi-attribute score 和模型错配诊断是否稳定。
