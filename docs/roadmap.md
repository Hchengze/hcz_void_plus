# Roadmap

## Stage 1

本地科研算法工程骨架与最小 DAS-like 运动学正演闭环。

## Stage 2

中文化输出与基础多炮扫描定位一体化增强：

- 中文图件和中文报告；
- 规范化输出目录和文件前缀；
- 运动学伪波场快照和 GIF；
- 直达波预测与基础 mute；
- x-y-h 多炮扫描；
- score volume 和基础定位图。

## Stage 3

基础置信度指标 + 稳定成果输出管理：

- peak sharpness、score contrast、multi-shot consistency；
- y-depth coupling warning 和 high/medium/low 规则型诊断；
- `fig_confidence_diagnostics.png` 与 `report_confidence.md`；
- `outputs/latest_stable/` 精选成果目录；
- 时间戳完整输出与 Git 精选输出分离。

## Stage 3B

三维场景约束下的扫描诊断修正与置信度稳健化：

- raw score 与 depth-weighted score 并列输出；
- raw_best、weighted_best 和二者差异进入报告与 summary；
- 新增深度边界、宽 y 高分区、raw/weighted 分歧和浅部偏置 warning；
- 直达波 mute 默认改为 taper；
- 新增 normalized_energy_stack；
- 新增三维几何路线文档。

## Stage 3C

深度稳健性对比、推荐位置规则与三维不确定性表达：

- 将 raw 语义整理为 unweighted / depth-weighted / active；
- 新增 recommended_location、recommended_location_type 和 recommended_reason；
- 轻量比较 diffraction_energy_stack 与 normalized_energy_stack；
- 输出三维高分区跨度、等效不确定性盒和不确定性切片；
- latest_stable 增加推荐位置、score_method 对比和 3D 高分区摘要。

## Stage 4A

Reference 审计接入 + 三维观测几何泛化 + 预处理与定位算法增强：

- 审计 `reference/`、`code/`、`tools_code/` 和 `literature_reproduction/`，明确哪些资料可吸收、需重写或仅作阅读参考；
- 接收点和震源点统一为三维 `receiver_xyz/source_xyz`，默认直线场景继续可跑，同时预留 CSV/polyline/grid；
- 异常体从中心点扩展到 sphere、ellipsoid、box、cylinder、pipe_trench 的等效散射点表达；
- 扫描前加入 bandpass、AGC、包络、道归一化和简化 f-k 滤波接口；
- 定位评分从单一 energy stack 扩展为 multi_attribute，包含 energy、normalized energy、matched wavelet 和 semblance；
- depth prior 默认不再决定主定位，只作为辅助诊断和敏感性分析；
- latest_stable 增加三维几何、异常体散射点、预处理对比、多属性评分和 depth prior 敏感性图。

## 后续阶段

- 更完整的概率置信度体系和不确定性表达；
- 鲁棒性参数扫描；
- DAS gauge length 真实响应；
- 分层速度模型；
- 局部 elastic2d / simplified elastic3d 全波场验证；
- 更系统的异常识别和多炮联合定位评价。

项目始终是科研级算法原型，不是工业级工程软件。当前结果不能作为工程确诊结论。

## Stage 5B

正演技术路线确立 + 正演主线重构 + 稳定算法入口硬化：

1. 建立 F0-F6 forward roadmap。
2. 将当前 active forward engine 明确为 `layered_kinematic`。
3. 保留 `kinematic_baseline` 作为 F0 快速基线。
4. 实现 `acoustic2d_prototype` 作为 F2 acoustic wave-equation infrastructure validation。
5. 完成 `elastic2d` 技术设计，作为下一步 Rayleigh/free-surface/void scattering 核心方向。
6. 在 `code/current_3d_algorithm/` 中沉淀 stable forward API。
7. latest_stable 新增 forward engine 对比、F0/F1 炮集差异、forward roadmap、acoustic2d 快照和报告。

## Stage 5C

forward 目录职责梳理 + latest_stable 精简治理 + elastic2d Rayleigh/free-surface 原型：

1. 用本地脚本核验关键 Python/Markdown 文件的 LF 换行、CR-only、行数和长行，避免只凭 GitHub raw 页面判断。
2. 梳理 `src/forward/` 新旧文件职责，明确 `forward_registry.py` 是 engine 统一入口。
3. 将 `outputs/latest_stable/` 治理为分层精选目录，不再平铺堆积历史阶段图件。
4. 实现最小 `elastic2d_prototype`：collocated-grid velocity-stress、`vx/vz/sxx/szz/sxz`、`Vp/Vs/rho/lambda/mu`、Ricker vertical force、近似 free surface、sponge boundary、surface gather 和 snapshots。
5. 新增 Rayleigh-like surface event、void-like low-Vs scattering、DAS-like gauge strain 与 elastic-vs-kinematic 对照验证。
6. 保持 `layered_kinematic` 作为当前主定位 forward，`elastic2d_prototype` 只作为 validation forward。

# Stage 5A 更新说明

本文件包含历史路线和当前路线。当前最新主线请以 `README.md`、`docs/current_status.md`、`docs/current_algorithm_boundary.md` 和 `code/current_3d_algorithm/` 为准。

Stage 5A 当前目标：

1. 将最新稳定三维算法沉淀到 `code/current_3d_algorithm/`。
2. 将默认速度模型从 `uniform` 升级为 `layered`。
3. 增加 `lateral_gradient`、`localized_low_velocity_zone` 和 `layered_with_anomaly_perturbation`。
4. 输出 velocity model ablation 与 model mismatch 诊断。
5. 继续坚持结果是科研候选区，不是工程确诊。
