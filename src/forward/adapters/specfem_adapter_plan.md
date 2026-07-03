# SPECFEM adapter plan

SPECFEM 可作为谱元法 seismic wave propagation 和局部 3D elastic validation 的长期参考。当前不接入 SPECFEM，不做大规模工业级 3D elastic。

未来 adapter 只应面向小域、少数震源和 receiver 的局部验证，输出与 `source_xyz / receiver_xyz / candidate_xyz` 三维几何相容的诊断结果。
