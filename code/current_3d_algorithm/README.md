# current_3d_algorithm 稳定算法成果区

本目录沉淀 hcz_void_plus 当前最新、最稳定、最值得保留的三维 DAS-like 空洞探测算法主线。

- `code/current_3d_algorithm/`：稳定成果区，面向复用、人工审计和阶段交付。
- `src/`：研发区，保留实验性模块、消融实验和后续算法探索。

当前主线仍是 `DAS-like response approximation` 与 `kinematic approximation`，不是完整 DAS 仪器模拟，也不是 3D elastic wavefield。Stage 5K 后，稳定正演入口仍明确为 `layered_kinematic`，forward 与 localization 优先共用 `observation_kernel_3d`；x-y-depth 三维运动学体响应 proxy 只作为可视化，`elastic2d_prototype` 与 staggered-grid benchmark 只作为 validation forward。

## 当前稳定算法线

1. 使用三维 `source_xyz / receiver_xyz / candidate_xyz` 几何。
2. 异常体使用 `equivalent scatter representation`，不是边界散射。
3. 推荐预处理组合：`bandpass + trace_normalization + taper direct mute`。
4. 主定位使用 `multi_attribute_unweighted`，depth weighting 只作为辅助诊断。
5. 输出 `3D high-score region`、不确定性区间和连通域诊断，不强行给工程确诊点。
6. Stage 5A 默认速度模型升级为 `layered`，并可切换 `uniform` 做基线对比。
7. Stage 5B/5C 当前稳定正演主线为 `layered_kinematic`，`kinematic_baseline` 只作 F0 基线。
8. `acoustic2d_prototype` 只作为 F2 validation forward，不作为 Rayleigh 波正演或默认定位数据。
9. `elastic2d_prototype` 是 F3 validation forward，用于 Rayleigh-like/free-surface/void-like scattering 局部科研检查。
10. Stage 5D 新增 velocity model audit、figure self-check、repository health report 和 elastic2d 参数敏感性诊断。
11. Stage 5E 新增 scientific figure self-check、elastic2d numerical sensitivity、velocity physics bridge 和 DAS gauge nonzero check。
12. Rayleigh-like 检测未通过、DAS gauge 很弱时，不得把 elastic2d 或 DAS-like strain 写成成功主线。
13. Stage 5F 新增 figure quality/dedup/language check、staggered-grid Rayleigh benchmark 和三维 forward validation policy。
14. Stage 5G 新增三类 latest_stable、图件中文化、正演动图和三维可视化增强。
15. Stage 5H 加固 metadata、tree snapshot、manual review readiness、三维图件可读性和 Rayleigh/DAS 解释。
16. Stage 5I 修复 scan 速度模型一致性，输出三维多属性体、posterior-like 体和三维不确定性诊断。
17. Stage 5J 新增 x-y-depth 运动学体响应 proxy、带速度模型上下文的炮集图和经验 Q attenuation，并收缩旧图件测试。
18. Stage 5K 新增统一三维 observation kernel 和 receiver-consistent imaging volume，修复 forward/localization 各自维护路径表的问题。
19. Rayleigh benchmark 未通过前，`ready_for_2p5d=False`。

## 正演路线

- F0：`kinematic_baseline`，快速均匀速度运动学基线。
- F1：`layered_kinematic`，当前主定位 forward。
- F2：`acoustic2d_prototype`，声学波动方程基础设施验证。
- F3：`elastic2d_prototype`，最小 velocity-stress 局部物理验证原型。
- F4-F6：多剖面 elastic、小域 3D elastic 和外部 solver adapters。

## 运行

```bash
python code/current_3d_algorithm/run_current_3d.py
```

该入口仍调用根目录 `main.py` 的参数体系，不维护第二套参数。
