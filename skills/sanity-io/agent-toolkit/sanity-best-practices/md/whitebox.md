# sanity-best-practices (`sanity-io/agent-toolkit/sanity-best-practices`)

## whitebox

- 接收 Sanity 相关任务 (schema/GROQ/框架集成/Studio/Functions 等), 识别所属领域
- 按速查表路由到最匹配的 1~2 个主题或框架指南 (如 nextjs + groq)
- 读取对应 references/*.md, 提取其中的正误代码示例与决策矩阵
- 套用全局规则和指南模式, 产出新代码或审查/修复现有代码
- 仅当任务跨领域时, 才补读额外的参考文件

- 按需路由加载: 指南以 references/<topic>.md 文件集形式组织 (groq.md、schema.md、nextjs.md…), 每次只加载命中任务的 1~2 个文件, 不全量读入
- 正误对照驱动: 每份参考文件内含 incorrect/correct 代码示例、决策矩阵和框架特有模式, 作为生成与审查代码的直接依据; 运行时是纯静态知识, 不调用任何外部模型 API
- 全局硬规则兜底: _id 一律由 Sanity 生成、关系用 reference 字段 + GROQ 解析、显式 ID 仅限 singleton; 视频禁止走 file 资产, 须走 Media Library (defineVideoField + @mux/mux-player-react) 或 Mux/YouTube/Vimeo 等流媒体服务
