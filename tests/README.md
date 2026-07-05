# Tests

Stage 5J 后，测试继续按三层维护，但重心回到算法契约，而不是逐张图件存在性。

- `core_contract`：长期保留，覆盖 `main.py` 唯一参数入口、active velocity model、active forward engine、三维 source/receiver/candidate 主线、scan path integration、posterior-like uncertainty、`ready_for_2p5d=False` 逻辑。
- `lightweight_smoke`：轻量保留，覆盖 elastic2d/staggered benchmark 结论、DAS gauge 报告口径、latest_stable 三类结构、动图输出和三维绘图接口。
- `archive_or_reduce`：继续收缩，主要处理旧阶段二维 validation、单图存在性、图件格式和历史 latest_stable 结构的重复测试。

本轮删除的过细测试：

- `test_latest_stable_stage5f_files.py`：Stage 5F 文件清单已被 Stage 5J 三类结构取代。
- `test_latest_stable_forward_outputs.py`：逐张 forward 图存在性检查改由 manifest/manual review 契约覆盖。
- `test_figure_label_audit.py`：图件中文化不再为每张图新增重测试，保留语言/清单级 smoke。
- `test_figure_quality_check.py`：质量检查保留在导出流程，不再作为独立细碎测试阻塞算法推进。
- `test_figure_self_check.py`：文件级自检已由 latest_stable 导出流程统一执行。
- `test_document_cleanup.py`：旧文档清理审计已完成，不再作为 Stage 5J 算法推进的阻塞契约。
- `test_repository_health_report.py`：repository health 报告属于阶段治理输出，不再逐轮阻塞生产算法开发。
- `test_scientific_figure_self_check.py`：科学图件自检已收敛到 manual review / manifest 层级，不再逐项测试。
- `test_latest_stable_curated.py`：旧 curated 结构检查由三类目录和 metadata consistency 测试覆盖。

新增测试优先服务 Stage 5J 主线：三维运动学体响应、经验 attenuation、forward-localization 契约和 `ready_for_2p5d=False`。
