# 当前算法边界

## 必须坚持的边界

1. 当前是 `DAS-like response approximation`。
2. 当前是 `kinematic approximation`。
3. 当前分层/非均匀速度模型是 `straight-ray kinematic approximation`。
4. 当前不是 3D elastic wavefield。
5. 当前不是真实 DAS 仪器响应。
6. 当前异常体是 `equivalent scatter representation`，不是真实边界散射。
7. 当前三维几何是 `source_xyz / receiver_xyz / candidate_xyz` 运动学几何。
8. 当前结果是科研候选区，不是工程确诊。
9. 当前 `acoustic2d_prototype` 是 acoustic wave-equation infrastructure validation，不是 Rayleigh 波正演。
10. `elastic2d_prototype` 是 Rayleigh/free-surface/void scattering 的局部物理验证起点，但不是工业级 elastic solver。

## 速度模型边界

Stage 5A 支持 `uniform / layered / lateral_gradient / localized_low_velocity_zone / layered_with_anomaly_perturbation`。

这些模型只改变运动学走时积分：

```text
travel_time = integral(ds / v(x, y, z))
```

路径仍是直线段，不做 Snell 射线弯曲，不做弹性波传播，不做速度反演。

## 结果解释边界

单侧线状 DAS-like 几何下，y 和 depth 的可分辨性天然有限。推荐结果应优先表达为：

- 三维高分候选区；
- y/depth 不确定性区间；
- high-score connected components；
- velocity model ablation；
- model mismatch 风险。

不能把 `best_location` 写成工程确诊点。

## 正演路线边界

- F0 `kinematic_baseline` 只保留为快速基线。
- F1 `layered_kinematic` 是当前 active forward engine。
- F2 `acoustic2d_prototype` 只能验证声学数值框架，不能解释为 Rayleigh 或空洞弹性散射。
- F3 `elastic2d_prototype` 是当前最小 velocity-stress 局部验证原型。
- F5 full/local 3D elastic 是长期小域验证目标，不是当前默认主流程。

## latest_stable 边界

Stage 5C 起，`outputs/latest_stable/` 是当前精选成果目录，不再是历史阶段所有图件和报告的平铺总仓库。完整历史输出应从时间戳运行目录追溯，当前主结论应优先查看分层后的 `figures/core`、`figures/forward`、`reports/core` 和 `reports/forward`。

Stage 5D 起，精选图件必须先经过 figure self-check：文件存在、可读取、非空白、分辨率达标、分类正确，并在 manifest 中记录 `stage / forward_engine / velocity_model_type`。未通过自检的图件只留在时间戳运行目录，不进入 `latest_stable`。

## Stage 5D 速度模型边界

Stage 5D 会输出 `report_velocity_model_audit.md` 和当前速度模型图件，核验 `layered` 等效 Rayleigh 速度是否真正进入 direct wave、scatter wave 和 scan candidate travel-time。即便核验通过，它仍然只是 `straight-ray kinematic approximation`，不是完整 Vp/Vs/rho 弹性模型；`elastic2d_prototype` 使用的 Vp/Vs/rho 与主定位的 Rayleigh equivalent velocity 属于不同物理层级。

## Stage 5E 边界

Stage 5E 增加 scientific figure self-check、elastic2d numerical sensitivity 和 velocity physics bridge。它们用于防止科学结论与图件不一致，并澄清 Rayleigh equivalent velocity 与 Vp/Vs/rho 的关系。

- Rayleigh-like 检测未通过时，不得宣称 Rayleigh 正演成功。
- DAS-like gauge strain 为零或很弱时，不得宣称 DAS 响应有效，也不得默认纳入定位。
- staggered-grid 当前只提供布局和 CFL 检查，不是成熟求解器。
- 未通过 Rayleigh/free-surface 基础验证前，不建议进入 2.5D 或局部 3D elastic。

## Stage 5F 边界

Stage 5F 增加 latest_stable 图件质量治理、旧文档清理、staggered-grid elastic2d benchmark 和三维 forward validation policy。

- `layered_kinematic` 仍是主定位 forward。
- `elastic2d_staggered_benchmark` 只是 validation benchmark，不替代主定位数据。
- 空图、重复图、旧阶段图和明显英文图不得进入 latest_stable 当前精选。
- Rayleigh-like benchmark 未通过时，不得把 elastic2d 写成 Rayleigh 正演成功。
- DAS-like gauge strain 即使非零，也不得默认用于定位，除非经过真实 DAS gauge、方向和仪器响应校准。
- 2D elastic 只服务三维道路 DAS-like 场景的局部物理验证，任何 2D 结果不得直接替代三维 x-y-h 定位。
- `ready_for_2p5d` 只有在 Rayleigh benchmark、DAS gauge response、void residual 和 latest_stable 一致性同时满足后才可为 True。
