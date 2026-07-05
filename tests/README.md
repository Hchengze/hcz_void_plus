# Tests

Stage 5I 后，测试按三层维护：

- `core_contract`：长期契约，覆盖参数入口、active velocity model、active forward engine、latest_stable 三类结构、三维 policy 和 ready_for_2p5d 逻辑。
- `lightweight_smoke`：轻量 smoke，覆盖 elastic2d/staggered benchmark、DAS gauge 报告、动图输出和 latest_stable 导出。
- `archive_or_reduce`：可收缩测试，主要是早期二维 validation 的细碎图件存在性和重复格式检查。

Stage 5I 起，图件测试优先检查 manifest、tree snapshot 和 manual review 清单；新增测试优先检查 scan path integration、多属性体、posterior-like uncertainty 和三维几何分辨率。测试的目标不是证明工程可探测，而是保证当前科研候选流程的结论、图件和算法契约不互相打架。
