# Tailwind CSS

请遵循已安装的 Tailwind 版本以及仓库中的 tokens、组件、类合并工具、CSS 入口文件和附近的 UI。它们优先于此技能；未经请求和本地需求，不要添加包、更改集成或迁移版本。

## 路由

- 仅在项目未明确说明的情况下应用 [编码偏好](references/coding-preferences.md)。
- 对于 v4 配置、迁移、指令或生成的类，使用 [v4 规则](references/tailwind-v4-rules.md) 以及匹配的官方文档。
- 仅当本地存在该集成或请求添加时，才阅读 [tailwind-variants](references/tailwind-variants.md)、[tw-animate-css](references/tw-animate-css.md) 或 [ESLint](references/eslint.md)。

不要将 v4 语法应用于较旧的安装。保留响应式、交互、可访问性和暗黑模式行为；不要超出请求范围进行重新设计。

## 完成

定义预期的视觉和状态变化，重用本地约定，并保持类的静态可发现性。如果源注册或生成的映射发生变化，请运行真实的 Tailwind 构建，并确认预期的工具。运行相关的仓库检查，然后在代表性的视口、主题和交互状态下检查更改的 UI。当标记由 JavaScript 或组件库转换时，也要检查最终的 DOM。仅靠文本类审查是不够的。

以 `### 🎨 Tailwind — ✅ styling updated`（或 `### 🎨 Tailwind — 🔎 inspected, no files written`）结束，附带一个紧凑的视口/主题/状态/结果表格，以及分离的代码检查和渲染检查证据。仅在需要时添加 `### ⚠️ Remaining`；保持源 UI 复本和诊断信息未经装饰。
