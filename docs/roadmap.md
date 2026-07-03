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

## 后续阶段

- 更完整的概率置信度体系和不确定性表达；
- 鲁棒性参数扫描；
- DAS gauge length 真实响应；
- 分层速度模型；
- 局部 elastic2d / simplified elastic3d 全波场验证；
- 更系统的异常识别和多炮联合定位评价。

项目始终是科研级算法原型，不是工业级工程软件。当前结果不能作为工程确诊结论。
