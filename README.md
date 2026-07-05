# hcz_void_plus

三维道路 DAS-like 空洞探测科研原型。当前结果用于算法研发与候选区解释，不是工程确诊。

## 当前阶段

当前推进到 **Stage 5J：代码优先的三维运动学正演补强 + 衰减模型 + 炮集速度模型上下文 + 测试收缩**。

当前主依据：

- `README.md`
- `docs/current_status.md`
- `docs/current_algorithm_boundary.md`
- `docs/forward_modeling_roadmap.md`
- `docs/three_dimensional_forward_validation_policy.md`
- `code/current_3d_algorithm/`
- `outputs/latest_stable/summary.md`

历史文档如 `docs/archive/` 中的内容只作为阶段记录，不作为当前开发依据。

## 当前主线

- active velocity model：`layered`
- active forward engine：`layered_kinematic`
- current main localization forward：layered straight-ray kinematic approximation
- validation forward：`acoustic2d_prototype`、`elastic2d_prototype`、`staggered_elastic2d_benchmark`
- ready_for_2p5d：`False`，除非 Rayleigh benchmark、DAS gauge response、void residual 和 latest_stable 一致性全部通过

`layered_kinematic` 使用的是等效 Rayleigh 速度模型；`elastic2d` 使用 Vp/Vs/rho 弹性参数。二者属于不同物理层级，需要通过经验关系或实测标定桥接，不能混为同一个速度模型。

## 正演路线

- F0 `kinematic_baseline`：快速均匀速度运动学基线，不是真实波场。
- F1 `layered_kinematic`：当前主定位 forward，通过 velocity model travel-time 接口计算 direct / scatter / scan。
- F2 `acoustic2d_prototype`：声学波动方程基础设施验证，不能代表 Rayleigh 波。
- F3 `elastic2d_prototype`：Rayleigh/free-surface/void scattering 的局部科研验证起点。
- Stage 5J `kinematic_volume_response`：新增 x-y-depth 三维运动学体响应 proxy、速度模型约束炮集和经验 Q attenuation；`staggered_elastic2d_benchmark` 继续只作为 validation forward。
- F4-F6：2.5D、多剖面、局部 3D elastic 是长期方向；Rayleigh benchmark 未通过前不建议进入。

## 三维场景边界

项目最终场景始终是三维道路 DAS-like：

- source：`source_xyz`
- receiver：`receiver_xyz` 或 receiver polyline
- candidate：`candidate_xyz`
- output：x-y-depth high-score region、connected components、uncertainty interval

2D elastic 只服务于局部物理验证，不能直接替代三维 x-y-depth 定位。

## latest_stable 治理

`outputs/latest_stable/` 是当前精选成果目录，不是历史输出仓库。Stage 5J 后，进入该目录的图件必须服务三维算法主线：

- 文件级 figure self-check
- 空图/低质量图检查
- 重复图检查
- 图件中文化检查
- latest_stable 三类数量审计
- tree snapshot 与 manual review readiness 审计

当前精选结构：

- `figures/forward/` 与 `animations/forward/`：正演、速度模型、三维几何、Rayleigh benchmark、DAS-like response 和正演动图
- `figures/localization/` 与 `animations/localization/`：x-y-depth 定位、高分候选体、推荐位置和三维不确定性
- `figures/error_analysis/` 与 `animations/error_analysis/`：质量检查、误差分析、Rayleigh/DAS 限制和 ready_for_2p5d 判断
- `reports/forward/`、`reports/localization/`、`reports/error_analysis/`：对应精选报告，数量保持受控

空图、重复图、旧阶段主结论图和明显英文图不得进入 `latest_stable`。

## 运行

```bash
D:\HczApp\Anaconda\envs\mywork\python.exe -m pytest
D:\HczApp\Anaconda\envs\mywork\python.exe main.py --task full_pipeline --max-shot-gather-figures 2 --wavefield-snapshot-count 8
D:\HczApp\Anaconda\envs\mywork\python.exe code\current_3d_algorithm\run_current_3d.py
```

`main.py` 仍是唯一 argparse 参数入口。不创建 `config/` 或 `para/` 目录。

## 当前限制

- `layered_kinematic` 仍是 straight-ray kinematic approximation。
- `elastic2d` 仍是最小科研验证原型，不是工业级 elastic solver。
- Rayleigh-like benchmark 未通过时，不得宣称 Rayleigh 正演成功。
- DAS-like gauge strain 很弱或不可解释时，不得默认用于定位。
- 当前 DAS-like response 不是完整真实 DAS 仪器响应。
- 当前结果是科研候选区，不是工程确诊。

## 下一步

优先继续加固 elastic2d 自由表面、吸收边界、staggered-grid 数值格式和 DAS-like gauge response。只有在 Rayleigh benchmark、void residual、DAS gauge response 和 latest_stable 一致性全部通过后，才考虑 2.5D 多剖面验证。
