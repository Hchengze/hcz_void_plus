# 正演参考矩阵

本矩阵只说明可借鉴的思想和本项目实现位置，不复制第三方代码。

| reference | 可借鉴点 | 本项目阶段 | 本项目实现位置 | 是否已实现 | 是否进入 code/current_3d_algorithm | 当前限制 |
|---|---|---|---|---|---|---|
| Devito | symbolic finite-difference、PDE propagator、模型/网格/算子分层组织 | F2-F6 | `src/forward/acoustic2d/`、`src/forward/adapters/devito_adapter_plan.md` | 仅实现本项目自写 acoustic2d prototype | 否，仅进入 roadmap | 未接入 Devito，未复制代码 |
| Deepwave | differentiable propagation、forward modeling 与 imaging/inversion workflow | F2-F6 | `src/forward/adapters/deepwave_adapter_plan.md` | 未实现 adapter | 否，仅进入 roadmap | 当前不做 FWI，也不把 PyTorch 波传播混入主流程 |
| SPECFEM | 谱元法 seismic wave propagation、局部 3D elastic validation 思路 | F5-F6 | `src/forward/adapters/specfem_adapter_plan.md` | 未实现 adapter | 否，仅进入 roadmap | 仅作为长期局部验证参考 |
| k-Wave | acoustic wave simulation 的网格、介质、吸收和快照组织 | F2 | `src/forward/acoustic2d/` | 已实现最小自写 acoustic2d prototype | 作为 validation forward 进入 stable API | acoustic 不能代表 Rayleigh/free-surface/void scattering |
| Xia 等 Rayleigh-wave diffraction 文献 | Rayleigh diffraction、FK filtering、layered half-space void diffraction 的物理问题意识 | F0-F4 | `src/preprocessing/fk_filter.py`、`src/localization/attribute_scoring.py`、`docs/elastic2d_forward_design.md` | 部分进入预处理和属性评分，elastic2d 仍为设计 | 是，作为算法边界和后续路线 | 当前还没有真实 elastic Rayleigh 正演 |
| Madagascar | 可复现实验组织、数据流和图件报告组织方式 | F0-F6 | `outputs/latest_stable/`、`src/validation/` | 已用于项目输出组织思想 | 是，作为稳定输出机制 | 未复制 Madagascar 代码 |

## 吸收原则

1. 参考项目只提供结构和物理思路，不无许可证复制实现。
2. 引入任何外部 solver 前必须写明物理假设、输入输出、适用范围和限制。
3. 进入 `code/current_3d_algorithm/` 的只能是当前稳定主线或明确的 roadmap，不包含未经验证的大型第三方代码。
4. 当前真正进入主流程的是 F1 `layered_kinematic`；F2 `acoustic2d_prototype` 只做 validation；F3 `elastic2d_prototype` 已是最小科研验证原型，下一步是精度和稳定性硬化。
