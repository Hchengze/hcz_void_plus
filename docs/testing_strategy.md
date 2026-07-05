# Testing Strategy After Stage 5K

Stage 5K 后，测试目标从“图件治理覆盖”收缩到“算法主线不跑偏”。新增测试优先覆盖三维 observation kernel、receiver-consistent imaging、路径积分一致性和 `ready_for_2p5d=False`。

## core_contract

- `main.py` 仍是唯一 argparse 参数入口，不创建 `config/` 或 `para/`。
- active velocity model 默认是 `layered`，`uniform` 只作为 baseline。
- active forward engine 是 `layered_kinematic`。
- forward 和 localization 共用 `observation_kernel_3d`。
- scan candidate 到时来自 source→candidate→receiver path integration。
- receiver-consistent imaging volume 使用接收记录沿 scatter time 取样。
- `kinematic_volume_response` 是 `visualization_only`，不能作为定位依据。
- Rayleigh benchmark 未通过时 `ready_for_2p5d=False`。

## lightweight_smoke

- elastic2d/staggered 只保留最小 benchmark smoke 和结论边界。
- latest_stable 只保留导出 smoke，不再为每张图写独立测试。
- 3D plotting 保留可运行 smoke，不再阻塞核心算法推进。

## Stage 5K reduction

本轮删除 5 个低价值治理测试：

- `tests/test_animation_outputs.py`
- `tests/test_manual_review_readiness.py`
- `tests/test_latest_stable_metadata_consistency.py`
- `tests/test_latest_stable_three_category_structure.py`
- `tests/test_latest_stable_curator.py`

删除原因：这些测试主要检查图件、动图、latest_stable 结构或 manual-review 清单，已经由 full_pipeline smoke 和导出流程覆盖。Stage 5K 之后，测试预算优先用于三维 forward/localization 协同，而不是旧图件逐项存在性。
