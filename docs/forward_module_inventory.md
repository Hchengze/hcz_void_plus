# forward 模块职责清单

| file/module | current role | stage | used by current stable pipeline | legacy-compatible | risk if misused | recommended action |
|---|---|---|---|---|---|---|
| `src/forward/forward_registry.py` | forward engine 统一注册入口 | F0-F3 | yes | no | 绕过它会重新造成新旧入口混乱 | 所有 engine 选择都从这里走 |
| `src/forward/layered_kinematic.py` | 当前 active forward engine | F1 | yes | no | 被误写成真实全波场 | 保留为主定位 forward，并持续走 velocity_model travel time |
| `src/forward/kinematic_baseline.py` | 均匀速度运动学基线 | F0 | no | yes | 被误当作当前推荐主线 | 仅用于 baseline 和回归测试 |
| `src/forward/acoustic2d/` | acoustic wave-equation infrastructure validation | F2 | no | no | 被误称为 Rayleigh 正演 | 保留为 validation，不进入主定位 |
| `src/forward/elastic2d/` | elastic2d Rayleigh/free-surface/void scattering 最小验证原型 | F3 | no | no | 被误称为工业级 elastic 或替代三维主流程 | 保留为局部物理验证起点 |
| `src/forward/direct_wave.py` | 直达波运动学基础组件 | component | yes, via F1 | yes | 直接调用会绕过 engine 语义 | 保留并在 docstring 标明基础组件 |
| `src/forward/scatter_kinematic.py` | 等效散射运动学基础组件 | component | yes, via F1 | yes | 被误当作完整散射正演 | 保留并标明 equivalent scatter approximation |
| `src/forward/multishot_forward.py` | direct/scatter/DAS-like response 组合组件 | component | yes, via F1 | yes | 被误当作当前 active engine | 保留为 F0/F1 内部组件 |
| `src/forward/wavelet.py` | Ricker 子波工具 | utility | yes | no | 低风险 | 保留为通用工具 |
| `src/forward/adapters/` | 外部 solver adapter 计划 | F6 | no | no | 无许可证复制第三方代码 | 仅保留计划文档 |

当前稳定主线：`layered_kinematic`。  
当前 validation forward：`acoustic2d_prototype`、`elastic2d_prototype`。  
当前结果仍是科研候选区，不是工程确诊。
