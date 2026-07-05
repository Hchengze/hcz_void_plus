# Stage 5I testing strategy

本项目的测试策略从 Stage 5G 起收缩为三层，Stage 5I 继续收敛：图件测试以 manifest、tree snapshot 和 manual review 清单为主，新增测试优先覆盖三维运动学反演契约，不再为每一张静态图写独立存在性测试。

## core_contract

长期保留，任何阶段都必须通过：

- `main.py` 是唯一 argparse 参数入口，不创建 `config/` 或 `para/`。
- active velocity model 默认是 `layered`，`uniform` 只作为 baseline。
- active forward engine 是 `layered_kinematic`。
- `layered_kinematic` 能运行，并且 direct / scatter / scan 使用 velocity_model travel-time 接口。
- `outputs/latest_stable` 采用 `forward / localization / error_analysis` 三类结构。
- `summary.md` 记录 Stage 5I、algorithm/latest_stable commit、manual review 图件、scan path integration、posterior-like 体、ready_for_2p5d 逻辑和 DAS gauge 口径。
- `metadata/latest_stable_tree_snapshot.txt` 固化当前 latest_stable 文件树。
- 三维 policy、三维几何图、三维高分区图和不确定性盒子接口必须可运行。

## lightweight_smoke

轻量保留，用于验证 validation forward 与输出链路没有断：

- elastic2d / staggered 最小 benchmark 能输出多个 case。
- Rayleigh benchmark 输出矩阵、速度误差和 surface event ridge。
- DAS gauge 报告输出，并明确不默认用于定位。
- 两个 GIF 能生成并进入 latest_stable。
- latest_stable 导出后图件数量受控，空图、重复图、英文 case label 不进入当前精选。
- manual review readiness 报告能确认关键 3D 图和两个 GIF 可供人工查看。

## archive_or_reduce

可归档或收缩，不再作为长期主线门槛：

- 过度细碎的单图存在性测试。
- 只针对早期 acoustic2d 或二维内部数组细节的测试。
- 多个测试重复检查同一 latest_stable 图是否存在。
- 未来三维化后大概率会重写的 elastic2d 内部格式细节。

本轮没有取消测试，而是把新增测试优先指向 Stage 5I 的三维运动学正演-定位一致性、多属性体、posterior-like uncertainty 和几何分辨率诊断。若删除或归档测试，提交说明必须解释原因；保留测试则优先覆盖项目边界和人工复查入口。

Stage 5I 后，3D plotting 只保留 smoke test 和关键 metadata/tree/manual-review 测试；elastic2d/staggered 只保留 benchmark smoke 与 Rayleigh 结论边界测试。过度细碎、面向早期二维内部数组的测试继续归入 `archive_or_reduce`。
