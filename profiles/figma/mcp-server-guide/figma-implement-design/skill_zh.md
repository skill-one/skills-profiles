# 实现设计

## 概述

此技能提供了一个结构化的工作流程，用于将 Figma 设计转换为具有像素级精确度的生产就绪代码。它确保与 Figma MCP 服务器的持续集成、设计令牌的正确使用以及与设计的 1:1 视觉一致性。

## 技能边界

- 当交付成果是用户仓库中的代码时，使用此技能。
- 如果用户要求在 Figma 本身内部创建/编辑/删除节点，切换到 [figma-use](../figma-use/SKILL.md)。
- 如果用户要求从代码或描述中在 Figma 中构建或更新全页屏幕，切换到 [figma-generate-design](../figma-generate-design/SKILL.md)。
- 如果用户仅要求 Code Connect 映射，切换到 [figma-code-connect](../figma-code-connect/SKILL.md)。
- 如果用户仅要求编写可重用的代理规则（`CLAUDE.md`/`AGENTS.md`），切换到 [figma-create-design-system-rules](../figma-create-design-system-rules/SKILL.md)。

## 前置条件

- Figma MCP 服务器必须已连接并可访问
- 用户必须在以下格式中提供 Figma URL：`https://figma.com/design/:fileKey/:fileName?node-id=1-2`
  - `:fileKey` 是文件密钥
  - `1-2` 是节点 ID（要实现的特定组件或框架）
- **或者** 当使用 `figma-desktop` MCP 时：用户可以直接在 Figma 桌面应用程序中选择一个节点（无需 URL）
- 项目应具有已建立的设计系统或组件库（首选）

## 必要的工作流程

**按顺序执行以下步骤。不要跳过步骤。**

### 第 1 步：获取节点 ID

#### 选项 A：从 Figma URL 解析

当用户提供 Figma URL 时，提取文件密钥和节点 ID 以作为参数传递给 MCP 工具。

**URL 格式：** `https://figma.com/design/:fileKey/:fileName?node-id=1-2`

**提取：**

- **文件密钥：** `:fileKey`（`/design/` 后面的部分）
- **节点 ID：** `1-2`（`node-id` 查询参数的值）

**注意：** 当使用本地桌面 MCP（`figma-desktop`）时，`fileKey` 不会作为工具调用的参数传递。服务器会自动使用当前打开的文件，因此只需 `nodeId` 即可。

**示例：**

- URL：`https://figma.com/design/kL9xQn2VwM8pYrTb4ZcHjF/DesignSystem?node-id=42-15`
- 文件密钥：`kL9xQn2VwM8pYrTb4ZcHjF`
- 节点 ID：`42-15`

#### 选项 B：使用 Figma 桌面应用程序的当前选择（仅限 `figma-desktop` MCP）

当使用 `figma-desktop` MCP 且用户未提供 URL 时，工具会自动使用桌面应用程序中打开的 Figma 文件中当前选择的节点。

**注意：** 基于选择的提示仅适用于 `figma-desktop` MCP 服务器。远程服务器需要链接到框架或图层以提取上下文。用户必须在 Figma 桌面应用程序中打开并选择一个节点。

### 第 2 步：获取设计上下文

使用提取的文件密钥和节点 ID 运行 `get_design_context`。

```
get_design_context(fileKey=":fileKey", nodeId="1-2")
```

这将提供结构化数据，包括：

- 布局属性（自动布局、约束、尺寸）
- 字体排印规范
- 颜色值和设计令牌
- 组件结构和变体
- 间距和填充值

**如果响应太大或被截断：**

1. 运行 `get_metadata(fileKey=":fileKey", nodeId="1-2")` 以获取高级节点映射
2. 从元数据中识别所需的特定子节点
3. 使用 `get_design_context(fileKey=":fileKey", nodeId=":childNodeId")` 获取单个子节点

### 第 3 步：捕获视觉参考

使用相同的文件密钥和节点 ID 运行 `get_screenshot` 以获取视觉参考。

```
get_screenshot(fileKey=":fileKey", nodeId="1-2")
```

此屏幕截图作为视觉验证的来源。在整个实现过程中保持其可访问性。

### 第 4 步：下载所需资源

下载 Figma MCP 服务器返回的任何资源（图像、图标、SVG）。

**重要提示：** 遵循以下资源规则：

- 如果 Figma MCP 服务器为图像或 SVG 返回 `localhost` 源，请直接使用该源
- 不要导入或添加新的图标包 - 所有资源都应来自 Figma 负载
- 如果提供 `localhost` 源，不要使用或创建占位符
- 资源通过 Figma MCP 服务器的内置资源端点提供

### 第 5 步：转换为项目规范

将 Figma 输出转换为此项目的框架、样式和规范。

**关键原则：**

- 将 Figma MCP 输出（通常是 React + Tailwind）视为设计和行为的表示，而不是最终的代码样式
- 将 Tailwind 实用类替换为项目的首选实用程序或设计系统令牌
- 重用现有组件（按钮、输入、字体排印、图标包装器）而不是重复功能
- 一致地使用项目的颜色系统、字体排印比例和间距令牌
- 尊重现有的路由、状态管理和数据获取模式

### 第 6 步：实现 1:1 视觉一致性

力求与 Figma 设计实现像素级精确的视觉一致性。

**指南：**

- 优先考虑 Figma 精确度以完全匹配设计
- 避免硬编码值 - 在可用的情况下使用 Figma 令牌
- 当设计系统令牌和 Figma 规格之间出现冲突时，优先考虑设计系统令牌，但最小程度调整间距或尺寸以匹配视觉效果
- 遵循 WCAG 要求的无障碍性
- 根据需要添加组件文档

### 第 7 步：与 Figma 验证

在标记完成之前，将最终 UI 与 Figma 屏幕截图进行验证。

**验证清单：**

- [ ] 布局匹配（间距、对齐、尺寸）
- [ ] 字体排印匹配（字体、大小、粗细、行高）
- [ ] 颜色完全匹配
- [ ] 交互状态按设计工作（悬停、激活、禁用）
- [ ] 响应式行为遵循 Figma 约束
- [ ] 资源正确渲染
- [ ] 满足无障碍性标准

## 实现规则

### 组件组织

- 将 UI 组件放置在项目的指定设计系统目录中
- 遵循项目的组件命名规范
- 除非确实需要动态值，否则避免内联样式

### 设计系统集成

- **始终** 在可能的情况下使用项目的设计系统组件
- 将 Figma 设计令牌映射到项目设计令牌
- 当存在匹配的组件时，扩展它而不是创建新的组件
- 记录添加到设计系统的任何新组件

### 代码质量

- 避免硬编码值 - 提取到常量或设计令牌
- 保持组件可组合和可重用
- 为组件属性添加 TypeScript 类型
- 为导出的组件添加 JSDoc 注释

## 示例

### 示例 1：实现一个按钮组件

用户说："实现这个 Figma 按钮组件：https://figma.com/design/kL9xQn2VwM8pYrTb4ZcHjF/DesignSystem?node-id=42-15"

**操作：**

1. 解析 URL 以提取 fileKey=`kL9xQn2VwM8pYrTb4ZcHjF` 和 nodeId=`42-15`
2. 运行 `get_design_context(fileKey="kL9xQn2VwM8pYrTb4ZcHjF", nodeId="42-15")`
3. 运行 `get_screenshot(fileKey="kL9xQn2VwM8pYrTb4ZcHjF", nodeId="42-15")` 以获取视觉参考
4. 从资源端点下载任何按钮图标
5. 检查项目是否有现有的按钮组件
6. 如果有，使用新的变体扩展它；如果没有，使用项目规范创建新组件
7. 将 Figma 颜色映射到项目设计令牌（例如，`primary-500`、`primary-hover`）
8. 与屏幕截图验证填充、边框半径、字体排印

**结果：** 与 Figma 设计匹配的按钮组件，集成到项目设计系统中。

### 示例 2：构建一个仪表板布局

用户说："构建这个仪表板：https://figma.com/design/pR8mNv5KqXzGwY2JtCfL4D/Dashboard?node-id=10-5"

**操作：**

1. 解析 URL 以提取 fileKey=`pR8mNv5KqXzGwY2JtCfL4D` 和 nodeId=`10-5`
2. 运行 `get_metadata(fileKey="pR8mNv5KqXzGwY2JtCfL4D", nodeId="10-5")` 以了解页面结构
3. 从元数据中识别主要部分（页眉、侧边栏、内容区域、卡片）及其子节点 ID
4. 运行 `get_design_context(fileKey="pR8mNv5KqXzGwY2JtCfL4D", nodeId=":childNodeId")` 以获取每个主要部分
5. 运行 `get_screenshot(fileKey="pR8mNv5KqXzGwY2JtCfL4D", nodeId="10-5")` 以获取整个页面
6. 下载所有资源（标志、图标、图表）
7. 使用项目的布局原语构建布局
8. 使用现有组件尽可能实现每个部分
9. 与 Figma 约束验证响应式行为

**结果：** 完整的仪表板与 Figma 设计匹配，具有响应式布局。

## 最佳实践

### 始终从上下文开始

不要基于假设实现。始终先获取 `get_design_context` 和 `get_screenshot`。

### 增量验证

在实现过程中频繁验证，而不仅仅是在最后。这可以尽早发现问题。

### 记录偏差

如果你必须偏离 Figma 设计（例如，为了无障碍性或技术约束），请在代码注释中记录原因。

### 重用胜于重新创建

在创建新组件之前始终检查现有组件。代码库的一致性比精确的 Figma 复制更重要。

### 优先考虑设计系统

不确定时，优先考虑项目的设计系统模式而不是字面 Figma 翻译。

## 常见问题和解决方案

### 问题：Figma 输出被截断

**原因：** 设计过于复杂或嵌套层过多，无法在单个响应中返回。
**解决方案：** 使用 `get_metadata` 获取节点结构，然后使用 `get_design_context` 逐个获取特定节点。

### 问题：实现后设计不匹配

**原因：** 实现的代码与原始 Figma 设计之间存在视觉差异。
**解决方案：** 与第 3 步的屏幕截图并排比较。检查设计上下文数据中的间距、颜色和字体排印值。

### 问题：资源无法加载

**原因：** Figma MCP 服务器的资源端点不可访问或 URL 被修改。
**解决方案：** 验证 Figma MCP 服务器的资源端点是否可访问。服务器在 `localhost` URL 下提供资源。直接使用这些 URL 而不要修改。

### 问题：设计令牌值与 Figma 不符

**原因：** 项目的设计系统令牌与 Figma 设计中指定的值不同。
**解决方案：** 当项目令牌与 Figma 值不同时，优先考虑项目令牌以保持一致性，但最小程度调整间距/尺寸以保持视觉保真度。

## 理解设计实现

Figma 实现工作流程建立了一个可靠的过程，用于将设计转换为代码：

**对于设计师：** 确保 实现 将与他们的设计具有像素级精确度。
**对于开发人员：** 提供一个结构化的方法，消除猜测并减少来回修改。
**对于团队：** 保持设计系统完整性的高质量实现。

通过遵循此工作流程，您可以确保每个 Figma 设计都以同样的关注度和细节水平实现。

## 额外资源

- [Figma MCP 服务器文档](https://developers.figma.com/docs/figma-mcp-server/)
- [Figma MCP 服务器工具和提示](https://developers.figma.com/docs/figma-mcp-server/tools-and-prompts/)
- [Figma 变量和设计令牌](https://help.figma.com/hc/en-us/articles/15339657135383-Guide-to-variables-in-Figma)
