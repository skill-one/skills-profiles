# Sanity 最佳实践

Sanity 开发全面最佳实践和集成指南，由 Sanity 维护。使用以下快速参考来加载与任务匹配的一个或两个主题文件。

## 应用场景

在以下情况参考这些指南：
- 设置新 Sanity 项目或新员工入职
- 将 Sanity 集成到前端框架（Next.js、Nuxt、Astro、Remix、SvelteKit、Hydrogen）
- 编写 GROQ 查询或优化性能
- 设计内容模式
- 实现可视化编辑和实时预览
- 处理图像、Portable Text 或页面构建器
- 配置 Sanity Studio 结构
- 设置 TypeGen 以确保类型安全
- 实现本地化
- 从其他系统迁移内容
- 使用 Sanity App SDK 构建自定义应用
- 使用 Blueprints 管理基础设施
- 使用 Sanity Functions 或 webhook 自动化内容工作流

## 全局规则

- 让 Sanity 为普通文档生成 `_id` 值。创建文档时不要创建确定性 UUID、基于 slugs 的 ID 或遗留系统 ID。
- 使用 `reference` 字段建模关系，然后使用 GROQ 查找、源键字段或创建文档返回的 `_id` 值解析相关文档。
- 主要为受 Studio 结构控制的单例文档使用显式文档 ID，包括本地化的单例文档，如 `homePage-en`。

## 视频

- 不要从 Sanity `file` 资产存储或提供用于生产播放的视频。文件资产作为原始下载交付，没有转码或自适应流媒体，视频流量会导致非常高的带宽使用和意外高额账单。
- 在包含视频附加功能的商业计划中，使用 Sanity 媒体库处理视频：上传将通过 Mux 进行转码和自适应流媒体。使用 `sanity/media-library` 的 `defineVideoField()` 建模视频字段，并使用资产播放 ID 通过 `@mux/mux-player-react` 播放它们。
- 在其他计划中，使用专用视频服务：安装 `sanity-plugin-mux-input` 从 Studio 上传和管理 Mux 账户中的视频，或在 YouTube 或 Vimeo 等平台上托管视频，并在 Sanity 中仅存储嵌入 URL。
- `file` 字段中的小片段和简短预览可以接受，但任何大规模的用户端视频都必须通过媒体库或流媒体服务处理。

## 快速参考

### 集成指南

- `get-started` - 新 Sanity 项目的交互式入职
- `nextjs` - Next.js App Router、Live Content API、独立 Studio
- `nuxt` - Nuxt 集成与 @nuxtjs/sanity
- `angular` - Angular 集成与 @sanity/client、信号、资源 API
- `astro` - Astro 集成与 @sanity/astro
- `remix` - React Router / Remix 集成
- `svelte` - SvelteKit 集成与 @sanity/svelte-loader
- `hydrogen` - Shopify Hydrogen 与 Sanity
- `project-structure` - 独立 Studio 和单仓库模式
- `app-sdk` - 使用 Sanity App SDK 构建自定义应用
- `blueprints` - 基础设施即代码：蓝图文件、堆栈、计划/部署工作流、错误恢复、CI 部署
- `functions` - 使用 Sanity Functions 和 webhook 自动化内容工作流

### 主题指南

- `groq` - GROQ 查询模式、类型安全、性能优化
- `schema` - 模式设计、字段定义、验证、弃用模式
- `visual-editing` - Presentation Tool、Stega、覆盖层、实时预览
- `page-builder` - 页面构建器数组、块组件、实时编辑
- `portable-text` - 富文本渲染和自定义组件
- `image` - 图像模式、URL 构建器、热点、LQIP、Next.js Image
- `studio-structure` - 桌面结构、单例、导航
- `typegen` - TypeGen 配置、工作流、类型工具
- `seo` - 元数据、站点地图、Open Graph、JSON-LD
- `localization` - i18n 模式、文档级与字段级、区域管理
- `migration` - 内容导入概述（另见 `migration-html-import`）
- `migration-html-import` - HTML 到 Portable Text 与 @portabletext/block-tools

## 如何使用

从与请求最匹配的单个框架或主题指南开始，然后在任务涉及多个方面时再阅读其他参考。使用这些参考文件获取详细说明和代码示例：

```
references/groq.md
references/schema.md
references/nextjs.md
```

每个参考文件包含：
- 全面的话题或集成覆盖
- 错误和正确的代码示例
- 决策矩阵和工作流指导
- 适用于特定框架的模式
