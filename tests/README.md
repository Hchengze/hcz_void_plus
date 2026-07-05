# Tests

Stage 5K 后，测试继续收缩到算法契约和轻量 smoke，不再为每一张 latest_stable 图件写独立存在性测试。

## core_contract

- `main.py` 仍是唯一 argparse 参数入口。
- active velocity model 默认是 `layered`。
- active forward engine 是 `layered_kinematic`。
- forward 和 localization 必须共享 `observation_kernel_3d` 的 source-candidate-receiver 路径表。
- receiver-consistent imaging volume 必须使用接收记录沿 scatter time 取样。
- `volume_proxy_used_for_localization=False`。
- Rayleigh benchmark 未通过时 `ready_for_2p5d=False`。

## lightweight_smoke

- elastic2d/staggered 保留最小 benchmark smoke，不进入三维主定位。
- latest_stable 只保留导出流程 smoke，不再逐图重复测试。
- 三维绘图保留接口 smoke，重点是可运行和 metadata 合理。

## Stage 5K Reduced Tests

本轮删除以下 5 个低价值治理测试：

- `test_animation_outputs.py`：动图存在性由 full_pipeline/latest_stable smoke 覆盖。
- `test_manual_review_readiness.py`：manual review 清单不再作为算法推进阻塞项。
- `test_latest_stable_metadata_consistency.py`：阶段 metadata 由 stage consistency 和 summary fields 覆盖。
- `test_latest_stable_three_category_structure.py`：三类结构已经稳定，不再逐轮阻塞核心算法。
- `test_latest_stable_curator.py`：curator 细节不再优先于 observation kernel 和成像体契约。

本轮新增测试文件数量：2。

- `test_observation_kernel_3d.py`
- `test_receiver_consistent_imaging.py`
