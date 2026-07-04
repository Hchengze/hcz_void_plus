# Stage 5F 文档清理报告

分类标签：`current`、`archive`、`delete`、`generated_only`。

## 结论

Stage 5F 已完成一次文档审计。当前主依据为 `README.md`、`docs/current_status.md`、`docs/current_algorithm_boundary.md`、`code/current_3d_algorithm/` 和 `outputs/latest_stable/summary.md`。

## 分类清单

| 文档 | 分类 | 原因 | 动作 |
|---|---|---|---|
| `README.md` | current | 当前总入口，需要写清 Stage 5F、layered_kinematic、elastic2d validation 和 latest_stable 精选治理。 | 更新 |
| `docs/current_status.md` | current | 当前事实清单，旧版仍偏 Stage 5E。 | 重写为 Stage 5F |
| `docs/current_algorithm_boundary.md` | current | 当前算法边界。 | 增加 Stage 5F 边界 |
| `code/current_3d_algorithm/` | current | 稳定算法成果区。 | 更新 stable_api |
| `docs/forward_modeling_roadmap.md` | current | forward F0-F6 路线仍有价值。 | 保留 |
| `docs/model_assumptions.md` | current | 模型假设仍有价值。 | 保留 |
| `docs/reference_algorithm_matrix.md` | current | reference-backed 算法映射仍有价值。 | 保留 |
| `docs/workflow.md` | archive | 主要描述 Stage 4A/3C 流程，容易被误读为当前流程。 | 移至 `docs/archive/workflow.md` |
| `docs/scan_and_confidence.md` | archive | 主要描述 Stage 3 扫描和规则型置信度，不能代表 Stage 5F。 | 移至 `docs/archive/scan_and_confidence.md` |
| `docs/das_like_approximation.md` | archive | 早期 DAS-like 近似说明，未包含 Stage 5F gauge 口径。 | 移至 `docs/archive/das_like_approximation.md` |
| `outputs/latest_stable/reports/*` | generated_only | 运行输出报告，只代表本次 latest_stable，不作为长期开发规范。 | 保留在 latest_stable |

## 删除清单

本轮没有直接删除文档。理由是旧文档仍保留项目演进价值；对会误导当前开发的文档已归档并加醒目标记。

## 当前约束

- 不把历史 Stage 3/4/5A 文档作为当前算法依据。
- 不删除 reference、roadmap、算法设计和模型假设中仍有价值的内容。
- generated_only 报告只用于审计本次运行结果，不作为长期规范。
