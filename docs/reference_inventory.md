# Reference Inventory

本页记录本地 `reference/`、`code/`、`tools_code/`、`literature_reproduction/` 的资产状态。由于远程仓库只公开 `.gitkeep`，本轮不把大型 PDF 或无许可证审计结论不充分的第三方工程直接提交，而是把可吸收算法以本项目风格重写进 `src`。

| 文件或资料 | 来源 | 类型 | 主题 | 可直接使用 | 是否需要重写 | 是否已吸收 | 吸收位置 |
|---|---|---|---|---|---|---|---|
| `reference/reference235.pdf` | 本地 reference | 论文/PDF | Rayleigh/DAS/浅层探测待审计 | 否，PDF 体量与版权不纳入 Git | 是 | 部分思想 | `docs/reference_backed_algorithm_plan.md` |
| `reference/reference236.pdf` | 本地 reference | 论文/PDF | 面波处理/绕射待审计 | 否 | 是 | 部分思想 | `src/preprocessing/*` |
| `reference/reference238.pdf` | 本地 reference | 论文/PDF | 定位/成像待审计 | 否 | 是 | 部分思想 | `src/localization/*` |
| `reference/reference239.pdf` | 本地 reference | 论文/PDF | DAS 或道路病害待审计 | 否 | 是 | 阅读参考 | docs |
| `reference/reference241.pdf` | 本地 reference | 论文/PDF | FK filtering / diffraction 待审计 | 否 | 是 | 接口吸收 | `src/preprocessing/fk_filter.py` |
| `reference/reference242.pdf` | 本地 reference | 论文/PDF | Rayleigh wave 待审计 | 否 | 是 | 深度敏感性思想 | `src/physics/rayleigh.py` |
| `reference/reference247.pdf` | 本地 reference | 论文/PDF | 定位/反演待审计 | 否 | 是 | 阅读参考 | docs |
| `reference/reference248.pdf` | 本地 reference | 论文/PDF | 工程检测待审计 | 否 | 是 | 阅读参考 | docs |
| `reference/reference249.pdf` | 本地 reference | 论文/PDF | DAS/面波处理待审计 | 否 | 是 | 阅读参考 | docs |
| `code/.gitkeep` | 本地 code | 占位 | 无旧代码公开资产 | 不适用 | 不适用 | 不适用 | 无 |
| `tools_code/DENISE-Black-Edition-master/` | 本地 tools_code | 第三方工程 | elastic/FWI/full waveform | 否，体量大且许可需单独审计 | 是，仅可借鉴概念 | 未进入主流程 | 不纳入 Git |
| `tools_code/devito-main/` | 本地 tools_code | 第三方工程 | PDE/全波场模拟 | 否，体量大且不属于本阶段 | 是，仅可借鉴概念 | 未进入主流程 | 不纳入 Git |
| `tools_code/SAVA-master/` | 本地 tools_code | 第三方工程 | 地震处理/速度分析待审计 | 否，许可需单独审计 | 是，仅可借鉴概念 | 未进入主流程 | 不纳入 Git |
| `literature_reproduction/.gitkeep` | 本地 literature_reproduction | 占位 | 尚无复现实验 | 不适用 | 不适用 | 待后续 | 无 |

## 本轮吸收说明

- Rayleigh-wave diffraction 文献强调直达面波压制、FK filtering、局部绕射事件增强，本轮以自写方式加入 `src/preprocessing`。
- 定位算法从单一 energy stack 扩展为 multi-attribute scan，包含能量、归一化能量、轻量匹配子波、一致性 semblance。
- 第三方全波场/FWI 工程不进入主流程；本项目仍是 kinematic DAS-like 科研原型。

