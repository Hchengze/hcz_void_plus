# current_3d_algorithm 稳定算法成果区

本目录沉淀 hcz_void_plus 当前最新、最稳定、最值得保留的三维 DAS-like 空洞探测算法主线。

- `code/current_3d_algorithm/`：稳定成果区，面向复用、人工审计和阶段交付。
- `src/`：研发区，保留实验性模块、消融实验和后续算法探索。

当前主线仍是 `DAS-like response approximation` 与 `kinematic approximation`，不是完整 DAS 仪器模拟，也不是 3D elastic wavefield。

## 当前稳定算法线

1. 使用三维 `source_xyz / receiver_xyz / candidate_xyz` 几何。
2. 异常体使用 `equivalent scatter representation`，不是边界散射。
3. 推荐预处理组合：`bandpass + trace_normalization + taper direct mute`。
4. 主定位使用 `multi_attribute_unweighted`，depth weighting 只作为辅助诊断。
5. 输出 `3D high-score region`、不确定性区间和连通域诊断，不强行给工程确诊点。
6. Stage 5A 默认速度模型升级为 `layered`，并可切换 `uniform` 做基线对比。

## 运行

```bash
python code/current_3d_algorithm/run_current_3d.py
```

该入口仍调用根目录 `main.py` 的参数体系，不维护第二套参数。
