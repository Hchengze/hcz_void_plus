# Devito adapter plan

Devito 可作为 symbolic finite-difference / PDE propagator 组织方式的参考。当前不接入 Devito，也不复制代码。

未来 adapter 需要：

1. 明确输入模型、网格、震源、接收和边界；
2. 明确输出 wavefield、shot gather 和 diagnostics；
3. 明确 license 和依赖安装方式；
4. 保持 `main.py` 是唯一 argparse 入口；
5. 只作为 validation forward，不直接替代 `layered_kinematic` 主流程。
