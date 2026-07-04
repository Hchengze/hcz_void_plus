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
