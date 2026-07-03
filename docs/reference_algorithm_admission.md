# Reference Algorithm Admission

## 可以进入 `src` 的算法

进入 `src` 的算法必须满足：

- 用本项目代码风格重写；
- 输入输出 shape、单位、物理意义、适用范围和限制清楚；
- 不依赖来源不明的大段第三方代码；
- 明确仍是 `kinematic approximation` 和 `DAS-like response approximation`。

本轮已进入 `src` 的参考支撑算法：

- FFT bandpass；
- sliding RMS AGC；
- Hilbert envelope；
- trace normalization；
- 简化 f-k velocity sector filter；
- multi-attribute localization scoring；
- depth prior sensitivity。

## 只能放在 `literature_reproduction` 的内容

- 对论文图件、算例或公开算法的逐步复现实验；
- 需要保留原文公式编号、图件设置、实验参数的材料；
- 尚未充分适配本项目主流程的探索脚本。

## 只能作为阅读参考的内容

- PDF 原文；
- 许可证未审计的大型第三方工程；
- 完整 elastic/FWI/FEM/SEM/BEM 代码；
- 工业级或商用工具链输出。

## 禁止

不允许把来源不清的代码直接混入主流程；不允许把第三方工程复制进 `src`；不允许把当前 kinematic prototype 宣称为完整 DAS 仪器模拟或完整 3D elastic wavefield。

