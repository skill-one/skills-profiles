# archify (`tt-a1i/archify/archify`)

## whitebox

- 定类型: 从提问判断五选一 (architecture / workflow / sequence / dataflow / lifecycle), 场景含糊时跑 guide 命令路由
- 读对应 schema + 一个示例 JSON (只读这两个文件), 按示例的字段形状而非事实, 直接写出候选 JSON 规格并先落盘 (artifact first)
- 校验: validate 命令以 showcase 质量跑, 必须报告全部 9 项 artifact 检查、0 组合错误 0 警告; 失败只修诊断指向的项并重跑
- 交付: deliver 命令把规格字节冻结成同目录快照, 渲染检查后原子提交 HTML, 出具规格与成品的 SHA-256 + 字节数回执
- 取证: visual-check 在真实浏览器里对已交付 HTML 做有界自动化测量与截图, 不改动、不重渲染

- 规格驱动: 输入是一份小型类型化 JSON, 输出是自包含 HTML (内联 SVG), 内置主题切换、平移缩放、搜索、关系追踪、演示模式与 PNG/JPEG/WebP/SVG/WebM 导出, 不依赖外部服务
- 外部依赖仅 Node.js: CLI bin/archify.mjs 承担类型路由、校验、交付与浏览器取证, 技能包内无需安装任何东西, 不调用任何外部模型 API
- Mermaid 转换: flowchart/sequenceDiagram/stateDiagram 只读拓扑与语义 (参与者→语义参与者、箭头→消息、状态→转移), 重新生成 Archify JSON, 不机械照搬 Mermaid 样式
