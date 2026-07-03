# 正演技术路线图

本文件是 Stage 5B 的正演主线约束。项目面向城市道路既有通信光纤 DAS-like 三维空洞探测，但当前主流程仍是科研原型，不是工程确诊系统。所有阶段都必须明确物理假设、输入输出和不能宣称的内容。

## F0：kinematic baseline forward

- 当前能力：source-scatter-receiver 走时、直达事件、等效散射事件和 Ricker 子波叠加。
- 实现位置：`src/forward/kinematic_baseline.py`、兼容入口 `src/forward/scatter_kinematic.py`。
- 物理目的：提供最快速的回归测试和均匀速度基线。
- 边界：不能称为真实正演，不能代表真实 DAS 仪器响应，也不能代表 Rayleigh 波全波场。
- 稳定区状态：只作为 baseline 进入 `code/current_3d_algorithm/` 的 roadmap，不作为默认主正演。

## F1：layered / heterogeneous straight-ray kinematic forward

- 当前能力：沿三维直线路径采样积分 `integral ds / v(x,y,z)`，支持 `layered`、`lateral_gradient`、`localized_low_velocity_zone` 和 `layered_with_anomaly_perturbation`。
- 实现位置：`src/forward/layered_kinematic.py`、`src/model/velocity_model.py`、`src/model/layered_velocity.py`、`src/model/heterogeneous_velocity.py`。
- 物理目的：把正演和扫描从单一均匀等效 Rayleigh 速度推进到分层/横向非均匀近地表运动学模型。
- 边界：仍然不做 Snell 射线弯曲，不做模式转换，不做弹性波全波场。
- 稳定区状态：当前主流程默认正演引擎，`stable_forward_engine = layered_kinematic`。

## F2：2D acoustic FDTD prototype

- 当前能力：二维标量 acoustic wave equation、常密度、二阶时间推进、Ricker 震源、接收线、sponge absorbing boundary、CFL 检查、炮集和快照输出。
- 实现位置：`src/forward/acoustic2d/`。
- 物理目的：建立波动方程框架、网格、震源、接收、边界和数值稳定性检查的最小闭环。
- 边界：acoustic 方程没有剪切波、自由表面 Rayleigh 模式和弹性空洞散射机制，因此不能写成 Rayleigh 波正演。
- 稳定区状态：只作为 validation forward，不作为默认定位数据。

## F3：2D elastic velocity-stress FDTD prototype

- 目标能力：二维 velocity-stress elastic wave equation、`Vp / Vs / rho`、自由表面、PML 或 sponge 边界、vertical force 震源、surface displacement/velocity 接收和 DAS-like gauge-length strain。
- 设计位置：`docs/elastic2d_forward_design.md`、`src/forward/elastic2d/README.md`。
- 物理目的：进入 Rayleigh/free-surface/void scattering 的核心局部全波场验证。
- 边界：下一阶段也应先做小域科研验证，不应直接宣称工业级 2D/3D 弹性模拟。
- 稳定区状态：planned physics forward。

## F4：2.5D / multi-section elastic validation

- 目标能力：围绕三维 source-receiver-anomaly 几何，抽取多个二维剖面做局部 elastic validation。
- 物理目的：服务三维道路场景，而不是把三维问题退化成单一 x-depth 剖面。
- 边界：多剖面验证只能检查局部物理一致性，不能替代完整三维全波场。

## F5：local small-domain 3D elastic validation

- 目标能力：只在小域、少数震源和 receiver 上做局部 3D elastic validation。
- 物理目的：验证三维绕射、空洞散射、DAS-like gauge response 和复杂观测几何的关键风险。
- 边界：不是大规模工业 3D elastic，不进入默认主流程。

## F6：external solver adapters

- 目标能力：为 Devito、Deepwave、SPECFEM、k-Wave 等外部求解器预留 adapter。
- 实现位置：`src/forward/adapters/` 中的计划文档。
- 物理目的：未来可复用成熟求解器思想和接口组织方式。
- 边界：不复制第三方无许可证代码，不把外部求解器混入主流程，不把 acoustic solver 误称为 Rayleigh solver。

## 当前结论

Stage 5B 的 active forward engine 是 `layered_kinematic`。`kinematic_baseline` 只保留为 F0 快速基线；`acoustic2d_prototype` 是 F2 波动方程基础设施验证；`elastic2d` 是下一步 Rayleigh/free-surface/void scattering 的核心方向。当前结果仍应表达为科研候选区和三维不确定性体，不是工程确诊。
