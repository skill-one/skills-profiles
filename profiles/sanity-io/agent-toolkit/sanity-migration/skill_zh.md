# Sanity 迁移

使用此技能进行 CMS 到 Sanity 的迁移工作。将迁移视为内容策略和 ETL 项目，而不是盲目的迁移。

## 必须遵循的工作流程

1. 首先阅读 `references/general.md`。
2. 如果源平台已知，请也阅读其指南：
   - AEM / Adobe Experience Manager: `references/aem.md`
   - Contentful: `references/contentful.md`
   - Strapi: `references/strapi.md`
   - Webflow: `references/webflow.md`
   - WordPress / WXR / Elementor: `references/wordpress.md`
   - Payload: `references/payload.md`
   - Drupal: `references/drupal.md`
   - Markdown / MDX / frontmatter 文件: `references/markdown.md`
3. 在编写代码之前，制定一个简短的迁移计划，涵盖源访问、内容范围、模式决策、提取、转换、导入、验证、重定向和切换。
4. 对于实际迁移，优先使用确定性、可重复的脚本。编写和审查迁移脚本、映射和验证检查；不要依赖一次性内容操作来处理大量内容。

## 需要产出物

对于实施或规划任务，产出这些文档或解释为什么不需要：

- 内容清单：源类型、数量、区域、状态/草稿范围、资产和关系类型。
- 源到 Sanity 的映射：文档类型、对象类型、引用、Portable Text 字段、资产字段、ID 和跳过的内容。
- 提取方法：需要的凭证/访问权限、API/导出命令、原始快照位置和已知的盲点。
- 转换/导入计划：确定性 ID、写入顺序、资产处理、富文本转换、验证和重跑策略。
- 切换计划：增量同步/内容冻结、重定向、断链检查、SEO 元数据和手动清理。

## 默认值

- 使用从源 ID、slug、路径或哈希派生的稳定文档 ID。
- 使用 `createOrReplace`、`createIfNotExists` 或 `sanity datasets import --replace` 以确保重跑时收敛。
- 在转换之前将提取的源数据快照保存到磁盘。
- 在引用其他文档的文档之前导入或创建引用的文档。
- 将富文本转换为 Portable Text，而不是存储原始 HTML 或 Markdown 字符串。
- 将资产上传到 Sanity 或媒体库；不要让生产内容依赖于遗留 CDN URL。
- 跟踪每个文档的质量问题，并在切换前产出验证摘要。
- 保留遗留 URL 和源 ID 以便重定向、QA 和未来调试。

## Sanity 指导原则

- 定义内容是什么，而不是旧站点的渲染方式。
- 使用文档表示可重用或独立管理的实体；使用对象表示属于一个文档的内容。
- 如果编写 Sanity 模式，使用 `defineType`、`defineField` 和 `defineArrayMember`。
- 使用 Sanity 上传的资产或媒体库资产的字段，而不是遗留 CDN URL。
- 使用 Portable Text 数组表示富文本和自定义块；不要将原始 HTML 存储为规范正文。
- 当项目使用 TypeScript 时，在模式或 GROQ 查询更改后运行模式提取和 TypeGen。
- 在使用 MCP/内容工具之前部署或应用模式更改。

如果已有 `sanity-best-practices`，请使用它获取更深入的 Sanity 实施指导。如果没有安装，可以告诉用户使用以下命令添加：

```bash
npx skills add sanity-io/agent-toolkit --skill sanity-best-practices
```

## 停止并询问

在编码前，如果以下任何项不明确，请停止：

- 源访问路径、凭证、导出文件或数据库连接。
- 目标 Sanity 项目/数据集或是否应使用草稿数据集。
- 草稿、存档、计划、区域或版本历史范围。
- 媒体文件是否应迁移，以及资产 URL/文件是否可访问。
- 目标模式是否存在或是否应作为迁移的一部分设计。

## 不要这样做

- 不要为源支持的文档创建随机 ID。
- 不要先获取再创建引用的文档；使用确定性 ID 和 `createIfNotExists`/`createOrReplace`。
- 不要通过 MCP 内容工具运行批量迁移，除非 NDJSON 或脚本更合适。
- 除非有要求，否则不要将区域回退值展平为翻译。
- 不要为需要的媒体、作者、引用或富文本转换留下 TODO。
- 在进行计数检查、样本检查、引用检查和路由/重定向检查之前，不要宣布迁移完成。

## 参考映射

使用 `references/general.md` 获取共享迁移原则，并使用平台参考获取源特定的提取路径、建模陷阱和验证检查。

对于未明确涵盖的源系统，应用 `references/general.md` 并调整最接近的平台模式：
- API 首先的 CMS：从 Contentful、Strapi 或 Payload 开始。
- 单体/页面构建器系统：从 WordPress、Drupal、Webflow 或 AEM 开始。
- HTML 为主的导出：从 WordPress 和 Webflow 富文本指南开始。
- Markdown 首先的源：从 `references/markdown.md` 开始。
