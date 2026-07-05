# latest_stable

Stage 5H 继续执行三类精选治理：本目录只保留当前人工复查最需要、且 metadata 可审计的成果。

## 三类结果

- `forward/`：正演、速度模型、三维几何、Rayleigh benchmark、DAS-like response 与正演动图。
- `localization/`：x-y-depth 定位、高分候选体、推荐位置和三维不确定性。
- `error_analysis/`：质量检查、误差分析、Rayleigh/DAS 限制和 ready_for_2p5d 判断。

当前结果是科研候选区，不是工程确诊。2D elastic 只服务三维道路 DAS-like 场景的局部物理验证；三维图件表达几何与定位，不代表 elastic2d 已是三维弹性正演。