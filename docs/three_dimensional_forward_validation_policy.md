# 三维场景 forward validation policy

## 基本立场

本项目最终场景是三维道路 DAS-like 空洞探测。主几何必须保持为 `source_xyz / receiver_xyz / candidate_xyz`，主定位必须保持为 `x-y-depth` 三维候选体、high-score region、connected components 和 uncertainty interval。

## 2D elastic 的角色

2D elastic 只服务局部物理验证，用于检查 Rayleigh-like surface event、free-surface、void-like scattering、DAS-like gauge strain 和运动学曲线解释力。它不是主场景退化，也不能直接替代三维 x-y-depth 定位。

## 不得直接替代的内容

任何 2D elastic 结果都不得直接替代：

- 三维 source-receiver-candidate 走时；
- 三维 score volume；
- 三维 high-score connected components；
- 三维 recommended_location / uncertainty interval；
- 单侧道路 DAS-like 几何下的 y-depth 不确定性判断。

## 进入 2.5D 的前置条件

只有同时满足以下条件，`ready_for_2p5d` 才允许为 True：

1. Rayleigh benchmark 至少一个 case 通过 sanity check；
2. DAS-like gauge response 有非零且可解释结果；
3. void residual 可见，且不是明显边界伪影；
4. latest_stable 图件、报告和 summary 结论一致；
5. latest_stable 无空图、重复图、旧阶段图和明显英文图；
6. 三维 x-y-depth 定位与不确定性表达仍保留。

## Stage 5F 结论

当前 `ready_for_2p5d=False`。Stage 5F 的 staggered-grid elastic2d benchmark 仍是 validation forward，不替代 `layered_kinematic` 主定位 forward。当前结果仍是科研候选区，不是工程确诊。
