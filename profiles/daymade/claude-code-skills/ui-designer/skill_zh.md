# UI 设计师

## 概述

该技能通过多步骤工作流程，从参考 UI 图像中系统性地提取设计系统：分析视觉模式 → 生成设计系统文档 → 创建产品需求文档（PRD）→ 生成可落地的 UI 提示。

## 使用场景

- 用户提供 UI 截图、原型或设计参考
- 需要从现有设计中提取调色板、排版、间距
- 希望从视觉示例中生成设计系统文档
- 构建 MVP UI 且需匹配参考美学
- 创建遵循一致设计原则的多个 UI 变体

## 工作流程

### 第 1 步：收集输入

向用户请求：
- **参考图像目录**：包含 UI 截图/原型的文件夹路径
- **项目构思文件**：描述产品概念和目标的文档
- **现有 PRD**（可选）：如果已存在 PRD，可跳过第 3 步

### 第 2 步：从图像中提取设计系统

使用通用子代理的 **Task 工具**，提供：

**来自 `assets/design-system.md` 的提示模板**：
- 分析调色板（主色、辅色、强调色、功能色）
- 提取排版（字体家族、尺寸、粗细、行高）
- 识别组件样式（按钮、卡片、输入框、图标）
- 记录间距系统
- 注明动画/过渡模式
- 如存在，包含暗黑模式变体

**将参考图像附加到子代理上下文**。

**输出**：符合模板格式的完整设计系统 Markdown

**保存至**：`documents/designs/{image_dir_name}_design_system.md`

### 第 3 步：生成 MVP PRD（如未提供）

使用通用子代理的 **Task 工具**，提供：

**来自 `assets/app-overview-generator.md` 的提示模板**：
- 将 `{项目背景}` 替换为项目构思文件内容
- 模板引导：电梯演讲、问题陈述、目标受众、独特销售主张、功能列表、UX/UI 考量

**与用户交互**，完善和澄清产品需求

**输出**：结构化 PRD Markdown

**保存为变量**供第 4 步使用（可选保存至 `documents/prd/`）

### 第 4 步：组合最终 UI 实现提示

使用 `assets/vibe-design-template.md` 结合设计系统和 PRD：

**替换项**：
- `{项目设计指南}` → 第 2 步的设计系统
- `{项目MVP PRD}` → 第 3 步的 PRD 或提供的 PRD 文件

**结果**：包含以下内容的完整、可落地的提示：
- 设计美学原则
- 项目特定调色板/排版指南
- 应用概述和功能需求
- 实现任务（多个 UI 变体、组件结构）

**保存至**：`documents/ux-design/{idea_file_name}_design_prompt_{timestamp}.md`

### 第 5 步：验证 React 环境

检查现有 React 项目：
```bash
find . -name "package.json" -exec grep -l "react" {} \;
```

如未找到，通知用户：
```bash
npx create-react-app my-app
cd my-app
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p
npm install lucide-react
```

### 第 6 步：实现 UI

使用第 4 步组合的最终提示，在 React 项目中实现 UI。

提示指示：
- 创建多个设计变体（移动端 3 个，Web 端 2 个）
- 按组件组织：`[solution-name]/pages/[page-name].jsx`
- 将所有变体聚合在展示页面

## 模板资源

### assets/design-system.md

提取视觉设计模式的模板。包含以下部分：
- 调色板（主色、辅色、强调色、功能色、背景色）
- 排版（字体家族、粗细、文本样式）
- 组件样式（按钮、卡片、输入框、图标）
- 间距系统（4dp-48dp 尺寸）
- 动画（持续时间、缓动曲线）
- 暗黑模式变体

在分析参考图像时使用此模板，确保设计系统覆盖全面。

### assets/app-overview-generator.md

协作式 PRD 生成模板。引导：
- 电梯演讲
- 问题陈述和目标受众
- 独特销售主张
- 平台目标
- 带用户故事的特性列表
- 每屏的 UX/UI 考量

设计用于与用户交互，澄清需求。

### assets/vibe-design-template.md

结合设计系统和 PRD 的最终实现提示模板。包含：
- 美学原则（极简主义、留白、色彩理论、排版层级）
- 实际需求（Tailwind CSS、Lucide 图标、响应式设计）
- 任务规范（多个变体、组件组织）

此模板生成无需进一步修改即可用于 UI 实现的提示。

## 最佳实践

### 图像分析

- 开始分析前阅读所有图像
- 跨多屏寻找模式
- 记录显式样式（颜色、字体）和隐式原则（间距、层级）
- 如参考中存在，捕获暗黑模式

### 设计系统提取

- 系统化处理：覆盖所有模板部分
- 使用具体值（十六进制代码、px 尺寸）而非通用描述
- 当可推断时，记录设计选择的“原因”
- 包含变体（悬停状态、禁用状态）

### PRD 生成

- 交互式与用户协作，澄清模糊点
- 基于问题理解建议特性
- 确保 MVP 范围现实
- 按屏/交互记录 UX 考量

### 输出组织

- 使用描述性文件名保存设计系统（基于图像目录名）
- 使用时间戳保存最终提示以追踪版本
- 将所有输出保存在 `documents/` 目录便于参考
- 保留中间输出以供迭代

## 示例使用

**用户提供**：
- `reference-images/saas-dashboard/`（5 张截图）
- `ideas/project-management-app.md`（项目构思）

**执行工作流**：

1. 从 `reference-images/saas-dashboard/` 读取 5 张图像
2. 使用 Task 工具 → design-system.md 模板 → 分析图像
3. 保存至 `documents/designs/saas-dashboard_design_system.md`
4. 使用 Task 工具 → app-overview-generator.md 与项目构思
5. 通过用户交互完善 PRD
6. 使用 vibe-design-template.md 结合设计系统 + PRD
7. 保存至 `documents/ux-design/project-management-app_design_prompt_20251025_153000.md`
8. 检查 React 环境，如需设置则通知用户
9. 使用最终提示实现 UI

## 注意事项

- 这是一个 **高自由度** 的工作流——根据上下文调整步骤
- 模板提供结构，但鼓励深入分析而非机械填充
- PRD 生成过程中的用户交互对质量至关重要
- 最终提示质量直接影响 UI 实现成功
- 保留所有中间输出以供迭代和优化
