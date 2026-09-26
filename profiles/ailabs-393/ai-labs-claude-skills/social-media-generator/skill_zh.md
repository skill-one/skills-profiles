# 社交媒体生成器

## 概述

该技能能够为 Twitter、Instagram、LinkedIn 和 Facebook 创建平台优化的社交媒体内容。它自动根据每个平台的最佳实践生成帖子，并将它们保存在一个有组织的目录结构中。

## 何时使用此技能

在以下情况下使用此技能：

- 请求为多个平台创建社交媒体帖子
- 为特定活动、公告或活动生成内容
- 平台特定的内容优化
- 有组织的社交媒体内容存储

## 核心工作流程

### 第 1 步：收集信息

从用户处收集以下详细信息（如未提供，请询问）：

- 活动或内容名称
- 日期和时间（格式：DD-MM-YYYY-HHMM）
- 主要信息或公告
- 目标受众
- 要包含的关键细节
- 行动号召
- 任何特定的标签或提及
- 品牌声音/语气偏好

### 第 2 步：生成平台特定内容

使用 `assets/` 中的模板为每个平台创建内容：

**Twitter** (`assets/twitter_template.md`)
- 保持 280 个字符以内
- 简洁有力
- 1-3 个相关标签
- 清晰的行动号召
- 考虑使用表情符号以提高参与度

**Instagram** (`assets/instagram_template.md`)
- 吸引人的标题，第一行包含钩子
- 更详细的描述
- 5-15 个相关标签
- 以视觉为中心的信息
- 换行以提高可读性
- 鼓励参与

**LinkedIn** (`assets/linkedin_template.md`)
- 专业和信息量大的语气
- 价值驱动的内容
- 行业见解或要点
- 3-5 个专业标签
- 项目符号形式的关键信息
- 提出讨论问题

**Facebook** (`assets/facebook_template.md`)
- 友好且吸引人
- 保持简洁（最佳参与度在 250 个字符以内）
- 2-3 个相关标签
- 以视觉为中心
- 鼓励评论和分享
- 如适用，包含活动详情

### 第 3 步：创建组织文件结构

在项目中创建以下目录结构：

```
social-media/
├── twitter/
│   └── event-name-DD-MM-YYYY-HHMM.md
├── instagram/
│   └── event-name-DD-MM-YYYY-HHMM.md
├── linkedin/
│   └── event-name-DD-MM-YYYY-HHMM.md
└── facebook/
    └── event-name-DD-MM-YYYY-HHMM.md
```

**文件名格式**：`event-name-DD-MM-YYYY-HHMM.md`
- 使用小写和连字符表示空格
- 包含日期，格式：日-月-年-时间
- 示例：`product-launch-15-03-2025-1400.md`

### 第 4 步：将内容写入文件

对于每个平台：

1. 基于模板生成平台优化的内容
2. 如果不存在，则创建平台特定的子目录
3. 将内容写入适当命名的 Markdown 文件
4. 在底部包含元数据（平台、日期、字符数）

### 第 5 步：审核和确认

生成所有帖子后：

1. 提供创建文件的摘要
2. 突出每个平台的关键点
3. 注明任何字符数警告
4. 如有必要，提供修改建议

## 内容优化指南

### 字符限制
- Twitter：280 个字符
- Instagram：2,200 个字符（但简洁更好）
- LinkedIn：3,000 个字符
- Facebook：无限（但最佳参与度在 250 个字符以内）

### 标签策略
- Twitter：1-3 个专注标签
- Instagram：5-15 个相关标签
- LinkedIn：3-5 个专业标签
- Facebook：2-3 个标签

### 语气调整
- Twitter：休闲、对话式、及时
- Instagram：以视觉为中心、吸引人、生活方式导向
- LinkedIn：专业、有见地、价值驱动
- Facebook：友好、社区导向、对话式

### 行动号召最佳实践
- 清晰具体
- 使用行动动词
- 在适当的时候制造紧迫感
- 符合平台惯例

## 示例用法

**用户请求：**
"为我们在 2025 年 3 月 15 日下午 2 点举行的产品发布活动创建社交媒体帖子。产品是一款名为 TaskFlow 的 AI 驱动的生产力工具。"

**执行：**
1. 收集额外细节（关键功能、目标受众、网站链接）
2. 生成四个平台特定的帖子
3. 创建目录结构：`social-media/twitter/`、`social-media/instagram/` 等
4. 写入文件：在每个平台文件夹中写入 `taskflow-launch-15-03-2025-1400.md`
5. 提供摘要，包括文件位置和关键点

## 资产

此技能包括 `assets/` 目录中的模板文件：
- `twitter_template.md` - Twitter 帖子结构和最佳实践
- `instagram_template.md` - Instagram 标题格式和指南
- `linkedin_template.md` - LinkedIn 帖子结构和专业语气指南
- `facebook_template.md` - Facebook 帖子格式和参与度技巧

这些模板作为参考，用于生成内容时的平台特定要求和最佳实践。
