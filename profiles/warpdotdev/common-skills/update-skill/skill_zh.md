# update-skill

本指南提供了创建或更新此存储库中技能的说明。它涵盖了技能所需的结构、frontmatter 以及最佳实践。

## 快速入门

每个技能都是一个包含 YAML frontmatter 和 markdown 体的 `SKILL.md` 文件的目录：

```markdown
---
name: pdf-processing
description: 从 PDF 文件中提取文本和表格，填写表单，合并文档。
---

# PDF 处理

## 何时使用此技能
当用户需要处理 PDF 文件时使用此技能...

## 如何提取文本
1. 使用 pdfplumber 进行文本提取...

## 如何填写表单
...
```

## 要求

### Frontmatter（必填）

每个 SKILL.md 必须以包含以下内容的 YAML frontmatter 开头：

- **name**：蛇形命名标识符（仅限小写字母、数字和连字符）
  - 示例：`add-feature-flag`，`pdf-processing`，`update-skill`
- **description**：技能的具体描述及其用途
  - 必须非空
  - 应包含用于技能发现的关键术语
  - 以动词开头，明确说明技能实现的功能（例如，“添加功能标志”而不是“帮助功能标志”），并立即跟随具体用例或上下文（例如，“在处理功能标志时使用”）
  - 使用第三人称（例如，“添加功能标志”而不是“我可以帮助你添加”）

### 编写有效的描述

描述字段对于技能发现至关重要。应包含技能的**功能**和**用途**。一些好的示例：

- `git-commit`： "通过分析 git 差异生成描述性提交消息。当用户需要帮助编写提交消息或审查暂存更改时使用。"
- `pdf-processing`： "从 PDF 文件中提取文本和表格，填写表单，合并文档。在处理 PDF 文件或用户提到 PDF、表单或文档提取时使用。"

避免模糊的描述，如“帮助代码”或“执行开发任务”。更多上下文，请参阅 [references/best-practices.md](references/best-practices.md) 中的“描述最佳实践”。

### 技能结构

Warp 技能的典型部分：

1. **标题和简要概述** – 清晰的标题和技能用途的简洁概述。如果有用，链接到部分、参考文件或相关技能
2. **概述** - 关于技能用途的上下文（可选但常见），扩展概述以提供更多细节和上下文
3. **主要内容** - 步骤、使用说明或工作流指导
4. **最佳实践** - 指南和建议（可选）
5. **示例 / 参考 PRs** - 链接到实际示例（可选）

根据技能的需求保持结构灵活。简单的技能可以省略可选部分。

### 验证

可选地，使用 [skills-ref](https://github.com/agentskills/agentskills/tree/main/skills-ref) 参考库验证您的技能：

```bash
skills-ref validate ./my-skill
```

这将检查您的 SKILL.md frontmatter 是否有效并遵循所有命名约定。如果未安装，使用 WebSearch 工具获取此包的上下文。

### 主要内容最佳实践

- 关于什么可以算作好的主要内容，请参阅 [references/best-practices.md](references/best-practices.md) 中的“简洁性原则”
- 当格式化代码示例时，请参阅 [references/best-practices.md](references/best-practices.md) 中的“代码示例格式”。

### 文件组织

- **简单技能**（<=200 行）：将所有内容保留在 SKILL.md 中
- **复杂技能** (>200 行)：将详细内容拆分为 `references/` 子目录
  - 从 SKILL.md 引用文件，并使用清晰链接
  - 示例："参见 [references/best-practices.md](references/best-practices.md) 获取详细指导"

## 何时拆分内容

当以下情况出现时，创建 `references/` 子目录：

- SKILL.md 接近 200+ 行
- 技能涵盖多个域或可独立加载的工作流
- 详细的参考材料会弄乱主指令

仅将基本工作流和程序性说明保留在 SKILL.md 中。将详细的参考材料、模式定义和大量示例移动到 `references/` 文件中。

## 现有技能的示例

关于结构和风格的参考：

- `.agents/skills/add-feature-flag/SKILL.md` - 具有清晰顺序步骤的多步骤工作流
- `.agents/skills/remove-feature-flag/SKILL.md` - 清理工作流，包含搜索命令

## 最佳实践

有关详细编写指导，包括：

- 逐步披露模式
- 编写简洁有效的说明
- 代码示例格式
- 避免常见的反模式

请参阅 [references/best-practices.md](references/best-practices.md)。
