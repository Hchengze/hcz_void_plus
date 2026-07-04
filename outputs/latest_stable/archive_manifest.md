# archive manifest

Stage 5C 起，latest_stable 不再平铺保存所有历史阶段图件和报告。

## 不再作为当前主结论平铺保存的内容

- 旧 Stage 3/4/5A 的大量诊断图件不再平铺保存在 latest_stable/figures 根目录。
- FK、matched wavelet、semblance、frequency shift 等详细验证仍保存在时间戳运行目录。
- latest_stable 只保留当前阶段最关键 curated outputs。

完整历史输出仍保存在对应时间戳运行目录；Git 中的 latest_stable 只保留当前精选成果。