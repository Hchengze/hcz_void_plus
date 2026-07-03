# Roadmap

## Stage 1

本地科研算法工程骨架与最小 DAS-like 运动学正演闭环。

## Stage 2

中文化输出与基础多炮扫描定位一体化增强：

- 中文图件和中文报告；
- 规范化输出目录和文件前缀；
- 运动学伪波场快照和 GIF；
- 直达波预测与基础 mute；
- x-y-h 多炮扫描；
- score volume 和基础定位图。

## Stage 3

基础置信度指标 + 稳定成果输出管理：

- peak sharpness、score contrast、multi-shot consistency；
- y-depth coupling warning 和 high/medium/low 规则型诊断；
- `fig_confidence_diagnostics.png` 与 `report_confidence.md`；
- `outputs/latest_stable/` 精选成果目录；
- 时间戳完整输出与 Git 精选输出分离。

## Stage 3B

三维场景约束下的扫描诊断修正与置信度稳健化：

- raw score 与 depth-weighted score 并列输出；
- raw_best、weighted_best 和二者差异进入报告与 summary；
- 新增深度边界、宽 y 高分区、raw/weighted 分歧和浅部偏置 warning；
- 直达波 mute 默认改为 taper；
- 新增 normalized_energy_stack；
- 新增三维几何路线文档。

## Stage 3C

深度稳健性对比、推荐位置规则与三维不确定性表达：

- 将 raw 语义整理为 unweighted / depth-weighted / active；
- 新增 recommended_location、recommended_location_type 和 recommended_reason；
- 轻量比较 diffraction_energy_stack 与 normalized_energy_stack；
- 输出三维高分区跨度、等效不确定性盒和不确定性切片；
- latest_stable 增加推荐位置、score_method 对比和 3D 高分区摘要。

## 后续阶段

- 更完整的概率置信度体系和不确定性表达；
- 鲁棒性参数扫描；
- DAS gauge length 真实响应；
- 分层速度模型；
- 局部 elastic2d / simplified elastic3d 全波场验证；
- 更系统的异常识别和多炮联合定位评价。

项目始终是科研级算法原型，不是工业级工程软件。当前结果不能作为工程确诊结论。
