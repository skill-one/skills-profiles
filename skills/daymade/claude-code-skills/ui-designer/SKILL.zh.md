---
name: ui-designer
description: 从参考UI图像中提取设计系统，并生成可用于实现的UI设计提示。当用户提供UI截图/模型，并希望创建一致的设计、生成设计系统或构建符合参考美学的MVP UI时使用。
---

# UI设计师

## 概述

该技能通过多步骤工作流程，从参考UI图像中系统性地提取设计系统：分析视觉模式 → 生成设计系统文档 → 创建PRD → 产出可实现的UI提示。

## 使用场景

- 用户提供UI截图、原型或设计参考
- 需要从现有设计中提取调色板、排版、间距
- 希望从视觉示例中生成设计系统文档
- 构建应与参考美学匹配的MVP UI
- 根据一致的设计原则创建多个UI变体

## 工作流程

### 第1步：收集输入

向用户请求：
- **参考图像目录**：包含UI截图/原型的文件夹路径
- **项目构思文件**：描述产品概念和目标的文档
- **现有PRD**（可选）：如果PRD已存在，则跳过第3步

### 第2步：从图像中提取设计系统

使用通用子代理的**任务工具**，提供：

**来自`assets/design-system.md`的提示模板**：
- 分析调色板（主色、辅色、强调色、功能色）
- 提取排版（字体家族、大小、粗细、行高）
- 识别组件样式（按钮、卡片、输入框、图标）
- 记录间距系统
- 注明动画/过渡模式
- 如存在，包含暗黑模式变体

**将参考图像附加到子代理上下文中**。

**输出**：遵循模板格式的完整设计系统Markdown文档

**保存至**：`documents/designs/{image_dir_name}_design_system.md`

### 第3步：生成MVP PRD（如未提供）

使用通用子代理的**任务工具**，提供：

**来自`assets/app-overview-generator.md`的提示模板**：
- 将`{项目背景}`替换为项目构思文件内容
- 模板引导：电梯演讲、问题陈述、目标受众、独特销售主张、功能列表、UX/UI考虑

**与用户交互**以完善和澄清产品需求

**输出**：结构化的PRD Markdown文档

**保存为变量**供第4步使用（可选保存至`documents/prd/`）

### 第4步：组合最终UI实现提示

使用`assets/vibe-design-template.md`组合设计系统和PRD：

**替换项**：
- `{项目设计指南}` → 第2步的设计系统
- `{项目MVP PRD}` → 第3步的PRD或提供的PRD文件

**结果**：包含以下内容的完整、可实现的提示：
- 设计美学原则
- 项目特定的颜色/排版指南
- 应用概述和功能需求
- 实现任务（多个UI变体、组件结构）

**保存至**：`documents/ux-design/{idea_file_name}_design_prompt_{timestamp}.md`

### 第5步：验证React环境

检查现有React项目：
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

### 第6步：实现UI

使用第4步组合的最终提示在React项目中实现UI。

提示指示：
- 创建多个设计变体（移动端3个，Web端2个）
- 按组件组织：`[solution-name]/pages/[page-name].jsx`
- 在展示页面中聚合所有变体

## 模板资源

### assets/design-system.md

提取视觉设计模式的模板。包含以下部分：
- 调色板（主色、辅色、强调色、功能色、背景色）
- 排版（字体家族、粗细、文本样式）
- 组件样式（按钮、卡片、输入框、图标）
- 间距系统（4dp-48dp范围）
- 动画（持续时间、缓动曲线）
- 暗黑模式变体

在分析参考图像时使用此模板，以确保全面的设计系统覆盖。

### assets/app-overview-generator.md

协作式PRD生成的模板。引导：
- 电梯演讲
- 问题陈述和目标受众
- 独特销售主张
- 平台目标
- 带用户故事的功能列表
- 每个屏幕的UX/UI考虑

设计用于与用户交互以澄清需求。

### assets/vibe-design-template.md

组合设计系统和PRD的最终实现提示模板。包含：
- 美学原则（极简主义、留白、色彩理论、排版层级）
- 实际要求（Tailwind CSS、Lucide图标、响应式设计）
- 任务规范（多个变体、组件组织）

此模板生成准备好用于UI实现的提示，无需进一步修改。

## 最佳实践

### 图像分析

- 开始分析前阅读所有图像
- 跨多个屏幕寻找模式
- 记录显式样式（颜色、字体）和隐式原则（间距、层级）
- 如参考中存在，捕获暗黑模式

### 设计系统提取

- 系统化处理：覆盖所有模板部分
- 使用具体值（十六进制代码、px大小），而非通用描述
- 当可推断时，记录设计选择的“原因”
- 包含变体（悬停状态、禁用状态）

### PRD生成

- 交互式地与用户协作以澄清歧义
- 基于问题理解建议功能
- 确保MVP范围现实
- 按屏幕/交互记录UX考虑

### 输出组织

- 使用描述性文件名保存设计系统（基于图像目录名）
- 使用时间戳保存最终提示以进行版本跟踪
- 将所有输出保存在`documents/`目录以便参考
- 保留中间输出以供迭代

## 示例使用

**用户提供：**
- `reference-images/saas-dashboard/`（5张截图）
- `ideas/project-management-app.md`（项目构思）

**执行工作流程：**

1. 从`reference-images/saas-dashboard/`读取5张图像
2. 使用任务工具 → design-system.md模板 → 分析图像
3. 保存至`documents/designs/saas-dashboard_design_system.md`
4. 使用任务工具 → app-overview-generator.md与项目构思
5. 通过用户交互完善PRD
6. 使用vibe-design-template.md组合设计系统+PRD
7. 保存至`documents/ux-design/project-management-app_design_prompt_20251025_153000.md`
8. 检查React环境，如需设置则通知用户
9. 使用最终提示实现UI

## 注意事项

- 这是一个**高度自由**的工作流程——根据上下文调整步骤
- 模板提供结构，但鼓励深思熟虑的分析而非机械填充
- PRD生成过程中的用户交互对质量至关重要
- 最终提示质量直接影响UI实现的成功
- 保留所有中间输出以供迭代和优化
