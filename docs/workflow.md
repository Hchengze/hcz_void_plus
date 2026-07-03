# Workflow

Stage 1 的运行流程：

1. `main.py` 解析命令行参数。
2. `main.py` 执行原始参数校验。
3. `main.py` 派生 `channel_x`、`receiver_xyz`、`shot_x`、`source_xyz`、`time_axis`、`nt` 和输出目录。
4. `main.py` 执行派生参数校验。
5. pipeline 设置随机种子。
6. pipeline 构建几何、速度模型、异常体和等效散射点。
7. 正演模块生成直达波和散射/绕射波。
8. DAS-like 模块应用 point receiver approximation。
9. pipeline 保存数组、metadata、参数快照、图件、报告和日志。

所有核心算法输出均标注 `kinematic approximation` 和 `DAS-like response approximation`。
