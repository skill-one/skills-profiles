# 创建设计系统规则

## 概述

这项技能帮助您根据项目的特定需求生成自定义设计系统规则。这些规则指导 AI 编码代理在实现 Figma 设计时生成一致、高质量的代码，确保您的团队规范、组件模式和架构决策能够自动遵循。

### 支持的规则文件

| 代理 | 规则文件 |
|------|----------|
| Claude Code | `CLAUDE.md` |
| Codex CLI | `AGENTS.md` |
| Cursor | `.cursor/rules/figma-design-system.mdc` |

## 设计系统规则是什么？

设计系统规则是项目级别的指令，它们将代码库的“未写明的知识”编码化——这是经验丰富的开发者所了解并会传递给新团队成员的专业知识：

- 使用哪些布局原语和组件
- 组件文件应放置在何处（例如 `src/components/`、`app/ui/`、`lib/components/`）
- 组件的命名和结构方式
- 什么不应该硬编码
- 如何处理设计令牌和样式
- 项目特定的架构模式

一旦定义，这些规则将显著减少重复的提示，并确保在所有 Figma 实现任务中的一致输出。

## 前提条件

- Figma MCP 服务器必须已连接并可访问
  - 在继续之前，请检查 Figma MCP 工具（例如 `create_design_system_rules`）是否可用，以验证 Figma MCP 服务器是否已连接。
  - 如果这些工具不可用，则 Figma MCP 服务器可能未启用。请指导用户启用随插件提供的 Figma MCP 服务器。他们可能需要重启 MCP 客户端。
- 可以访问项目代码库进行分析
- 了解您团队的组件规范（或愿意建立规范）

## 何时使用此技能

在以下情况下使用此技能：

- 开始一个将使用 Figma 设计的新项目
- 将 AI 编码代理引入具有既定模式的现有项目
- 在团队中标准化 Figma 到代码的工作流程
- 更新或完善现有的设计系统规范
- 用户明确请求：“创建设计系统规则”、“设置 Figma 指南”、“为我的项目自定义规则”

## 必需的工作流程

**按顺序执行以下步骤，不要跳过步骤。**

### 第 1 步：运行创建设计系统规则工具

调用 Figma MCP 服务器的 `create_design_system_rules` 工具以获取基础提示和模板。

**参数：**

- `clientLanguages`：项目使用的语言列表，用逗号分隔（例如 `"typescript,javascript"`、`"python"`、`"javascript"`）
- `clientFrameworks`：使用的框架（例如 `"react"`、`"vue"`、`"svelte"`、`"angular"`、`"unknown"`）

此工具将返回创建设计系统规则的指导和建议模板。

按照工具响应中提供的模板格式构建您的设计系统规则。

### 第 2 步：分析代码库

在最终确定规则之前，分析项目以了解现有模式：

**组件组织：**

- UI 组件位于何处？（例如 `src/components/`、`app/ui/`、`lib/components/`）
- 是否有专门的设计系统目录？
- 组件如何组织？（按功能、按类型、扁平结构）

**样式方法：**

- 使用哪种 CSS 框架或方法？（Tailwind、CSS Modules、styled-components 等）
- 设计令牌定义在哪里？（CSS 变量、主题文件、配置文件）
- 是否有现有的颜色、排版或间距令牌？

**组件模式：**

- 使用哪些命名约定？（PascalCase、kebab-case、前缀）
- 组件的 props 通常如何结构化？
- 是否有常见的组合模式？

**架构决策：**

- 如何处理状态管理？
- 使用什么路由系统？
- 是否有特定的导入模式或路径别名？

### 第 3 步：生成项目特定规则

根据您的代码库分析，创建一套全面的规则。包括：

#### 一般组件规则

```markdown
- IMPORTANT: 尽可能使用 `[YOUR_PATH]` 中的组件
- 将新的 UI 组件放置在 `[COMPONENT_DIRECTORY]`
- 遵循 `[NAMING_CONVENTION]` 进行组件命名
- 组件必须以 `[EXPORT_PATTERN]` 导出
```

#### 样式规则

```markdown
- 使用 `[CSS_FRAMEWORK/APPROACH]` 进行样式设置
- 设计令牌定义在 `[TOKEN_LOCATION]`
- IMPORTANT: 永不硬编码颜色——始终使用来自 `[TOKEN_FILE]` 的令牌
- 间距值必须使用 `[SPACING_SYSTEM]` 尺度
- 排版遵循 `[TYPOGRAPHY_LOCATION]` 中定义的尺度
```

#### Figma MCP 集成规则

```markdown
## Figma MCP 集成规则

这些规则定义了如何将 Figma 输入转换为此项目的代码，并且必须遵循每个 Figma 驱动的更改。

### 必需的流程（不要跳过）

1. 首先运行 `get_design_context` 以获取精确节点的结构化表示
2. 如果响应太大或被截断，运行 `get_metadata` 获取高级节点映射，然后重新获取所需的节点
3. 运行 `get_screenshot` 获取节点变体的视觉参考
4. 只有在您同时拥有 `get_design_context` 和 `get_screenshot` 后，才下载所需的资源并开始实现
5. 将输出（通常是 React + Tailwind）转换为此项目的约定、样式和框架
6. 在标记完成之前，与 Figma 进行 1:1 的外观和行为验证

### 实现规则

- 将 Figma MCP 输出（React + Tailwind）视为设计和行为的表示，而不是最终的代码样式
- 在适用的情况下，用 `[YOUR_STYLING_APPROACH]` 替换 Tailwind 实用类
- 尽可能重用来自 `[COMPONENT_PATH]` 的现有组件，而不是重复功能
- 一致地使用项目的颜色系统、排版尺度和间距令牌
- 尊重现有的路由、状态管理和数据获取模式
- 力求与 Figma 设计 1:1 的视觉一致性
- 在最终 UI 与 Figma 截图进行 1:1 的外观和行为验证之前进行验证
```

#### 资源处理规则

```markdown
## 资源处理

- Figma MCP 服务器提供了一个资源端点，可以提供图像和 SVG 资源
- IMPORTANT: 如果 Figma MCP 服务器返回图像或 SVG 的本地主机源，请直接使用该源
- IMPORTANT: 不要导入/添加新的图标包——所有资源都应在 Figma 负载中
- IMPORTANT: 如果提供了本地主机源，不要使用或创建占位符
- 将下载的资源存储在 `[ASSET_DIRECTORY]`
```

#### 项目特定约定

```markdown
## 项目特定约定

- [添加任何独特的架构模式]
- [添加任何特殊的导入要求]
- [添加任何测试要求]
- [添加任何可访问性标准]
- [添加任何性能考虑]
```

### 第 4 步：将规则保存到相应的规则文件

检测用户正在使用的 AI 编码代理，并将生成的规则保存到相应的文件：

| 代理 | 规则文件 | 备注 |
|------|----------|------|
| Claude Code | 项目根目录下的 `CLAUDE.md` | Markdown 格式。也可以使用 `.claude/rules/figma-design-system.md` 进行模块化组织。 |
| Codex CLI | 项目根目录下的 `AGENTS.md` | Markdown 格式。如果文件已存在，则追加为新部分。32 KiB 合并大小限制。 |
| Cursor | `.cursor/rules/figma-design-system.mdc` | 带有 YAML 前面的 Markdown（`description`、`globs`、`alwaysApply`）。 |

如果不确定用户正在使用哪个代理，请检查项目中的现有规则文件或询问用户。

对于 Cursor，用 YAML 前面包裹规则：

```markdown
---
description: 使用 Figma MCP 服务器实现 Figma 设计的规则。涵盖组件组织、样式约定、设计令牌、资源处理和必需的 Figma 到代码的工作流程。
globs: "src/components/**"
alwaysApply: false
---

[生成的规则]
```

自定义 `globs` 模式以匹配 Figma 源代码将存在于项目中的目录（例如 `"src/**/*.tsx"` 或 `["src/components/**", "src/pages/**"]`）。

保存后，规则将自动由代理加载并应用于所有 Figma 实现任务。

### 第 5 步：验证和迭代

创建规则后：

1. 使用简单的 Figma 组件实现进行测试
2. 验证代理是否正确遵循规则
3. 精炼任何不符合预期的规则
4. 与团队成员分享以获取反馈
5. 随着项目的演变更新规则

## 规则类别和示例

### 必要规则（始终包含）

**组件发现：**

```markdown
- UI 组件位于 `src/components/ui/`
- 功能组件位于 `src/components/features/`
- 布局原语位于 `src/components/layout/`
```

**设计令牌使用：**

```markdown
- 颜色定义为 CSS 变量在 `src/styles/tokens.css` 中
- 永不硬编码十六进制颜色——使用 `var(--color-*)` 令牌
- 间距使用 4px 基础尺度：`--space-1`（4px）、`--space-2`（8px）等
```

**样式方法：**

```markdown
- 使用 Tailwind 实用类进行样式设置
- 自定义样式放在组件级 CSS Modules 中
- 主题定制在 `tailwind.config.js` 中
```

### 推荐规则（非常有价值）

**组件模式：**

```markdown
- 所有组件必须接受 `className` prop 以进行组合
- 变体 prop 应使用联合类型：`variant: 'primary' | 'secondary'`
- 图标组件应接受 `size` 和 `color` prop
```

**导入约定：**

```markdown
- 使用路径别名：`@/components`、`@/styles`、`@/utils`
- 分组导入：React、第三方、内部、类型
- 不应使用相对导入，除了父目录
```

**代码质量：**

```markdown
- 为导出的组件添加 JSDoc 注释
- 为所有 props 添加 PropTypes 或 TypeScript 类型
- 将魔法数字提取到命名常量中
```

### 可选规则（项目特定）

**可访问性：**

```markdown
- 所有交互元素必须有 `aria-labels`
- 颜色对比度必须符合 WCAG AA 标准
- 所有交互都需要键盘导航
```

**性能：**

```markdown
- 使用来自 `@/components/Image` 的 `Image` 组件懒加载图像
- 使用 React.memo 处理接收复杂 props 的组件
- 图标应该是 SVG 组件，而不是图标字体
```

**测试：**

```markdown
- 在 `__tests__` 目录中为新组件包含单元测试
- 使用 Testing Library 查询（getByRole、getByLabelText）
- 测试所有交互状态和变体
```

## 示例

### 示例 1：React + Tailwind 项目

用户说：“为我的 React 项目创建设计系统规则”

**操作：**

1. 运行 `create_design_system_rules(clientLanguages="typescript,javascript", clientFrameworks="react")`
2. 分析代码库结构
3. 生成规则：

```markdown
# Figma MCP 集成规则

## 组件组织

- UI 组件位于 `src/components/ui/`
- 页面组件位于 `src/app/`
- 使用 Tailwind 进行样式设置

## Figma 实现流程

1. 运行 `get_design_context` 为节点
2. 运行 `get_screenshot` 获取视觉参考
3. 将 Figma 颜色映射到 `tailwind.config.js` 中定义的 Tailwind 颜色
4. 尽可能重用 `src/components/ui/` 中的组件
5. 在完成之前与截图进行验证

## 样式规则

- IMPORTANT: 使用 Tailwind 实用类，而不是内联样式
- 颜色定义在 `tailwind.config.js` theme.colors 中
- 间距使用 Tailwind 的默认尺度
- 自定义组件放在 `src/components/ui/`

## 资源规则

- IMPORTANT: 直接使用 Figma MCP 服务器返回的本地主机源
- 将静态资源存储在 `public/assets/`
- 不要安装新的图标库
```

4. 保存到用户代理的相应规则文件
5. 使用一个简单的按钮实现进行测试

**结果：** 代理现在在实现 Figma 设计时始终遵循项目的约定。

### 示例 2：Vue + 自定义 CSS 项目

用户说：“为我的 Vue 应用设置 Figma 规则”

**操作：**

1. 运行 `create_design_system_rules(clientLanguages="typescript,javascript", clientFrameworks="vue")`
2. 发现项目使用 CSS Modules 和自定义设计令牌系统
3. 生成规则：

```markdown
# Figma MCP 集成规则

## 组件组织

- 组件位于 `src/components/`
- 组合式 API 位于 `src/composables/`
- Vue SFC 结构：`<script setup>`、`<template>`、`<style scoped>`

## 设计令牌

- IMPORTANT: 所有颜色定义在 `src/styles/tokens.css` 中作为 CSS 变量
- 使用 `var(--color-primary)`、`var(--color-secondary)` 等
- 间距：`var(--space-xs)` 到 `var(--space-xl)`
- 排版：`var(--text-sm)` 到 `var(--text-2xl)`

## Figma 实现流程

1. 运行 `get_design_context` 和 `get_screenshot`
2. 将 React 输出转换为 Vue 3 Composition API
3. 将 Figma 颜色映射到 `src/styles/tokens.css` 中的 CSS 变量
4. 使用 CSS Modules 进行组件样式
5. 在创建新组件之前检查 `src/components/` 中的现有组件

## 样式规则

- 使用 CSS Modules（`.module.css` 文件）
- IMPORTANT: 引用设计令牌，永不硬编码值
- CSS Modules 的作用域样式
```

4. 保存到用户代理的相应规则文件
5. 使用一个卡片组件进行验证

**结果：** 代理现在可以正确地将 Figma 设计转换为 Vue 组件，并使用项目的设计令牌系统。

### 示例 3：设计系统团队

用户说：“为我们的设计系统库生成规则”

**操作：**

1. 运行 `create_design_system_rules(clientLanguages="typescript", clientFrameworks="react")`
2. 分析包含设计系统包的 monorepo 结构
3. 生成全面的规则：

```markdown
# 设计系统规则

## 仓库结构

- 设计系统组件：`packages/design-system/src/components/`
- 文档：`packages/docs/`
- 设计令牌：`packages/tokens/src/`

## 组件开发

- IMPORTANT: 所有组件都必须在 `packages/design-system/src/components/`
- 组件文件结构：`ComponentName/index.tsx`、`ComponentName.stories.tsx`、`ComponentName.test.tsx`
- 从 `packages/design-system/src/index.ts` 导出所有组件

## 设计令牌

- 颜色：`packages/tokens/src/colors.ts`
- 排版：`packages/tokens/src/typography.ts`
- 间距：`packages/tokens/src/spacing.ts`
- IMPORTANT: 永不硬编码值——从令牌包导入

## 文档要求

- 为每个组件添加 Storybook 故事
- 使用 @example 添加 JSDoc
- 描述所有 props
- 添加可访问性说明

## Figma 集成

1. 从 Figma 获取设计上下文和截图
2. 将 Figma 令牌映射到设计系统令牌
3. 在设计系统包中创建或扩展组件
4. 添加展示所有变体的 Storybook 故事
5. 与 Figma 截图进行验证
6. 更新文档
```

4. 保存到相应的规则文件并与团队分享
5. 添加到团队文档

**结果：** 整个团队在将 Figma 添加到设计系统时遵循一致的模式。

## 最佳实践

### 从简单开始，迭代

不要试图从一开始就捕获所有规则。从最重要的约定开始，并在遇到不一致时添加规则。

### 保持具体

而不是：使用设计系统
写：始终使用来自 `src/components/ui/Button.tsx` 的 Button 组件，variant prop 为 ('primary' | 'secondary' | 'ghost')

### 使规则可执行

每个规则都应告诉代理确切要做什么，而不仅仅是避免什么。

好：颜色定义在 `src/theme/colors.ts` 中——导入并使用这些常量
坏：不要硬编码颜色

### 使用 IMPORTANT 标记关键规则

用 "IMPORTANT:" 前缀标记必须始终遵守的规则，以确保代理优先考虑它们。

```markdown
- IMPORTANT: 不要在客户端代码中暴露 API 密钥
- IMPORTANT: 始终在渲染之前清理用户输入
```

### 记录原因

当规则看起来很任意时，解释其理由：

```markdown
- 将所有数据获取放在服务器组件中（减少客户端捆绑包大小并提高性能）
- 使用绝对导入和 `@/` 别名（使重构更容易并防止相对路径损坏）
```

## 常见问题和解决方案

### 问题：代理没有遵循规则

**原因：** 规则可能过于模糊或代理没有正确加载规则。
**解决方案：**

- 使规则更具体和可执行
- 验证规则是否保存在正确的配置文件中
- 重启您的代理或 IDE 以重新加载规则
- 为关键规则添加 "IMPORTANT:" 前缀

### 问题：规则相互冲突

**原因：** 互相矛盾或重叠的规则。
**解决方案：**

- 审查所有规则是否存在冲突
- 建立明确的优先级层次结构
- 删除冗余规则
- 将相关的规则合并为单个清晰的陈述

### 问题：太多规则导致延迟增加

**原因：** 过多的规则增加了上下文大小和处理时间。
**解决方案：**

- 专注于解决 80% 的问题的 20% 的规则
- 删除过于具体的规则，这些规则很少适用
- 合并相关规则
- 使用渐进式披露（基本规则首先，高级规则在链接的文件中）

### 问题：随着项目演变，规则变得过时

**原因：** 代码库发生变化，但规则没有更新。
**解决方案：**

- 定期审查规则（每月或每季度）
- 当架构决策发生变化时更新规则
- 版本控制您的规则文件
- 在提交消息中记录规则更改

## 理解设计系统规则

设计系统规则改变了 AI 编码代理如何与您的 Figma 设计合作：

**规则之前：**

- 代理对组件结构做出假设
- 实现中样式方法不一致
- 不匹配设计令牌的硬编码值
- 组件随机放置
- 重复解释项目约定

**规则之后：**

- 代理自动遵循您的约定
- 组件结构和样式一致
- 从一开始就正确使用设计令牌
- 组件放置正确
- 零重复提示

在创建良好规则上投入的时间在每次 Figma 实现任务中都会成倍回报。

## 额外资源

- [Figma MCP 服务器文档](https://developers.figma.com/docs/figma-mcp-server/)
- [Figma 变量和设计令牌](https://help.figma.com/hc/en-us/articles/15339657135383-Guide-to-variables-in-Figma)
