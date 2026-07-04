# elastic2d Rayleigh/free-surface 验证报告

本报告基于最小 collocated-grid velocity-stress elastic2d prototype。它是局部物理验证起点，不是工业级 elastic 模拟。

- CFL stable：`True`。
- CFL number：`0.35`。
- estimated surface velocity：`316.1` m/s。
- expected sanity range：`[212.5, 245.0]` m/s。
- rayleigh_like_event_detected：`False`。
- estimation method：`envelope_peak_moveout`。

## 边界

- 顶部自由表面为近似 traction-free 处理。
- 当前格式是 collocated-grid minimal prototype，精度和稳定性不等同于 staggered-grid/PML 工业实现。
- 该结果只能说明出现 Rayleigh-like surface event 的 sanity check，不能作为工程级 Rayleigh 正演。